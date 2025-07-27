"""Advanced prompt templates for RepairGPT LLM interactions"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class PromptType(Enum):
    """Types of prompts for different use cases"""

    DIAGNOSIS = "diagnosis"
    REPAIR_GUIDE = "repair_guide"
    TROUBLESHOOTING = "troubleshooting"
    SAFETY_CHECK = "safety_check"
    PARTS_IDENTIFICATION = "parts_identification"
    TOOL_RECOMMENDATION = "tool_recommendation"
    SKILL_ASSESSMENT = "skill_assessment"


@dataclass
class PromptContext:
    """Context information for prompt generation"""

    device_type: str
    device_model: str
    issue_description: str
    user_skill_level: str
    available_tools: List[str]
    safety_concerns: List[str]
    previous_attempts: List[str]
    symptoms: List[str]
    environment: str = "home"  # home, workshop, professional
    urgency: str = "normal"  # low, normal, high, emergency
    budget_constraint: str = "moderate"  # low, moderate, high, unlimited


class PromptTemplateManager:
    """Manages prompt templates for different repair scenarios"""

    def __init__(self):
        self.templates = self._load_templates()
        self.system_prompts = self._load_system_prompts()

    def _load_templates(self) -> Dict[PromptType, Dict]:
        """Load prompt templates for each use case"""
        return {
            PromptType.DIAGNOSIS: {
                "base": self._diagnosis_template(),
                "followup": self._diagnosis_followup_template(),
                "detailed": self._diagnosis_detailed_template(),
            },
            PromptType.REPAIR_GUIDE: {
                "step_by_step": self._repair_guide_template(),
                "quick_fix": self._quick_fix_template(),
                "comprehensive": self._comprehensive_repair_template(),
            },
            PromptType.TROUBLESHOOTING: {
                "systematic": self._systematic_troubleshooting_template(),
                "quick": self._quick_troubleshooting_template(),
            },
            PromptType.SAFETY_CHECK: {
                "general": self._safety_check_template(),
                "electrical": self._electrical_safety_template(),
                "mechanical": self._mechanical_safety_template(),
            },
            PromptType.PARTS_IDENTIFICATION: {
                "visual": self._parts_identification_template(),
                "functional": self._functional_parts_template(),
            },
            PromptType.TOOL_RECOMMENDATION: {
                "basic": self._basic_tools_template(),
                "advanced": self._advanced_tools_template(),
            },
            PromptType.SKILL_ASSESSMENT: {
                "beginner": self._beginner_assessment_template(),
                "intermediate": self._intermediate_assessment_template(),
                "advanced": self._advanced_assessment_template(),
            },
        }

    def _load_system_prompts(self) -> Dict[str, str]:
        """Load system prompts for different scenarios"""
        return {
            "repair_expert": """
You are RepairGPT, an expert electronics repair assistant with deep knowledge of consumer electronics, gaming consoles, smartphones, laptops, and other electronic devices.

Core Principles:
1. SAFETY FIRST - Always prioritize user safety and highlight potential hazards
2. ACCURACY - Provide technically accurate information based on established repair practices
3. CLARITY - Use clear, step-by-step instructions appropriate for the user's skill level
4. PRACTICALITY - Focus on solutions that are actually feasible for the user
5. HONESTY - Be transparent about repair complexity and success likelihood

Expertise Areas:
- Gaming Consoles (Nintendo Switch, PlayStation, Xbox)
- Smartphones (iPhone, Android devices)
- Laptops and Desktop Computers
- Tablets and E-readers
- Audio Equipment (Headphones, Speakers)
- Small Appliances with Electronic Components

Always consider:
- User's stated skill level
- Available tools and workspace
- Safety implications of each step
- Alternative solutions if primary approach fails
- When to recommend professional repair instead
""",
            "diagnosis_specialist": """
You are a diagnostic specialist for electronic device troubleshooting. Your role is to help users
systematically identify the root cause of device problems through careful questioning and logical analysis.

Diagnostic Approach:
1. Gather comprehensive symptom information
2. Identify potential causes through systematic elimination
3. Recommend specific tests to narrow down issues
4. Provide confidence levels for each potential diagnosis
5. Suggest appropriate next steps based on findings

Key Skills:
- Pattern recognition for common failure modes
- Understanding of electronic component behavior
- Knowledge of device-specific common issues
- Ability to guide users through diagnostic procedures
- Risk assessment for different failure scenarios
""",
            "safety_advisor": """
