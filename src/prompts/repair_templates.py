"""
Repair Prompt Templates for RepairGPT
Implements Issue #10: 修理用プロンプトテンプレートの作成
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class PromptType(Enum):
    """Types of repair prompts"""

    DIAGNOSTIC = "diagnostic"
    STEP_BY_STEP = "step_by_step"
    TROUBLESHOOTING = "troubleshooting"
    SAFETY_CHECK = "safety_check"
    PARTS_RECOMMENDATION = "parts_recommendation"
    TOOL_SELECTION = "tool_selection"
    DIFFICULTY_ASSESSMENT = "difficulty_assessment"
    SUCCESS_PREDICTION = "success_prediction"


@dataclass
class PromptContext:
    """Context for prompt generation"""

    device_name: str = ""
    device_model: str = ""
    issue_description: str = ""
    user_skill_level: str = "beginner"
    symptoms: List[str] = None
    available_tools: List[str] = None
    budget: str = ""
    urgency: str = "normal"
    previous_attempts: List[str] = None

    def __post_init__(self):
        if self.symptoms is None:
            self.symptoms = []
        if self.available_tools is None:
            self.available_tools = []
        if self.previous_attempts is None:
            self.previous_attempts = []


class RepairPromptTemplates:
    """Collection of repair prompt templates"""

    # Base system prompts
    SYSTEM_PROMPTS = {
        "repair_expert": """You are an expert electronics repair technician with 15+ years of experience. You specialize in consumer electronics including gaming consoles, smartphones, laptops, and other devices.

Key principles:
1. SAFETY FIRST - Always prioritize user safety and warn about potential hazards
2. Clear, step-by-step instructions appropriate for the user's skill level
3. Honest assessment of repair difficulty and success likelihood
4. Warn about warranty implications when relevant
5. Suggest professional help when repairs are too complex or risky

Your responses should be:
- Practical and actionable
- Safety-conscious
- Appropriate for the user's skill level
- Honest about limitations and risks
- Well-structured with clear steps""",
        "diagnostic_specialist": """You are a diagnostic specialist for electronic devices. Your role is to help users identify the root cause of device issues through systematic troubleshooting.

Approach:
1. Ask clarifying questions to narrow down the problem
2. Suggest simple tests to isolate the issue
3. Explain what each test reveals about the device's condition
4. Provide clear next steps based on test results
5. Recommend when professional diagnosis is needed

Focus on:
- Non-destructive testing methods
- User safety during diagnosis
- Clear explanation of what's happening inside the device
- Logical troubleshooting sequence""",
        "safety_advisor": """You are a safety advisor for electronics repair. Your primary concern is preventing injury, property damage, and further device damage.

Always consider:
1. Electrical safety (shock, short circuits)
2. Chemical safety (battery acids, cleaning solvents)
3. Physical safety (sharp tools, small parts)
4. Environmental safety (ESD protection, ventilation)
5. Tool safety (proper usage, maintenance)

Provide:
- Clear safety warnings
- Proper protective equipment recommendations
- Safe work environment setup
- Emergency procedures
- When to stop and seek professional help""",
    }

    # Specific repair templates
    REPAIR_TEMPLATES = {
        PromptType.DIAGNOSTIC: """
Analyze the following device issue and provide diagnostic guidance:

**Device Information:**
- Device: {device_name} {device_model}
- Issue: {issue_description}
- Symptoms: {symptoms}
- User's Previous Attempts: {previous_attempts}

**User Profile:**
- Skill Level: {user_skill_level}
- Available Tools: {available_tools}

**Please provide:**
1. **Most Likely Causes** (ranked by probability)
2. **Diagnostic Steps** (non-destructive tests to confirm the cause)
3. **Required Tools** for diagnosis
4. **Safety Precautions** specific to this device/issue
5. **When to Stop** and seek professional help

**Format your response with clear sections and safety warnings where appropriate.**
""",
        PromptType.STEP_BY_STEP: """
Create a detailed repair guide for the following issue:

**Repair Details:**
- Device: {device_name} {device_model}
- Problem: {issue_description}
- User Skill Level: {user_skill_level}
- Available Tools: {available_tools}
- Budget: {budget}

**Provide a comprehensive guide including:**

1. **Pre-Repair Assessment**
   - Confirm the diagnosis
   - Success likelihood
   - Difficulty rating
   - Time estimate

2. **Safety Preparation**
   - Required safety equipment
   - Workspace setup
   - Precautions specific to this device

3. **Tools and Parts Needed**
   - Essential tools
   - Optional but helpful tools
   - Replacement parts with specifications
   - Where to obtain parts

4. **Step-by-Step Instructions**
   - Numbered steps with clear descriptions
   - Photos or diagrams needed (describe what to show)
   - Critical warnings at each step
   - Tips for success

5. **Testing and Verification**
   - How to test the repair
   - What success looks like
   - Troubleshooting if it doesn't work

6. **Reassembly and Final Checks**
   - Proper reassembly order
   - Final safety checks
   - Cleanup procedures

