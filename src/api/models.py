"""
Pydantic models for RepairGPT API
Centralized data models for request/response validation
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DeviceType(str, Enum):
    """Supported device types"""

    NINTENDO_SWITCH = "nintendo_switch"
    NINTENDO_SWITCH_LITE = "nintendo_switch_lite"
    NINTENDO_SWITCH_OLED = "nintendo_switch_oled"
    IPHONE = "iphone"
    IPAD = "ipad"
    MACBOOK = "macbook"
    IMAC = "imac"
    PLAYSTATION_5 = "playstation_5"
    PLAYSTATION_4 = "playstation_4"
    XBOX_SERIES = "xbox_series"
    XBOX_ONE = "xbox_one"
    SAMSUNG_GALAXY = "samsung_galaxy"
    GOOGLE_PIXEL = "google_pixel"
    GAMING_PC = "gaming_pc"
    LAPTOP = "laptop"
    DESKTOP_PC = "desktop_pc"
    OTHER = "other"


class SkillLevel(str, Enum):
    """User skill levels"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class RepairUrgency(str, Enum):
    """Repair urgency levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RepairDifficulty(str, Enum):
    """Repair difficulty levels"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


# Diagnose API Models
class DiagnoseRequest(BaseModel):
    """Request model for device diagnosis"""

    device_type: DeviceType = Field(..., description="Type of device to diagnose")
    device_model: Optional[str] = Field(None, description="Specific model of the device")
    issue_description: str = Field(..., min_length=5, description="Description of the problem")
    symptoms: Optional[List[str]] = Field(default=[], description="Specific symptoms observed")
    skill_level: SkillLevel = Field(default=SkillLevel.BEGINNER, description="User's technical skill level")
    language: Optional[str] = Field(default="en", description="Response language (en/ja)")
    additional_context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context information")


class DiagnosisStep(BaseModel):
    """Individual diagnosis step"""

    step_number: int = Field(..., description="Step number in the diagnosis process")
    description: str = Field(..., description="Step description")
    expected_result: str = Field(..., description="What to expect from this step")
    warnings: Optional[List[str]] = Field(default=[], description="Safety warnings for this step")


class RepairRecommendation(BaseModel):
    """Repair recommendation"""

    title: str = Field(..., description="Repair recommendation title")
    description: str = Field(..., description="Detailed description")
    difficulty: RepairDifficulty = Field(..., description="Repair difficulty level")
    estimated_time: str = Field(..., description="Estimated time to complete")
    estimated_cost: Optional[str] = Field(None, description="Estimated cost range")
    success_rate: Optional[str] = Field(None, description="Success rate percentage")
    tools_required: List[str] = Field(default=[], description="Required tools")
    parts_required: List[str] = Field(default=[], description="Required parts")
    warnings: List[str] = Field(default=[], description="Important warnings")


class DiagnoseResponse(BaseModel):
    """Response model for device diagnosis"""

    diagnosis_id: str = Field(..., description="Unique diagnosis identifier")
    device_type: DeviceType = Field(..., description="Diagnosed device type")
    device_model: Optional[str] = Field(None, description="Device model")
    primary_issue: str = Field(..., description="Primary identified issue")
    possible_causes: List[str] = Field(..., description="Possible causes of the issue")
    severity: RepairUrgency = Field(..., description="Issue severity level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Diagnosis confidence (0.0-1.0)")

    # Diagnostic steps
    diagnostic_steps: List[DiagnosisStep] = Field(default=[], description="Recommended diagnostic steps")

    # Repair recommendations
    repair_recommendations: List[RepairRecommendation] = Field(default=[], description="Repair recommendations")

    # Professional help recommendation
    recommend_professional: bool = Field(default=False, description="Whether professional help is recommended")
    professional_reason: Optional[str] = Field(None, description="Reason for professional recommendation")

    # Additional information
    estimated_repair_time: Optional[str] = Field(None, description="Overall estimated repair time")
    estimated_total_cost: Optional[str] = Field(None, description="Overall estimated cost")
    preventive_measures: List[str] = Field(default=[], description="Preventive measures")

    language: str = Field(default="en", description="Response language")
    timestamp: str = Field(..., description="Diagnosis timestamp")


# Chat API Models (moved from routes.py)
class ChatRequest(BaseModel):
    """Chat request model"""

    message: str = Field(..., min_length=1, description="User message")
    device_type: Optional[DeviceType] = Field(None, description="Device type context")
    device_model: Optional[str] = Field(None, description="Device model context")
    issue_description: Optional[str] = Field(None, description="Issue description context")
    skill_level: SkillLevel = Field(default=SkillLevel.BEGINNER, description="User skill level")
    language: Optional[str] = Field(default="en", description="Response language")


class ChatResponse(BaseModel):
    """Chat response model"""

    response: str = Field(..., description="Bot response")
    language: str = Field(..., description="Response language")
    context: Dict[str, Any] = Field(..., description="Conversation context")


# Device Info Models
class DeviceInfo(BaseModel):
    """Device information model"""

    device_type: DeviceType = Field(..., description="Device type")
    device_model: Optional[str] = Field(None, description="Device model")
    issue_description: Optional[str] = Field(None, description="Issue description")
    skill_level: SkillLevel = Field(default=SkillLevel.BEGINNER, description="User skill level")


# Repair Guide Models
class RepairGuideStep(BaseModel):
    """Individual repair guide step"""

    step_number: int = Field(..., description="Step number")
    title: str = Field(..., description="Step title")
    description: str = Field(..., description="Step description")
    image_url: Optional[str] = Field(None, description="Step image URL")
    video_url: Optional[str] = Field(None, description="Step video URL")
    tools_needed: List[str] = Field(default=[], description="Tools needed for this step")
    warnings: List[str] = Field(default=[], description="Safety warnings")
    tips: List[str] = Field(default=[], description="Helpful tips")


class RepairGuide(BaseModel):
    """Repair guide model"""

    id: str = Field(..., description="Guide ID")
    title: str = Field(..., description="Guide title")
    device_type: DeviceType = Field(..., description="Target device type")
    device_model: Optional[str] = Field(None, description="Specific device model")
    difficulty: RepairDifficulty = Field(..., description="Repair difficulty")
    time_estimate: str = Field(..., description="Estimated completion time")
    cost_estimate: Optional[str] = Field(None, description="Estimated cost")
    success_rate: Optional[str] = Field(None, description="Success rate")
    summary: Optional[str] = Field(None, description="Guide summary")
    tools_required: List[str] = Field(..., description="Required tools")
    parts_required: List[str] = Field(..., description="Required parts")
    warnings: List[str] = Field(..., description="Important warnings")
    steps: List[RepairGuideStep] = Field(..., description="Repair steps")
    tips: List[str] = Field(default=[], description="General tips")


# Health Check Models
class HealthResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    language: str = Field(..., description="Response language")
    version: str = Field(..., description="API version")


# Error Models
class ErrorResponse(BaseModel):
    """Error response model"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: str = Field(..., description="Error timestamp")