You are a safety advisor specializing in electronics repair. Your primary responsibility is ensuring user safety during repair procedures.

Safety Priorities:
1. Electrical safety (shock, short circuit prevention)
2. Chemical safety (battery, cleaning solvents)
3. Mechanical safety (sharp tools, small parts)
4. Fire/heat safety (overheating, thermal damage)
5. Data protection (backup requirements)

Always:
- Warn about specific hazards before each procedure
- Recommend appropriate protective equipment
- Explain emergency procedures for accidents
- Identify when to stop and seek professional help
- Consider environmental factors (ventilation, workspace)
""",
        }

    def generate_prompt(
        self,
        prompt_type: PromptType,
        context: PromptContext,
        template_variant: str = "base",
        custom_instructions: str = "",
    ) -> str:
        """Generate a complete prompt based on type and context"""

        # Get base template
        template_dict = self.templates.get(prompt_type, {})
        template = template_dict.get(template_variant, template_dict.get("base", ""))

        if not template:
            raise ValueError(f"No template found for {prompt_type.value}/{template_variant}")

        # Format template with context
        formatted_prompt = template.format(
            device_type=context.device_type,
            device_model=context.device_model,
            issue_description=context.issue_description,
            user_skill_level=context.user_skill_level,
            available_tools=(", ".join(context.available_tools) if context.available_tools else "Not specified"),
            safety_concerns=(", ".join(context.safety_concerns) if context.safety_concerns else "None identified"),
            previous_attempts=(", ".join(context.previous_attempts) if context.previous_attempts else "None"),
            symptoms=(", ".join(context.symptoms) if context.symptoms else "Not detailed"),
            environment=context.environment,
            urgency=context.urgency,
            budget_constraint=context.budget_constraint,
            custom_instructions=custom_instructions,
        )

        return formatted_prompt

    def get_system_prompt(self, specialist_type: str = "repair_expert") -> str:
        """Get system prompt for specific specialist type"""
        return self.system_prompts.get(specialist_type, self.system_prompts["repair_expert"])

    # Template definitions
    def _diagnosis_template(self) -> str:
        return """
Please help diagnose the issue with this device:

**Device Information:**
- Type: {device_type}
- Model: {device_model}
- Environment: {environment}

**Issue Description:**
{issue_description}

**Observed Symptoms:**
{symptoms}

**Previous Repair Attempts:**
{previous_attempts}

**User Skill Level:** {user_skill_level}
**Available Tools:** {available_tools}
**Safety Concerns:** {safety_concerns}
**Urgency:** {urgency}

**Diagnostic Request:**
Please provide:
1. Most likely causes (ranked by probability)
2. Specific diagnostic steps to confirm each cause
3. Required tools for each diagnostic step
4. Safety precautions for the diagnostic process
5. Estimated time and difficulty for diagnosis
6. When to stop and seek professional help

{custom_instructions}
"""

    def _diagnosis_followup_template(self) -> str:
        return """
Based on the initial diagnosis, I need more specific guidance:

**Device:** {device_type} {device_model}
**Original Issue:** {issue_description}
**Diagnostic Results So Far:** {previous_attempts}

**Current Situation:**
{symptoms}

**Next Steps Needed:**
Please provide:
1. Interpretation of current diagnostic results
2. Next specific tests or checks to perform
3. What the results of each test would indicate
4. Decision tree for different test outcomes
5. Point at which to move from diagnosis to repair

{custom_instructions}
"""

    def _repair_guide_template(self) -> str:
        return """
Please provide a comprehensive repair guide for:

**Device:** {device_type} {device_model}
**Problem:** {issue_description}
**Confirmed Diagnosis:** {symptoms}

**User Profile:**
- Skill Level: {user_skill_level}
- Available Tools: {available_tools}
- Work Environment: {environment}
- Budget Constraints: {budget_constraint}

**Safety Considerations:** {safety_concerns}

**Required Output:**
1. **Pre-repair Checklist**
   - Required tools and parts
   - Safety equipment needed
   - Workspace preparation
   - Data backup requirements

2. **Step-by-Step Repair Process**
   - Detailed instructions for each step
   - Visual landmarks and confirmation points
   - Common mistakes to avoid
   - Troubleshooting if steps don't work as expected