**Adjust complexity and detail level for {user_skill_level} skill level.**
""",
        PromptType.TROUBLESHOOTING: """
Help troubleshoot an issue during repair:

**Current Situation:**
- Device: {device_name} {device_model}
- Original Issue: {issue_description}
- Current Problem: {symptoms}
- Skill Level: {user_skill_level}
- Steps Already Taken: {previous_attempts}

**Provide troubleshooting guidance:**

1. **Immediate Safety Check**
   - Any immediate dangers to address
   - Whether to stop work immediately

2. **Problem Analysis**
   - What likely went wrong
   - Common mistakes at this stage
   - How to verify the actual problem

3. **Recovery Steps**
   - How to safely back out of current state
   - Steps to correct the issue
   - Alternative approaches

4. **Prevention**
   - How to avoid this problem in future repairs
   - Better techniques or tools to use

5. **Decision Point**
   - Whether to continue or seek professional help
   - Cost/benefit analysis of continuing

**Be honest about when the repair has become too complex or risky to continue.**
""",
        PromptType.SAFETY_CHECK: """
Perform a safety assessment for this repair:

**Repair Context:**
- Device: {device_name} {device_model}
- Planned Repair: {issue_description}
- User Skill Level: {user_skill_level}
- Available Safety Equipment: {available_tools}

**Provide safety assessment:**

1. **Risk Level Assessment**
   - Overall safety risk (Low/Medium/High/Extreme)
   - Specific hazards present
   - Risk to user vs. risk to device

2. **Required Safety Equipment**
   - Essential protective gear
   - Recommended workspace setup
   - Environmental controls needed

3. **Critical Safety Procedures**
   - Power isolation steps
   - ESD protection measures
   - Chemical/battery safety
   - Tool safety requirements

4. **Red Flags - When to Stop**
   - Conditions that make repair unsafe
   - Signs that professional help is needed
   - Emergency procedures

5. **Skill Appropriateness**
   - Whether this repair matches user skill level
   - Skills that need to be learned first
   - Recommended learning progression

**Recommend whether this repair should be attempted by this user.**
""",
        PromptType.PARTS_RECOMMENDATION: """
Recommend replacement parts for this repair:

**Device and Issue:**
- Device: {device_name} {device_model}
- Problem: {issue_description}
- Budget: {budget}
- Urgency: {urgency}

**Provide parts recommendation:**

1. **Essential Parts**
   - Exact part numbers when available
   - Specifications and compatibility info
   - Why each part is needed

2. **Quality Tiers**
   - OEM (Original Equipment Manufacturer) options
   - High-quality aftermarket alternatives
   - Budget-friendly options
   - Parts to avoid (and why)

3. **Sourcing Information**
   - Authorized dealers
   - Reliable online sources
   - Local repair shops
   - Lead times and availability

4. **Cost Analysis**
   - Part costs breakdown
   - Tool costs if new tools needed
   - Total repair cost vs. replacement cost
   - Value proposition assessment

5. **Installation Considerations**
   - Parts that require special tools or skills
   - Parts that should be installed by professionals
   - Warranty implications

**Consider the user's budget of {budget} and urgency level of {urgency}.**
""",
        PromptType.TOOL_SELECTION: """
Recommend tools for this repair:

**Repair Context:**
- Device: {device_name} {device_model}
- Repair Type: {issue_description}
- User Skill Level: {user_skill_level}
- Current Tools: {available_tools}
- Budget: {budget}

**Provide tool recommendations:**

1. **Essential Tools**
   - Absolutely required tools
   - Specific sizes/types needed
   - Why each tool is necessary

2. **Recommended Tools**
   - Tools that make the job easier/safer
   - Quality vs. budget considerations
   - Multi-use tools for future repairs

3. **Nice-to-Have Tools**
   - Professional-grade options
   - Specialized tools for this device type
   - Tools for advanced techniques

4. **Tool Alternatives**
   - Household items that can substitute
   - DIY tool modifications
   - Borrowing vs. buying considerations

5. **Purchasing Guidance**
   - Where to buy quality tools
   - Brands to consider/avoid
   - Tool maintenance requirements
   - Long-term investment value

**Prioritize recommendations based on the {budget} budget constraint.**
""",
        PromptType.DIFFICULTY_ASSESSMENT: """
Assess the difficulty of this repair:

**Repair Details:**
- Device: {device_name} {device_model}
- Issue: {issue_description}
- User Skill Level: {user_skill_level}
- Available Tools: {available_tools}

**Provide difficulty assessment:**

1. **Overall Difficulty Rating**
   - Beginner/Intermediate/Advanced/Expert
   - Specific challenges in this repair
   - Skills required vs. user's current skills

2. **Skill Requirements**
   - Technical skills needed
   - Fine motor skills required
   - Problem-solving complexity
   - Time and patience requirements

3. **Risk Assessment**
   - Risk of making problem worse
   - Risk of injury
   - Risk of destroying device
   - Financial risk analysis

