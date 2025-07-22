"""
Diagnose API routes for device diagnostics
"""

import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, validator

from ...config.settings_simple import settings
from ...utils.security import create_audit_log, get_client_ip, sanitize_input

diagnose_router = APIRouter(prefix="/diagnose", tags=["Diagnose"])


class DiagnoseRequest(BaseModel):
    device_type: str
    issue_description: str
    device_model: Optional[str] = None
    symptoms: Optional[List[str]] = None
    skill_level: str = "beginner"
    language: str = "en"

    @validator("device_type", "issue_description")
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return sanitize_input(v, max_length=500)

    @validator("device_model")
    def validate_device_model(cls, v):
        if v:
            return sanitize_input(v, max_length=100)
        return v

    @validator("symptoms")
    def validate_symptoms(cls, v):
        if v:
            return [sanitize_input(symptom, max_length=200) for symptom in v[:10]]
        return v

    @validator("skill_level")
    def validate_skill_level(cls, v):
        allowed_levels = ["beginner", "intermediate", "expert"]
        if v not in allowed_levels:
            raise ValueError(f"Skill level must be one of: {allowed_levels}")
        return v

    @validator("language")
    def validate_language(cls, v):
        if v not in settings.supported_languages:
            raise ValueError(f"Language must be one of: {settings.supported_languages}")
        return v


class DiagnoseResponse(BaseModel):
    diagnosis: str
    confidence: float
    possible_causes: List[str]
    recommended_actions: List[str]
    safety_warnings: List[str]
    required_tools: List[str]
    estimated_difficulty: str
    estimated_time: str
    success_rate: str
    professional_help_recommended: bool
    language: str