3. **Post-repair Verification**
   - Testing procedures to confirm fix
   - Quality check steps
   - Performance optimization

4. **Risk Assessment**
   - Difficulty rating (1-10)
   - Estimated time required
   - Success probability
   - Potential complications

5. **Alternative Solutions**
   - If this repair fails
   - Temporary workarounds
   - Professional repair considerations

{custom_instructions}
"""

    def _safety_check_template(self) -> str:
        return """
Please perform a comprehensive safety analysis for this repair:

**Repair Details:**
- Device: {device_type} {device_model}
- Procedure: {issue_description}
- User Skill: {user_skill_level}
- Environment: {environment}

**Current Safety Concerns:** {safety_concerns}
**Available Safety Equipment:** {available_tools}

**Required Safety Analysis:**

1. **Hazard Identification**
   - Electrical hazards (shock, short circuit)
   - Chemical hazards (batteries, solvents)
   - Mechanical hazards (sharp tools, pressure)
   - Thermal hazards (heat, fire risk)
   - Environmental hazards (ventilation, workspace)

2. **Risk Assessment**
   - Probability of each hazard occurring
   - Severity of potential consequences
   - Overall risk level for this user

3. **Safety Precautions**
   - Required protective equipment
   - Workspace safety setup
   - Emergency procedures
   - First aid considerations

4. **Go/No-Go Decision**
   - Is this repair safe for this user?
   - What conditions must be met before proceeding?
   - Clear stop criteria during the repair

5. **Emergency Procedures**
   - What to do if something goes wrong
   - Emergency contact information
   - Damage limitation steps

{custom_instructions}
"""

    def _parts_identification_template(self) -> str:
        return """
Help identify the correct parts needed for this repair:

**Device:** {device_type} {device_model}
**Repair Need:** {issue_description}
**Symptoms:** {symptoms}

**User Context:**
- Skill Level: {user_skill_level}
- Budget: {budget_constraint}
- Location/Environment: {environment}

**Parts Identification Needed:**

1. **Primary Components**
   - Exact part numbers and specifications
   - Compatible alternatives if available
   - Quality grades (OEM vs aftermarket)

2. **Supporting Parts**
   - Screws, connectors, adhesives
   - Replacement wear items
   - Optional upgrade components

3. **Tools and Consumables**
   - Specialized tools required
   - Cleaning supplies
   - Protective materials

4. **Sourcing Information**
   - Recommended suppliers
   - Price ranges
   - Availability and lead times
   - Shipping considerations

5. **Quality Assessment**
   - How to verify authentic parts
   - Red flags for counterfeit components
   - Quality testing before installation

{custom_instructions}
"""

    def _systematic_troubleshooting_template(self) -> str:
        return """
Let's systematically troubleshoot this issue:

**Device:** {device_type} {device_model}
**Problem Report:** {issue_description}
**Symptoms:** {symptoms}
**Previous Attempts:** {previous_attempts}

**User Profile:**
- Skill Level: {user_skill_level}
- Available Tools: {available_tools}
- Time Available: Based on {urgency} urgency

**Systematic Troubleshooting Plan:**

1. **Problem Definition**
   - Exact symptom description
   - When problem occurs
   - Frequency and patterns
   - Environmental factors

2. **Information Gathering**
   - Device history and usage
   - Recent changes or events
   - Error messages or codes
   - Performance degradation timeline

3. **Hypothesis Formation**
   - Most likely causes (ranked)
   - Test strategy for each hypothesis
   - Required tools for each test

4. **Testing Sequence**
   - Start with simplest/safest tests
   - Non-destructive testing first
   - Progressive isolation of components
   - Documentation of results

5. **Decision Points**
   - When to escalate complexity
   - When to seek additional help
   - When to consider replacement vs repair

{custom_instructions}
"""

    def _diagnosis_detailed_template(self) -> str:
        return """
Provide detailed diagnostic analysis:

**Complete Device Profile:**
- Device: {device_type} {device_model}
- Issue: {issue_description}
- Symptoms: {symptoms}
- Environment: {environment}
- Previous Work: {previous_attempts}

**Diagnostic Deep Dive Required:**

1. **Component-Level Analysis**
   - Which specific components could cause these symptoms
   - Component interaction effects
   - Failure mode analysis for each component

