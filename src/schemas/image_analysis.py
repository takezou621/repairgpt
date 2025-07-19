"""
Pydantic models for image analysis API
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DamageTypeEnum(str, Enum):
    """Types of damage that can be detected"""

    SCREEN_CRACK = "screen_crack"
    LIQUID_DAMAGE = "liquid_damage"
    PHYSICAL_DAMAGE = "physical_damage"
    BUTTON_DAMAGE = "button_damage"
    PORT_DAMAGE = "port_damage"
    BATTERY_SWELLING = "battery_swelling"
    CORROSION = "corrosion"
    SCRATCHES = "scratches"
    DENTS = "dents"
    MISSING_PARTS = "missing_parts"


class DeviceTypeEnum(str, Enum):
    """Types of devices that can be analyzed"""

    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    GAMING_CONSOLE = "gaming_console"
    SMARTWATCH = "smartwatch"
    HEADPHONES = "headphones"
    OTHER = "other"


class ImageAnalysisRequest(BaseModel):
    """Request model for image analysis"""

    language: Optional[str] = Field(
        default="en", description="Analysis language (en/ja)"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional context"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "language": "en",
                "context": {
                    "device_type": "smartphone",
                    "user_skill_level": "beginner",
                },
            }
        }


class DamageAssessmentResponse(BaseModel):
    """Response model for detected damage"""

    damage_type: DamageTypeEnum = Field(description="Type of damage detected")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0-1)")
    severity: str = Field(description="Damage severity (low/medium/high/critical)")
    location: Optional[str] = Field(default=None, description="Location of damage")
    description: str = Field(description="Human-readable description")

    class Config:
        json_schema_extra = {
            "example": {
                "damage_type": "screen_crack",
                "confidence": 0.92,
                "severity": "high",
                "location": "upper left corner",
                "description": "Large crack extending across screen",
            }
        }


class DeviceInfoResponse(BaseModel):
    """Response model for device information"""

    device_type: DeviceTypeEnum = Field(description="Type of device")
    brand: Optional[str] = Field(default=None, description="Device brand")
    model: Optional[str] = Field(default=None, description="Device model")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "device_type": "smartphone",
                "brand": "Apple",
                "model": "iPhone 14 Pro",
                "confidence": 0.89,
            }
        }


class ImageAnalysisResponse(BaseModel):
    """Complete image analysis response"""

    device_info: DeviceInfoResponse = Field(description="Detected device information")
    damage_detected: List[DamageAssessmentResponse] = Field(
        description="List of detected damages"
    )
    overall_condition: str = Field(description="Overall device condition")
    repair_urgency: str = Field(description="Repair urgency level")
    estimated_repair_cost: Optional[str] = Field(
        default=None, description="Estimated repair cost"
    )
    repair_difficulty: Optional[str] = Field(
        default=None, description="Repair difficulty level"
    )
    analysis_confidence: float = Field(
        ge=0.0, le=1.0, description="Overall analysis confidence"
    )
    recommended_actions: List[str] = Field(description="Recommended next steps")
    warnings: List[str] = Field(description="Safety warnings and alerts")
    language: str = Field(description="Response language")

    class Config:
        json_schema_extra = {
            "example": {
                "device_info": {
                    "device_type": "smartphone",
                    "brand": "Apple",
                    "model": "iPhone 14 Pro",
                    "confidence": 0.89,
                },
                "damage_detected": [
                    {
                        "damage_type": "screen_crack",
                        "confidence": 0.92,
                        "severity": "high",
                        "location": "upper left corner",
                        "description": "Large crack extending across screen",
                    }
                ],
                "overall_condition": "fair",
                "repair_urgency": "medium",
                "estimated_repair_cost": "$150-250",
                "repair_difficulty": "intermediate",
                "analysis_confidence": 0.85,
                "recommended_actions": [
                    "Schedule screen replacement",
                    "Backup data immediately",
                    "Avoid water exposure",
                ],
                "warnings": ["Crack may worsen with continued use"],
                "language": "en",
            }
        }


class ImageAnalysisError(BaseModel):
    """Error response for image analysis"""

    error: str = Field(description="Error message")
    error_code: str = Field(description="Error code")
    language: str = Field(description="Response language")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Image file too large",
                "error_code": "FILE_TOO_LARGE",
                "language": "en",
            }
        }