def _generate_mock_diagnosis(request: DiagnoseRequest) -> Dict[str, Any]:
    """Generate mock diagnosis response"""
    time.sleep(0.8)  # Simulate processing time
    
    device_lower = request.device_type.lower()
    issue_lower = request.issue_description.lower()
    
    # Device-specific diagnoses
    if "nintendo" in device_lower or "switch" in device_lower:
        if "drift" in issue_lower or "joy-con" in issue_lower:
            return {
                "diagnosis": "Joy-Con analog stick drift detected",
                "confidence": 0.85,
                "possible_causes": [
                    "Worn analog stick mechanism",
                    "Dust or debris buildup under the stick",
                    "Electrical contact degradation",
                    "Manufacturing defect"
                ],
                "recommended_actions": [
                    "Try recalibrating the Joy-Con in System Settings",
                    "Clean around the analog stick with compressed air",
                    "Apply electrical contact cleaner (advanced users)",
                    "Replace the analog stick module",
                    "Contact Nintendo for warranty service"
                ],
                "safety_warnings": [
                    "Power off the device before any physical repairs",
                    "Use proper tools to avoid damage",
                    "Be careful with ribbon cables"
                ],
                "required_tools": [
                    "Y00 Tripoint screwdriver",
                    "Plastic prying tools",
                    "Compressed air",
                    "Electrical contact cleaner (optional)"
                ],
                "estimated_difficulty": "Easy to Moderate",
                "estimated_time": "10-45 minutes",
                "success_rate": "70-95%",
                "professional_help_recommended": request.skill_level == "beginner"
            }
    
    elif "iphone" in device_lower or "phone" in device_lower:
        if "screen" in issue_lower or "cracked" in issue_lower or "display" in issue_lower:
            return {
                "diagnosis": "Display assembly damage detected",
                "confidence": 0.90,
                "possible_causes": [
                    "Physical impact damage",
                    "Pressure damage",
                    "Manufacturing defect",
                    "Water damage affecting display"
                ],
                "recommended_actions": [
                    "Back up your data immediately",
                    "Check if touch functionality still works",
                    "Assess LCD damage (black spots, lines)",
                    "Replace the display assembly",
                    "Visit Apple Store or authorized repair center"
                ],
                "safety_warnings": [
                    "Sharp glass fragments - handle with care",
                    "Disconnect battery before repair",
                    "May affect Face ID functionality",
                    "Water resistance will be compromised"
                ],
                "required_tools": [
                    "Pentalobe screwdrivers",
                    "Plastic picks and spudgers",
                    "Suction cups",
                    "Display assembly replacement",
                    "Waterproof adhesive"
                ],
                "estimated_difficulty": "Moderate to Hard",
                "estimated_time": "45-90 minutes",
                "success_rate": "80-95%",
                "professional_help_recommended": request.skill_level != "expert"
            }
        elif "battery" in issue_lower:
            return {
                "diagnosis": "Battery degradation or failure suspected",
                "confidence": 0.75,
                "possible_causes": [
                    "Normal battery aging",
                    "Excessive heat exposure",
                    "Charging circuit malfunction",
                    "Software issues causing drain"
                ],
                "recommended_actions": [
                    "Check battery health in Settings",
                    "Update to latest iOS version",
                    "Reset all settings",
                    "Replace battery if health below 80%",
                    "Check for swelling (stop use immediately if found)"
                ],
                "safety_warnings": [
                    "Never puncture the battery",
                    "Stop using if battery is swollen",
                    "Use only genuine replacement parts",
                    "Dispose of old battery properly"
                ],
                "required_tools": [
                    "Pentalobe screwdrivers",
                    "Y000 Tripoint screwdriver",
                    "Plastic opening tools",
                    "Battery adhesive strips",
                    "New battery"
                ],
                "estimated_difficulty": "Moderate",
                "estimated_time": "30-60 minutes",
                "success_rate": "85-95%",
                "professional_help_recommended": request.skill_level == "beginner"
            }
    
    # Generic diagnosis
    return {
        "diagnosis": f"General issue with {request.device_type}",
        "confidence": 0.60,
        "possible_causes": [
            "Hardware component failure",
            "Software/firmware issues",
            "Physical damage",
            "Environmental factors"
        ],
        "recommended_actions": [
            "Perform basic troubleshooting",
            "Check for software updates",
            "Inspect for visible damage",
            "Test in safe mode if applicable",
            "Consult repair manual or guides"
        ],
        "safety_warnings": [
            "Always power off before repairs",
            "Use proper tools",
            "Work in a clean environment",
            "Take photos before disassembly"
        ],
        "required_tools": [
            "Appropriate screwdrivers",
            "Plastic opening tools",
            "Anti-static mat",
            "Good lighting"
        ],
        "estimated_difficulty": "Varies",
        "estimated_time": "30-120 minutes",
        "success_rate": "Depends on issue",
        "professional_help_recommended": True
    }


@diagnose_router.post("", response_model=DiagnoseResponse)
async def diagnose_endpoint(diagnose_request: DiagnoseRequest, request: Request):
    """Diagnose endpoint for device issues with mock support"""
    # Create audit log
    client_ip = get_client_ip(request)
    create_audit_log(
        action="diagnose_request",
        ip_address=client_ip,
        details={
            "device_type": diagnose_request.device_type,
            "skill_level": diagnose_request.skill_level,
            "language": diagnose_request.language,
            "issue_length": len(diagnose_request.issue_description),
        },
    )

    # Check if we should use mock mode
    use_mock = settings.should_use_mock_ai()
    
    if use_mock:
        # Generate mock diagnosis
        diagnosis_data = _generate_mock_diagnosis(diagnose_request)
        
        return DiagnoseResponse(
            **diagnosis_data,
            language=getattr(request.state, "language", diagnose_request.language)
        )
    else:
        # Use real AI for diagnosis (future implementation)
        # For now, return mock data
        diagnosis_data = _generate_mock_diagnosis(diagnose_request)
        
        return DiagnoseResponse(
            **diagnosis_data,
            language=getattr(request.state, "language", diagnose_request.language)
        )