2. **Signal Flow Analysis**
   - Trace the signal/power path
   - Identify test points for measurements
   - Expected vs actual values at each point

3. **Failure Pattern Recognition**
   - Compare to known failure patterns
   - Statistical likelihood of different causes
   - Age and usage pattern considerations

4. **Advanced Diagnostic Tests**
   - Electrical measurements needed
   - Software diagnostic tools
   - Mechanical stress tests
   - Thermal analysis if relevant

5. **Differential Diagnosis**
   - Rule out similar conditions
   - Confirm diagnosis with multiple test methods
   - Document diagnostic confidence level

{custom_instructions}
"""

    def _quick_fix_template(self) -> str:
        return """
Provide quick fix options for immediate relief:

**Device:** {device_type} {device_model}
**Issue:** {issue_description}
**Urgency:** {urgency}
**Skill Level:** {user_skill_level}

**Quick Fix Requirements:**

1. **Immediate Actions** (5-10 minutes)
   - Emergency stabilization steps
   - Prevent further damage
   - Basic functionality restoration

2. **Temporary Solutions** (30 minutes or less)
   - Workarounds that don't require parts
   - Simple adjustments or resets
   - Software fixes if applicable

3. **Tool-Based Quick Fixes** (if tools available)
   - Using: {available_tools}
   - Simple mechanical adjustments
   - Basic cleaning procedures

4. **Success Probability**
   - Likelihood each quick fix will work
   - Duration of temporary fix
   - Risks of quick fix approach

5. **Next Steps**
   - When quick fixes aren't sufficient
   - Planning for permanent repair
   - Preventing recurrence

{custom_instructions}
"""

    def _comprehensive_repair_template(self) -> str:
        return """
Provide comprehensive repair documentation:

**Complete Repair Project:**
- Device: {device_type} {device_model}
- Issue: {issue_description}
- Scope: Full restoration to original function
- User Level: {user_skill_level}
- Environment: {environment}
- Budget: {budget_constraint}

**Comprehensive Repair Plan:**

1. **Project Planning**
   - Total time estimate
   - Milestone breakdown
   - Resource requirements
   - Risk assessment

2. **Preparation Phase**
   - Workspace setup
   - Tool and part procurement
   - Safety preparations
   - Documentation setup

3. **Disassembly Procedure**
   - Step-by-step disassembly
   - Organization and labeling
   - Photo documentation points
   - Component condition assessment

4. **Repair Execution**
   - Component replacement procedures
   - Adjustment and calibration
   - Quality control checkpoints
   - Troubleshooting contingencies

5. **Reassembly and Testing**
   - Reverse assembly procedure
   - Progressive testing approach
   - Performance verification
   - Final quality inspection

6. **Documentation and Maintenance**
   - Repair record keeping
   - Future maintenance schedule
   - Performance monitoring
   - Warranty considerations

{custom_instructions}
"""

    def _beginner_assessment_template(self) -> str:
        return """
Assess if this repair is appropriate for a beginner:

**Repair Assessment for Beginner Level:**
- Device: {device_type} {device_model}
- Proposed Repair: {issue_description}
- Available Tools: {available_tools}
- Environment: {environment}

**Beginner Suitability Analysis:**

1. **Skill Requirements**
   - Technical complexity (1-10 scale)
   - Hand dexterity requirements
   - Problem-solving complexity
   - Learning curve assessment

2. **Safety Considerations**
   - Risk level for inexperienced user
   - Potential for injury
   - Risk of device damage
   - Emergency response capabilities

3. **Success Probability**
   - Likelihood of successful repair
   - Common beginner mistakes
   - Recovery options if repair fails

4. **Learning Value**
   - Educational benefit of attempting repair
   - Transferable skills gained
   - Confidence building potential

5. **Recommendation**
   - Go/no-go for beginner attempt
   - Modifications to make repair beginner-friendly
   - Alternative learning opportunities
   - When to recommend professional help

{custom_instructions}
"""

    def _basic_tools_template(self) -> str:
        return """
Recommend basic tools for this repair:

**Tool Requirements Analysis:**
- Device: {device_type} {device_model}
- Repair: {issue_description}
- User Level: {user_skill_level}
- Budget: {budget_constraint}

**Basic Tool Recommendations:**

1. **Essential Tools** (minimum required)
   - Specific screwdrivers needed
   - Basic hand tools
   - Safety equipment
   - Measurement tools if needed