4. **Success Probability**
   - Likelihood of successful repair
   - Common failure points
   - What "partial success" might look like

5. **Alternatives**
   - Easier repair approaches
   - Partial fixes or workarounds
   - When to consider professional repair
   - Cost comparison with replacement

**Be honest about whether this repair is appropriate for this user's skill level.**
""",
        PromptType.SUCCESS_PREDICTION: """
Predict the likelihood of successful repair:

**Repair Context:**
- Device: {device_name} {device_model}
- Issue: {issue_description}
- User Skill Level: {user_skill_level}
- Available Tools: {available_tools}
- Previous Repair Attempts: {previous_attempts}

**Provide success prediction:**

1. **Success Probability**
   - Percentage likelihood of complete success
   - Percentage likelihood of partial success
   - Factors that improve/reduce chances

2. **Critical Success Factors**
   - Most important steps that determine outcome
   - Common points of failure
   - Skills that most impact success

3. **Mitigation Strategies**
   - How to maximize success chances
   - Backup plans if primary approach fails
   - When to try alternative methods

4. **Failure Analysis**
   - Most likely ways this repair could fail
   - How to recognize early failure signs
   - Damage limitation strategies

5. **Go/No-Go Recommendation**
   - Clear recommendation on whether to proceed
   - Conditions under which to proceed
   - Alternative options to consider

**Provide an honest, data-driven assessment based on the specific circumstances.**
""",
    }

    @classmethod
    def get_template(cls, prompt_type: PromptType) -> str:
        """Get a specific prompt template"""
        return cls.REPAIR_TEMPLATES.get(prompt_type, "")

    @classmethod
    def get_system_prompt(cls, prompt_category: str = "repair_expert") -> str:
        """Get a system prompt for the AI model"""
        return cls.SYSTEM_PROMPTS.get(
            prompt_category, cls.SYSTEM_PROMPTS["repair_expert"]
        )

    @classmethod
    def format_template(cls, prompt_type: PromptType, context: PromptContext) -> str:
        """Format a template with the provided context"""
        template = cls.get_template(prompt_type)
        if not template:
            return ""

        # Convert context to dict for formatting
        context_dict = {
            "device_name": context.device_name,
            "device_model": context.device_model,
            "issue_description": context.issue_description,
            "user_skill_level": context.user_skill_level,
            "symptoms": (
                ", ".join(context.symptoms) if context.symptoms else "Not specified"
            ),
            "available_tools": (
                ", ".join(context.available_tools)
                if context.available_tools
                else "Not specified"
            ),
            "budget": context.budget or "Not specified",
            "urgency": context.urgency,
            "previous_attempts": (
                ", ".join(context.previous_attempts)
                if context.previous_attempts
                else "None"
            ),
        }

        try:
            return template.format(**context_dict)
        except KeyError as e:
            return f"Template formatting error: Missing key {e}"

    @classmethod
    def get_all_template_types(cls) -> List[PromptType]:
        """Get all available template types"""
        return list(PromptType)

    @classmethod
    def create_custom_prompt(
        cls,
        base_type: PromptType,
        device_specific_info: str = "",
        additional_context: str = "",
    ) -> str:
        """Create a custom prompt by modifying a base template"""
        base_template = cls.get_template(base_type)

        custom_additions = ""
        if device_specific_info:
            custom_additions += (
                f"\n**Device-Specific Information:**\n{device_specific_info}\n"
            )

        if additional_context:
            custom_additions += f"\n**Additional Context:**\n{additional_context}\n"

        return base_template + custom_additions


# Example usage and testing
if __name__ == "__main__":
    print("Testing RepairGPT Prompt Templates...")

    # Create test context
    test_context = PromptContext(
        device_name="Nintendo Switch",
        device_model="OLED",
        issue_description="Joy-Con analog stick drift",
        user_skill_level="beginner",
        symptoms=[
            "Left stick moves cursor without input",
            "Character moves randomly in games",
        ],
        available_tools=["Phillips screwdriver", "Plastic prying tools"],
        budget="$50",
        urgency="normal",
    )

    # Test different prompt types
    prompt_types = [
        PromptType.DIAGNOSTIC,
        PromptType.STEP_BY_STEP,
        PromptType.SAFETY_CHECK,
        PromptType.DIFFICULTY_ASSESSMENT,
    ]

    for prompt_type in prompt_types:
        print(f"\n{'='*50}")
        print(f"Testing {prompt_type.value.upper()} template:")
        print(f"{'='*50}")

        formatted_prompt = RepairPromptTemplates.format_template(
            prompt_type, test_context
        )
        print(
            formatted_prompt[:500] + "..."
            if len(formatted_prompt) > 500
            else formatted_prompt
        )

    # Test system prompts
    print(f"\n{'='*50}")
    print("System Prompt (Repair Expert):")
    print(f"{'='*50}")
    print(RepairPromptTemplates.get_system_prompt("repair_expert"))

    print("\nPrompt template testing completed!")
