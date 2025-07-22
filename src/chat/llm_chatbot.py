"""
LLM Chatbot for RepairGPT
Implements Issue #9: 基本的なLLMチャットボットの実装
"""

import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional

try:
    from ..utils.logger import (
        LoggerMixin,
        get_logger,
        log_api_call,
        log_api_error,
        log_performance,
    )
except ImportError:
    # Fallback for direct execution - add parent directory to path
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from utils.logger import (
        LoggerMixin,
        get_logger,
        log_api_call,
        log_api_error,
        log_performance,
    )

try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    anthropic = None
    Anthropic = None

try:
    pass

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Try to import requests for Hugging Face API
try:
    import requests

    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

# Get logger instance
logger = get_logger(__name__)


@dataclass
class Message:
    """Chat message structure"""

    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: str = None
    metadata: Dict = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RepairContext:
    """Context information for repair session"""

    device_type: Optional[str] = None
    device_model: Optional[str] = None
    issue_description: Optional[str] = None
    user_skill_level: Optional[str] = None
    safety_concerns: List[str] = None
    available_tools: List[str] = None

    def __post_init__(self):
        if self.safety_concerns is None:
            self.safety_concerns = []
        if self.available_tools is None:
            self.available_tools = []

    def dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class RepairChatbot(LoggerMixin):
    """Advanced LLM chatbot for repair assistance"""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        huggingface_api_key: Optional[str] = None,
        preferred_model: str = "auto",
        use_mock: bool = False,
    ):
        """
        Initialize the repair chatbot

        Args:
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
            huggingface_api_key: Hugging Face API key (optional)
            preferred_model: "openai", "anthropic", "huggingface", or "auto"
            use_mock: Use mock responses instead of real API calls
        """
        self.log_info("Initializing RepairChatbot", preferred_model=preferred_model, use_mock=use_mock)

        self.openai_client = None
        self.anthropic_client = None
        self.huggingface_api_key = huggingface_api_key or os.getenv("HUGGINGFACE_API_KEY")
        self.preferred_model = preferred_model
        self.use_mock = use_mock

        # Initialize OpenAI client
        if openai and (openai_api_key or os.getenv("OPENAI_API_KEY")):
            try:
                self.openai_client = openai.OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"))
                self.log_info("OpenAI client initialized successfully")
            except Exception as e:
                self.log_error(e, "Failed to initialize OpenAI client")

        # Initialize Anthropic client
        if anthropic and (anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")):
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"))
                self.log_info("Anthropic client initialized successfully")
            except Exception as e:
                self.log_error(e, "Failed to initialize Anthropic client")

        # Set working client based on availability
        if use_mock:
            self.log_info("Using mock mode for AI responses")
            self.active_client = "mock"
        elif preferred_model == "anthropic" and self.anthropic_client:
            self.active_client = "anthropic"
        elif preferred_model == "openai" and self.openai_client:
            self.active_client = "openai"
        elif preferred_model == "huggingface" and HF_AVAILABLE:
            self.active_client = "huggingface"
        elif self.openai_client:
            self.active_client = "openai"
        elif self.anthropic_client:
            self.active_client = "anthropic"
        elif HF_AVAILABLE:
            self.active_client = "huggingface"
        else:
            self.log_warning("No LLM clients available - using enhanced fallback mode")
            self.active_client = "enhanced_fallback"

        # Initialize conversation state
        self.conversation_history: List[Message] = []
        self.repair_context = RepairContext()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.log_info(
            "RepairChatbot initialization completed",
            active_client=self.active_client,
            session_id=self.session_id,
        )

    @property
    def context(self) -> RepairContext:
        """Get the current repair context"""
        return self.repair_context

    def _init_openai_client(self, api_key: Optional[str] = None):
        """Initialize OpenAI client"""
        try:
            if not openai:
                raise ImportError("OpenAI package not available")
            self.openai_client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.log_info("OpenAI client initialized successfully")
        except Exception as e:
            self.log_error(e, "Failed to initialize OpenAI client")

    def _init_anthropic_client(self, api_key: Optional[str] = None):
        """Initialize Anthropic client"""
        try:
            if not anthropic:
                raise ImportError("Anthropic package not available")
            self.anthropic_client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            self.log_info("Anthropic client initialized successfully")
        except Exception as e:
            self.log_error(e, "Failed to initialize Anthropic client")

    def update_context(self, **kwargs):
        """Update repair context with new information"""
        updated_fields = {}
        for key, value in kwargs.items():
            if hasattr(self.repair_context, key):
                setattr(self.repair_context, key, value)
                updated_fields[key] = value

        if updated_fields:
            self.log_info("Updated repair context", **updated_fields)

    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to conversation history"""
        message = Message(role=role, content=content, metadata=metadata or {})
        self.conversation_history.append(message)

        # Log message addition with appropriate detail level
        content_preview = content[:100] + "..." if len(content) > 100 else content
        self.logger.debug(
            f"Added {role} message",
            extra={
                "extra_data": {
                    "role": role,
                    "content_length": len(content),
                    "content_preview": content_preview,
                    "session_id": self.session_id,
                }
            },
        )

    def chat(self, user_message: str, include_context: bool = True) -> str:
        """
        Generate response for user message

        Args:
            user_message: User's repair question or description
            include_context: Whether to include repair context in prompt

        Returns:
            Chatbot response
        """
        start_time = time.time()

        # Log chat request
        self.log_info(
            "Processing chat request",
            message_length=len(user_message),
            include_context=include_context,
            active_client=self.active_client,
        )

        # Add user message to history
        self.add_message("user", user_message)

        try:
            if self.active_client == "mock":
                response = self._mock_response(user_message, include_context)
            elif self.active_client == "openai":
                response = self._chat_with_openai(user_message, include_context)
            elif self.active_client == "anthropic":
                response = self._chat_with_anthropic(user_message, include_context)
            elif self.active_client == "huggingface":
                response = self._chat_with_huggingface(user_message, include_context)
            elif self.active_client == "enhanced_fallback":
                response = self._enhanced_fallback_response(user_message)
            else:
                response = self._fallback_response(user_message)

            # Add response to history
            self.add_message("assistant", response)

            # Log successful completion
            duration = time.time() - start_time
            log_performance(
                self.logger,
                "chat_completion",
                duration,
                client=self.active_client,
                response_length=len(response),
            )

            return response

        except Exception as e:
            # Log the error with context
            duration = time.time() - start_time
            self.log_error(
                e,
                "chat_request_failed",
                client=self.active_client,
                message_length=len(user_message),
                duration=duration,
            )

            # Return enhanced fallback response
            fallback_response = self._enhanced_fallback_response(user_message)
            self.add_message("assistant", fallback_response)
            return fallback_response

    def _chat_with_openai(self, user_message: str, include_context: bool) -> str:
        """Generate response using OpenAI"""
        if not self.openai_client:
            raise Exception("OpenAI client not available")

        # Log API call
        log_api_call(
            self.logger,
            "openai_chat_completion",
            "POST",
            model="gpt-4",
            include_context=include_context,
        )

        try:
            messages = self._build_messages(user_message, include_context)

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=800,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            result = response.choices[0].message.content.strip()

            # Log successful API response
            self.log_info(
                "OpenAI API call successful",
                tokens_used=(response.usage.total_tokens if hasattr(response, "usage") else None),
                response_length=len(result),
            )

            return result

        except Exception as e:
            # Log API error with details
            log_api_error(
                self.logger,
                "openai_chat_completion",
                e,
                model="gpt-4",
                message_count=len(messages) if "messages" in locals() else 0,
            )
            raise

    def _chat_with_anthropic(self, user_message: str, include_context: bool) -> str:
        """Generate response using Anthropic Claude"""
        if not self.anthropic_client:
            raise Exception("Anthropic client not available")

        # Log API call
        log_api_call(
            self.logger,
            "anthropic_messages",
            "POST",
            model="claude-3-sonnet-20240229",
            include_context=include_context,
        )

        try:
            system_prompt = self._build_system_prompt(include_context)
            conversation = self._build_conversation_for_anthropic()

            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=800,
                temperature=0.7,
                system=system_prompt,
                messages=conversation + [{"role": "user", "content": user_message}],
            )

            result = response.content[0].text.strip()

            # Log successful API response
            self.log_info(
                "Anthropic API call successful",
                input_tokens=(response.usage.input_tokens if hasattr(response, "usage") else None),
                output_tokens=(response.usage.output_tokens if hasattr(response, "usage") else None),
                response_length=len(result),
            )

            return result

        except Exception as e:
            # Log API error with details
            log_api_error(self.logger, "anthropic_messages", e, model="claude-3-sonnet-20240229")
            raise

    def _chat_with_huggingface(self, user_message: str, include_context: bool) -> str:
        """Generate response using Hugging Face Inference API"""
        if not HF_AVAILABLE:
            raise Exception("Requests library not available for Hugging Face API")

        # Free models available on Hugging Face
        models = [
            "microsoft/DialoGPT-medium",
            "facebook/blenderbot-400M-distill",
            "google/flan-t5-base",
        ]

        system_prompt = self._build_system_prompt(include_context)
        prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"

        for model in models:
            try:
                headers = {}
                if self.huggingface_api_key:
                    headers["Authorization"] = f"Bearer {self.huggingface_api_key}"

                api_url = f"https://api-inference.huggingface.co/models/{model}"
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 500,
                        "temperature": 0.7,
                        "do_sample": True,
                    },
                }

                response = requests.post(api_url, headers=headers, json=payload, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get("generated_text", "")
                        # Extract only the assistant's response
                        if "Assistant:" in generated_text:
                            return generated_text.split("Assistant:")[-1].strip()
                        return generated_text.strip()

                self.log_warning(
                    f"HF model {model} failed",
                    status_code=response.status_code,
                    model=model,
                )

            except Exception as e:
                self.log_warning(f"HF model {model} failed", error=str(e), model=model)
                continue

        # If all HF models fail, use enhanced fallback
        return self._enhanced_fallback_response(user_message)

    def _build_messages(self, user_message: str, include_context: bool) -> List[Dict]:
        """Build message list for OpenAI API"""
        messages = []

        # System prompt
        system_prompt = self._build_system_prompt(include_context)
        messages.append({"role": "system", "content": system_prompt})

        # Recent conversation history (last 10 messages)
        recent_history = self.conversation_history[-10:]
        for msg in recent_history:
            messages.append({"role": msg.role, "content": msg.content})

        # Current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _build_conversation_for_anthropic(self) -> List[Dict]:
        """Build conversation for Anthropic API (no system messages)"""
        conversation = []
        recent_history = self.conversation_history[-10:]

        for msg in recent_history:
            if msg.role != "system":  # Anthropic handles system separately
                conversation.append({"role": msg.role, "content": msg.content})

        return conversation

    def _build_system_prompt(self, include_context: bool) -> str:
        """Build system prompt with repair context"""
        base_prompt = (
            "You are an expert electronics repair assistant. You provide clear, safe, and "
            "practical repair guidance for consumer electronics including gaming consoles, "
            "smartphones, laptops, and other devices.\n\n"
            "Key principles:\n"
            "1. SAFETY FIRST - Always prioritize user safety and warn about potential hazards\n"
            "2. Clear instructions - Provide step-by-step guidance appropriate for the user's skill level\n"
            "3. Tool requirements - Specify exactly what tools and parts are needed\n"
            "4. Troubleshooting - Help diagnose issues before suggesting repairs\n"
            "5. Alternatives - Suggest when professional repair might be better\n\n"
            "Guidelines:\n"
            "- Ask clarifying questions when the problem description is unclear\n"
            "- Provide estimated difficulty and time requirements\n"
            "- Warn about warranty implications\n"
            "- Suggest testing steps to verify the fix worked\n"
            "- Be honest about repair complexity and success likelihood"
        )

        if include_context and (self.repair_context.device_type or self.repair_context.issue_description):
            available_tools_str = (
                ", ".join(self.repair_context.available_tools)
                if self.repair_context.available_tools
                else "Not specified"
            )
            safety_concerns_str = (
                ", ".join(self.repair_context.safety_concerns) if self.repair_context.safety_concerns else "None noted"
            )
            context_info = (
                f"\n\nCurrent repair context:\n"
                f"- Device: {self.repair_context.device_type} {self.repair_context.device_model}\n"
                f"- Issue: {self.repair_context.issue_description}\n"
                f"- User skill level: {self.repair_context.user_skill_level}\n"
                f"- Available tools: {available_tools_str}\n"
                f"- Safety concerns: {safety_concerns_str}"
            )

            base_prompt += context_info

        return base_prompt

    def _fallback_response(self, user_message: str) -> str:
        """Provide fallback response when no LLM is available"""
        return f"""I'm currently unable to connect to AI services, but I can provide some general guidance:

For device repair questions like yours:

1. **Safety First**: Always power off the device and disconnect from power sources
2. **Gather Information**:
   - What specific symptoms are you experiencing?
   - When did the problem start?
   - Any recent drops, spills, or other incidents?

3. **Basic Troubleshooting**:
   - Try a simple restart/power cycle
   - Check all connections and cables
   - Look for obvious physical damage

4. **Research**: Check the device manufacturer's support documentation
5. **Consider Professional Help**: For complex issues or if you're uncomfortable with the repair

Please try again later when AI services are available for more detailed assistance.

Your message: "{user_message[:100]}{'...' if len(user_message) > 100 else ''}"
"""

    def _mock_response(self, user_message: str, include_context: bool) -> str:
        """Generate mock AI response for testing without API keys"""
        self.log_info("Generating mock response", include_context=include_context)

        # Simulate processing time
        time.sleep(0.5)

        user_lower = user_message.lower()

        # Prepare context information
        context_info = ""
        if include_context and self.repair_context.device_type:
            context_info = "\n\n**Current Context:**\n"
            if self.repair_context.device_type:
                context_info += f"- Device: {self.repair_context.device_type}\n"
            if self.repair_context.device_model:
                context_info += f"- Model: {self.repair_context.device_model}\n"
            if self.repair_context.issue_description:
                context_info += f"- Issue: {self.repair_context.issue_description}\n"
            if self.repair_context.user_skill_level:
                context_info += f"- Skill Level: {self.repair_context.user_skill_level}\n"

        # Mock responses based on keywords
        if "joy-con" in user_lower or "drift" in user_lower:
            return f"""🤖 **Mock AI Response** (API keys not configured)

I understand you're experiencing Joy-Con drift issues. This is a common problem with Nintendo Switch controllers.

**Common Solutions:**
1. **Recalibration**: Go to System Settings > Controllers and Sensors > Calibrate Control Sticks
2. **Cleaning**: Use compressed air around the analog stick base
3. **Contact Cleaner**: Apply electrical contact cleaner under the rubber cap (advanced users)
4. **Replacement**: The analog stick mechanism can be replaced with proper tools

**Tools Needed:**
- Compressed air
- Electrical contact cleaner (optional)
- Y00 Tripoint screwdriver (for replacement)
- Plastic prying tools

⚠️ **Safety Note**: Always power off your device before attempting repairs.{context_info}

*This is a mock response for testing. Configure API keys for real AI assistance.*"""

        elif "screen" in user_lower and ("iphone" in user_lower or "cracked" in user_lower):
            return f"""🤖 **Mock AI Response** (API keys not configured)

I see you're dealing with an iPhone screen issue. Screen repairs require careful handling.

**Assessment Steps:**
1. Check if the touch functionality still works
2. Look for LCD damage (black spots, lines, or bleeding)
3. Test the home button/Face ID functionality
4. Check for frame damage

**Repair Options:**
1. **Professional Repair**: Apple Store or authorized service provider
2. **Third-party Repair**: Local repair shops (may void warranty)
3. **DIY Repair**: Requires experience and proper tools

**DIY Tools Required:**
- Pentalobe screwdrivers
- Plastic picks and prying tools
- Suction cups
- New screen assembly
- Waterproof adhesive

⚠️ **Warning**: iPhone repairs can be complex and may damage Face ID or water resistance.{context_info}

*This is a mock response for testing. Configure API keys for real AI assistance.*"""

        elif "battery" in user_lower:
            return f"""🤖 **Mock AI Response** (API keys not configured)

Battery issues are common in electronic devices. Let me help you diagnose the problem.

**Common Battery Problems:**
1. **Rapid Drain**: Apps running in background, old battery
2. **Not Charging**: Faulty cable, port damage, or battery failure
3. **Swelling**: Dangerous - stop using immediately
4. **Overheating**: May indicate battery or charging circuit issues

**Diagnostic Steps:**
1. Check battery health in device settings
2. Test with different charging cables and adapters
3. Clean charging port with compressed air
4. Monitor battery temperature during use

**Safety First:**
- Never puncture a battery
- Replace swollen batteries immediately
- Use only certified replacement batteries
- Dispose of old batteries properly{context_info}

*This is a mock response for testing. Configure API keys for real AI assistance.*"""

        else:
            # Generic repair response
            return f"""🤖 **Mock AI Response** (API keys not configured)

I'm here to help with your repair question. Based on your message: "{user_message}"

**General Repair Guidelines:**
1. **Safety First**: Always power off devices before repair
2. **Right Tools**: Use proper tools to avoid damage
3. **Documentation**: Take photos before disassembly
4. **Patience**: Don't force components

**Common Steps:**
1. Identify the specific issue
2. Research repair guides (iFixit is great)
3. Gather necessary tools and parts
4. Work in a clean, well-lit area
5. Follow guides step-by-step

**When to Seek Help:**
- If you're unsure about any step
- For complex motherboard repairs
- When special equipment is needed
- If device is under warranty{context_info}

💡 **Tip**: Provide more specific details about your device and issue for better assistance.

*This is a mock response for testing. Configure API keys for real AI assistance.*"""

    def _enhanced_fallback_response(self, user_message: str) -> str:
        """Provide enhanced fallback response with repair knowledge database"""

        # Common repair knowledge database
        repair_knowledge = {
            "joy-con": {
                "drift": {
                    "symptoms": [
                        "analog stick moves without input",
                        "character moves randomly",
                        "cursor drifts",
                    ],
                    "causes": [
                        "worn analog stick mechanisms",
                        "dust/debris buildup",
                        "electrical contact issues",
                    ],
                    "solutions": [
                        (
                            "1. **Immediate Fix**: Recalibrate the Joy-Con in System Settings > "
                            "Controllers and Sensors > Calibrate Control Sticks"
                        ),
                        "2. **Cleaning**: Use compressed air around the analog stick base to remove debris",
                        "3. **Contact Cleaner**: Apply electrical contact cleaner under the rubber cap (advanced)",
                        "4. **Replacement**: Replace the analog stick mechanism (requires disassembly)",
                        "5. **Professional Repair**: Nintendo repair service or local repair shop",
                    ],
                    "difficulty": "Easy to Hard (depending on method)",
                    "tools": [
                        "Compressed air",
                        "Contact cleaner (optional)",
                        "Y00 Tripoint screwdriver (for replacement)",
                        "Plastic prying tools",
                    ],
                    "cost": "$5-30 (DIY) or $40-80 (professional)",
                    "success_rate": "Calibration: 20%, Cleaning: 50%, Contact cleaner: 70%, Replacement: 95%",
                }
            },
            "iphone": {
                "screen": {
                    "symptoms": [
                        "cracked display",
                        "black screen",
                        "touch not responding",
                        "lines on screen",
                    ],
                    "causes": [
                        "impact damage",
                        "pressure damage",
                        "liquid damage",
                        "connector issues",
                    ],
                    "solutions": [
                        "1. **Assessment**: Check if it's just the glass or the full LCD/OLED assembly",
                        "2. **Backup Data**: Immediately backup if touch still works",
                        "3. **Professional Assessment**: Complex repair requiring special tools",
                        "4. **DIY Options**: Only for experienced repairers with proper tools",
                        "5. **Insurance/Warranty**: Check AppleCare+ or device insurance coverage",
                    ],
                    "difficulty": "Very Hard",
                    "tools": [
                        "Pentalobe screwdrivers",
                        "Suction cups",
                        "Heat gun/pads",
                        "Spudgers",
                        "Screen assembly",
                    ],
                    "cost": "$50-300 (DIY) or $100-400 (professional)",
                    "success_rate": "DIY: 60% (high risk), Professional: 95%",
                }
            },
            "laptop": {
                "boot": {
                    "symptoms": [
                        "won't turn on",
                        "no display",
                        "fan spins but no boot",
                        "blue screen",
                    ],
                    "causes": [
                        "power supply issues",
                        "battery problems",
                        "RAM issues",
                        "hard drive failure",
                        "motherboard problems",
                    ],
                    "solutions": [
                        "1. **Power Check**: Try different power adapter, remove battery and use wall power only",
                        "2. **Hard Reset**: Hold power button for 30 seconds while unplugged",
                        "3. **RAM Test**: Remove and reseat RAM modules, test one stick at a time",
                        "4. **Display Test**: Connect external monitor to check if issue is screen or motherboard",
                        "5. **Boot Diagnostics**: Access BIOS/UEFI settings to run hardware diagnostics",
                    ],
                    "difficulty": "Easy to Hard",
                    "tools": [
                        "Screwdrivers",
                        "Anti-static wrist strap",
                        "External monitor",
                        "Replacement RAM (for testing)",
                    ],
                    "cost": "$0-200 (depending on failed component)",
                    "success_rate": "Power issues: 80%, RAM issues: 90%, Hard drive: 85%, Motherboard: 30%",
                }
            },
        }

        # Analyze user message for keywords
        message_lower = user_message.lower()
        device_context = self.repair_context.device_type.lower() if self.repair_context.device_type else ""
        issue_context = self.repair_context.issue_description.lower() if self.repair_context.issue_description else ""

        # Combined context for analysis
        full_context = f"{message_lower} {device_context} {issue_context}"

        # Match repair knowledge
        matched_advice = None
        for device, issues in repair_knowledge.items():
            if device in full_context:
                for issue, details in issues.items():
                    if issue in full_context or any(symptom in full_context for symptom in details["symptoms"]):
                        matched_advice = (device, issue, details)
                        break

        if matched_advice:
            device, issue, details = matched_advice

            response = f"""🔧 **RepairGPT Knowledge Base Response**

**Device**: {device.title().replace('-', '-')}
**Issue**: {issue.title()} Problem

**Symptoms You Might Experience**:
{chr(10).join(f"• {symptom.title()}" for symptom in details["symptoms"])}

**Most Likely Causes**:
{chr(10).join(f"• {cause.title()}" for cause in details["causes"])}

**Recommended Solutions** (in order of difficulty):
{chr(10).join(details["solutions"])}

**📊 Repair Information**:
• **Difficulty**: {details["difficulty"]}
• **Tools Needed**: {', '.join(details["tools"])}
• **Estimated Cost**: {details["cost"]}
• **Success Rates**: {details["success_rate"]}

**⚠️ Safety Reminders**:
• Always power off devices before repair
• Use proper anti-static precautions
• Work in good lighting with proper tools
• If unsure, consult a professional
• Check warranty status before opening devices

**🤔 Need More Help?**
If this doesn't match your specific issue, please provide more details about:
1. Exact symptoms you're experiencing
2. When the problem started
3. Any recent incidents (drops, spills, etc.)
4. Your comfort level with repairs

*This response is generated from RepairGPT's built-in knowledge base.
For AI-powered personalized assistance, configure API keys in settings.*"""

        else:
            # General repair guidance when no specific match
            response = f"""🔧 **RepairGPT General Repair Guidance**

I understand you're having an issue with your device. While I don't have AI assistance active right now,
I can provide general repair guidance.

**🔍 Diagnostic Steps**:
1. **Identify the Problem**: Be specific about symptoms
   - What exactly is happening?
   - When did it start?
   - Does it happen consistently?

2. **Safety First**:
   - Power off the device completely
   - Disconnect from power sources
   - Ground yourself to prevent static damage

3. **Basic Troubleshooting**:
   - Try a simple restart/power cycle
   - Check all connections and cables
   - Look for obvious physical damage
   - Test in safe mode (if applicable)

**📱 Common Device Issues & Quick Fixes**:

**Gaming Consoles** (Switch, PlayStation, Xbox):
• Controller drift → Recalibration, cleaning, contact cleaner
• Won't turn on → Power cycle, check cables, try different outlet
• Overheating → Clean vents, check ventilation

**Smartphones** (iPhone, Android):
• Screen issues → Restart, check for software updates
• Battery drain → Check battery health, close background apps
• Won't charge → Try different cable/adapter, clean charging port

**Laptops/Computers**:
• Won't boot → Check power supply, reseat RAM, hard reset
• Slow performance → Check storage space, run antivirus scan
• Overheating → Clean fans, check thermal paste

**🛠️ When to Seek Professional Help**:
• Complex internal repairs (motherboard, CPU, etc.)
• Liquid damage
• Warranty still valid
• Lack proper tools or experience
• Risk of making problem worse

**💡 Your Issue**: "{user_message[:150]}{'...' if len(user_message) > 150 else ''}"

For more specific guidance, please tell me:
- Device type and model
- Specific symptoms
- What you've already tried

*To enable full AI-powered assistance, configure OpenAI or Anthropic API keys in the application settings.*"""

        return response

    def _error_response(self, error_msg: str) -> str:
        """Generate error response"""
        return f"""I apologize, but I encountered an issue processing your request: {error_msg}

Please try:
1. Rephrasing your question
2. Providing more specific details about your device and issue
3. Trying again in a moment

If the problem persists, you may want to:
- Check device manufacturer documentation
- Consult professional repair services
- Visit repair communities like iFixit

I'm here to help when the technical issue is resolved!"""

    def get_conversation_summary(self) -> Dict:
        """Get summary of current conversation"""
        return {
            "session_id": self.session_id,
            "message_count": len(self.conversation_history),
            "context": asdict(self.repair_context),
            "active_client": self.active_client,
            "last_updated": datetime.now().isoformat(),
        }

    def save_conversation(self, filepath: str):
        """Save conversation to JSON file"""
        conversation_data = {
            "session_id": self.session_id,
            "context": asdict(self.repair_context),
            "messages": [asdict(msg) for msg in self.conversation_history],
            "metadata": {
                "active_client": self.active_client,
                "created": self.session_id,
                "saved": datetime.now().isoformat(),
            },
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)

        self.log_info(
            "Conversation saved",
            filepath=filepath,
            message_count=len(self.conversation_history),
        )

    def load_conversation(self, filepath: str):
        """Load conversation from JSON file"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.session_id = data["session_id"]
        self.repair_context = RepairContext(**data["context"])
        self.conversation_history = [Message(**msg) for msg in data["messages"]]

        self.log_info(
            "Conversation loaded",
            filepath=filepath,
            message_count=len(self.conversation_history),
        )

    def reset_conversation(self):
        """Reset conversation history and context"""
        self.conversation_history = []
        self.repair_context = RepairContext()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_info("Conversation reset", new_session_id=self.session_id)


# Example usage and testing
if __name__ == "__main__":
    print("Testing RepairGPT Chatbot...")

    # Initialize chatbot
    bot = RepairChatbot(preferred_model="openai")
    print(f"Active client: {bot.active_client}")

    # Set repair context
    bot.update_context(
        device_type="Nintendo Switch",
        device_model="OLED",
        issue_description="Joy-Con drift on left controller",
        user_skill_level="beginner",
    )

    # Test conversation
    test_messages = [
        "My Nintendo Switch left Joy-Con is drifting. What should I try first?",
        "I've tried calibration but it didn't work. Is there a way to fix this myself?",
        "What tools would I need for this repair?",
    ]

    for message in test_messages:
        print(f"\nUser: {message}")
        response = bot.chat(message)
        print(f"Bot: {response}")

    # Show conversation summary
    print(f"\nConversation Summary: {bot.get_conversation_summary()}")
    print("\nRepairGPT Chatbot test completed!")