2. **Helpful Additions** (improve success rate)
   - Organization tools
   - Lighting and magnification
   - Cleaning supplies
   - Documentation tools

3. **Safety Equipment**
   - Personal protective equipment
   - Fire safety tools
   - First aid considerations
   - Emergency contact list

4. **Purchasing Guidance**
   - Quality vs cost considerations
   - Where to buy tools
   - Multi-use tool priorities
   - Building a basic toolkit

5. **Tool Alternatives**
   - Household item substitutes
   - Borrowing vs buying decisions
   - Rental options for expensive tools

{custom_instructions}
"""

    def _advanced_tools_template(self) -> str:
        return """
Recommend advanced tools for professional-quality repair:

**Advanced Tool Requirements:**
- Device: {device_type} {device_model}
- Complex Repair: {issue_description}
- Advanced User: {user_skill_level}
- Professional Environment: {environment}

**Professional Tool Recommendations:**

1. **Precision Tools**
   - Specialized screwdrivers and bits
   - Precision tweezers and picks
   - Torque-controlled tools
   - Anti-static equipment

2. **Measurement Equipment**
   - Multimeters and oscilloscopes
   - Temperature measurement
   - Pressure and force gauges
   - Optical measurement tools

3. **Workstation Setup**
   - ESD-safe workspace
   - Proper lighting and magnification
   - Ventilation and fume extraction
   - Organization and storage systems

4. **Advanced Techniques**
   - Soldering and desoldering equipment
   - Heat guns and hot air stations
   - Ultrasonic cleaners
   - Component testing equipment

5. **Quality Assurance**
   - Testing and verification tools
   - Documentation systems
   - Calibration requirements
   - Maintenance of tools

{custom_instructions}
"""

    def _intermediate_assessment_template(self) -> str:
        return """
Assess intermediate-level repair feasibility:

**Intermediate Skill Assessment:**
- Device: {device_type} {device_model}
- Repair Challenge: {issue_description}
- Available Resources: {available_tools}
- Working Environment: {environment}

**Intermediate Level Analysis:**

1. **Skill Bridge Requirements**
   - Gap between current and required skills
   - Learning opportunities during repair
   - Skill development potential
   - Knowledge transfer value

2. **Technical Complexity**
   - Multi-step procedure management
   - Component interaction understanding
   - Troubleshooting complexity
   - Documentation requirements

3. **Risk vs Reward**
   - Success probability at intermediate level
   - Cost of failure scenarios
   - Learning value vs risk
   - Time investment analysis

4. **Support Requirements**
   - Need for expert consultation
   - Online resource requirements
   - Community support value
   - Professional backup plans

5. **Progression Path**
   - How this repair advances skills
   - Next logical repair challenges
   - Building toward advanced capabilities
   - Professional development value

{custom_instructions}
"""

    def _advanced_assessment_template(self) -> str:
        return """
Advanced repair analysis and optimization:

**Advanced Practitioner Assessment:**
- Complex Device: {device_type} {device_model}
- Advanced Challenge: {issue_description}
- Professional Setup: {available_tools}
- Expert Environment: {environment}

**Advanced Analysis Requirements:**

1. **Technical Innovation**
   - Novel repair approaches
   - Component substitution options
   - Performance optimization opportunities
   - Reliability improvement modifications

2. **Efficiency Optimization**
   - Time-saving techniques
   - Tool selection optimization
   - Workflow improvements
   - Quality assurance streamlining

3. **Knowledge Contribution**
   - Documentation for community
   - Technique refinement
   - Failure analysis contribution
   - Training material development

4. **Professional Standards**
   - Industry best practices
   - Regulatory compliance
   - Warranty considerations
   - Liability management

5. **Continuous Improvement**
   - Process refinement opportunities
   - Tool and technique evolution
   - Knowledge sharing platforms
   - Professional development

{custom_instructions}
"""

    def _quick_troubleshooting_template(self) -> str:
        return """
Quick troubleshooting for immediate issues:

**Rapid Problem Resolution:**
- Device: {device_type} {device_model}
- Urgent Issue: {issue_description}
- Time Constraint: {urgency}
- Quick Resources: {available_tools}

**Fast Troubleshooting Protocol:**

1. **Immediate Assessment** (2 minutes)
   - Obvious visual problems
   - Power and connection check
   - Basic function test
   - Safety hazard identification

2. **Quick Tests** (5 minutes)
   - Power cycle procedures
   - Connection verification
   - Basic setting checks
   - External factor elimination

3. **Common Fix Attempts** (10 minutes)
   - Known solutions for this device/issue
   - Simple cleaning procedures
   - Basic adjustments
   - Software resets

4. **Decision Point** (15 minutes total)
   - Continue with quick fixes
   - Escalate to systematic troubleshooting
   - Seek immediate professional help
   - Implement temporary workaround

5. **Rapid Documentation**
   - What worked/didn't work
   - Symptoms that changed
   - Next steps if current approach fails

{custom_instructions}
"""

    def _electrical_safety_template(self) -> str:
        return """
Electrical safety analysis for this repair:

**Electrical Safety Assessment:**
- Device: {device_type} {device_model}
- Electrical Work: {issue_description}
- User Experience: {user_skill_level}
- Work Environment: {environment}

**Electrical Hazard Analysis:**

1. **Power Source Hazards**
   - AC mains voltage exposure
   - High voltage components (CRT, flash, etc.)
   - Stored energy in capacitors
   - Battery hazards (thermal, chemical)

2. **Circuit Protection**
   - Proper disconnection procedures
   - Lockout/tagout requirements
   - Residual energy discharge
   - Circuit breaker/fuse considerations

3. **Personal Protection**
   - Insulated tools requirements
   - Personal protective equipment
   - Grounding and ESD protection
   - Safe work practices

4. **Environmental Factors**
   - Workspace electrical safety
   - Humidity and moisture concerns
   - Ground fault protection
   - Emergency power disconnection

5. **Emergency Procedures**
   - Electrical shock response
   - Fire suppression for electrical fires
   - Emergency contact procedures
   - First aid for electrical incidents

{custom_instructions}
"""

    def _mechanical_safety_template(self) -> str:
        return """
Mechanical safety analysis for this repair:

**Mechanical Safety Assessment:**
- Device: {device_type} {device_model}
- Mechanical Work: {issue_description}
- User Capability: {user_skill_level}
- Work Setting: {environment}

**Mechanical Hazard Analysis:**

1. **Tool Safety**
   - Sharp tool handling
   - Power tool precautions
   - Proper tool selection
   - Tool maintenance requirements

2. **Component Hazards**
   - Spring-loaded mechanisms
   - Sharp edges and small parts
   - Moving parts and pinch points
   - Pressure vessels or gas-filled components

3. **Material Handling**
   - Heavy component lifting
   - Fragile component protection
   - Chemical exposure (adhesives, solvents)
   - Dust and particle protection

4. **Workspace Safety**
   - Adequate lighting and space
   - Stable work surfaces
   - Organization to prevent accidents
   - Ventilation for fumes/dust

5. **Injury Prevention**
   - Cut and puncture prevention
   - Eye protection requirements
   - Repetitive strain considerations
   - Emergency first aid preparation

{custom_instructions}
"""

    def _functional_parts_template(self) -> str:
        return """
Identify parts by function and symptoms:

**Functional Parts Analysis:**
- Device: {device_type} {device_model}
- Functional Issue: {issue_description}
- Observed Symptoms: {symptoms}
- Functional Requirements: Based on {user_skill_level} analysis

**Functional Component Mapping:**

1. **Symptom-to-Component Analysis**
   - Which components could cause these symptoms
   - Primary vs secondary failure analysis
   - Component interaction effects
   - Failure mode probability ranking

2. **Functional Circuit Analysis**
   - Signal flow path components
   - Power distribution elements
   - Control and feedback systems
   - Protection and safety circuits

3. **Component Hierarchy**
   - Critical path components
   - Supporting components
   - Replaceable vs integrated parts
   - Cost-benefit analysis for replacement

4. **Testing Strategy**
   - How to test each suspected component
   - In-circuit vs out-of-circuit testing
   - Required test equipment
   - Go/no-go criteria for each test

5. **Replacement Planning**
   - Component availability
   - Compatibility requirements
   - Installation complexity
   - Testing after replacement

{custom_instructions}
"""


# Global template manager instance
template_manager = PromptTemplateManager()


def get_prompt_template_manager() -> PromptTemplateManager:
    """Get global prompt template manager"""
    return template_manager
