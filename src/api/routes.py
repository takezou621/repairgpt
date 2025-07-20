"""
API routes for RepairGPT with internationalization and security support
Implements Issue #90: 🔒 設定管理とセキュリティ強化
"""

import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, validator

from ..config.settings import settings
from ..utils.security import (
    create_audit_log,
    get_client_ip,
    sanitize_filename,
    sanitize_input,
    validate_content_type,
    validate_image_content,
)
from . import get_localized_error, get_localized_response

logger = logging.getLogger(__name__)


# Auth Models
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    language: Optional[str] = "en"

    @validator("username")
    def validate_username(cls, v):
        if not v or len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return sanitize_input(v, max_length=50)

    @validator("email")
    def validate_email(cls, v):
        import re

        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, v):
            raise ValueError("Invalid email format")
        return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    expires_in: int


# Request/Response models with security validation
class ChatRequest(BaseModel):
    message: str
    device_type: Optional[str] = None
    device_model: Optional[str] = None
    issue_description: Optional[str] = None
    skill_level: Optional[str] = "beginner"
    language: Optional[str] = "en"

    @validator("message")
    def validate_message(cls, v):
        """Validate and sanitize chat message"""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return sanitize_input(v, max_length=settings.max_text_length)

    @validator("device_type", "device_model", "issue_description")
    def validate_text_fields(cls, v):
        """Validate and sanitize text fields"""
        if v:
            return sanitize_input(v, max_length=500)
        return v

    @validator("skill_level")
    def validate_skill_level(cls, v):
        """Validate skill level"""
        allowed_levels = ["beginner", "intermediate", "expert"]
        if v not in allowed_levels:
            raise ValueError(f"Skill level must be one of: {allowed_levels}")
        return v

    @validator("language")
    def validate_language(cls, v):
        """Validate language"""
        if v not in settings.supported_languages:
            raise ValueError(f"Language must be one of: {settings.supported_languages}")
        return v


class ChatResponse(BaseModel):
    response: str
    language: str
    context: Dict[str, Any]


class DeviceInfo(BaseModel):
    device_type: str
    device_model: Optional[str] = None
    issue_description: Optional[str] = None
    skill_level: str = "beginner"


class RepairGuide(BaseModel):
    id: str
    title: str
    difficulty: str
    time_estimate: str
    cost_estimate: str
    success_rate: str
    device: str
    summary: Optional[str] = None
    tools_required: List[str]
    parts_required: List[str]
    warnings: List[str]
    steps: List[Dict[str, Any]]
    tips: List[str]


class HealthResponse(BaseModel):
    status: str
    message: str
    language: str
    version: str


# Create router
router = APIRouter()


# Auth endpoints
@router.post("/auth/register", response_model=AuthResponse)
async def register_user(register_request: RegisterRequest, request: Request):
    """Register a new user"""
    try:
        from ..auto_feature_60 import AuthenticationFeature

        auth_feature = AuthenticationFeature()
        result = await auth_feature.register_user(
            email=register_request.email,
            password=register_request.password,
            language=register_request.language,
            username=register_request.username,
        )

        if result["success"]:
            return AuthResponse(
                access_token=result["token"]["access_token"],
                user_id=result["user"]["user_id"],
                username=result["user"]["username"],
                expires_in=3600,
            )
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/login", response_model=AuthResponse)
async def login_user(login_request: LoginRequest, request: Request):
    """Login user"""
    try:
        from ..auto_feature_60 import AuthenticationFeature

        auth_feature = AuthenticationFeature()
        result = await auth_feature.login_user(
            email=login_request.username,  # Use username as email for now
            password=login_request.password,
        )

        if result["success"]:
            return AuthResponse(
                access_token=result["token"]["access_token"],
                user_id=result["user"]["user_id"],
                username=result["user"]["username"],
                expires_in=3600,
            )
        else:
            raise HTTPException(status_code=401, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/me")
async def get_current_user(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    """Get current user information"""
    try:
        from ..auto_feature_60 import AuthenticationFeature

        auth_feature = AuthenticationFeature()
        result = await auth_feature.verify_token(credentials.credentials)

        if result["success"]:
            return {"user": result["user"]}
        else:
            raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check endpoint with localized response"""
    return HealthResponse(
        status="healthy",
        message=request.state.i18n.translate(
            "api.health.message", request.state.language
        ),
        language=request.state.language,
        version="1.0.0",
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest, request: Request):
    """Chat endpoint for repair assistance with security logging"""
    # Create audit log
    client_ip = get_client_ip(request)
    audit_entry = create_audit_log(
        action="chat_request",
        ip_address=client_ip,
        details={
            "device_type": chat_request.device_type,
            "skill_level": chat_request.skill_level,
            "language": chat_request.language,
            "message_length": len(chat_request.message),
        },
    )
    logger.info(f"Chat request: {audit_entry}")

    try:
        # Import here to avoid circular imports
        from ..chat.llm_chatbot import RepairChatbot

        # Initialize chatbot
        chatbot = RepairChatbot(preferred_model="auto")

        # Update context if provided
        if chat_request.device_type:
            chatbot.update_context(
                device_type=chat_request.device_type,
                device_model=chat_request.device_model,
                issue_description=chat_request.issue_description,
                user_skill_level=chat_request.skill_level,
            )

        # Get response
        response = chatbot.chat(chat_request.message)

        return ChatResponse(
            response=response,
            language=request.state.language,
            context={
                "device_type": chat_request.device_type,
                "device_model": chat_request.device_model,
                "issue_description": chat_request.issue_description,
                "skill_level": chat_request.skill_level,
            },
        )

    except Exception as e:
        raise get_localized_error(
            request, "api.errors.chat_failed", status_code=500, error=str(e)
        )


@router.get("/devices")
async def get_supported_devices(request: Request):
    """Get list of supported devices in the current language"""
    language = request.state.language
    i18n = request.state.i18n

    devices = [
        "nintendo_switch",
        "nintendo_switch_lite",
        "nintendo_switch_oled",
        "iphone",
        "ipad",
        "macbook",
        "imac",
        "playstation_5",
        "playstation_4",
        "xbox_series",
        "xbox_one",
        "samsung_galaxy",
        "google_pixel",
        "gaming_pc",
        "laptop",
        "desktop_pc",
        "other",
    ]

    localized_devices = {}
    for device in devices:
        localized_devices[device] = i18n.translate(f"devices.{device}", language)

    return get_localized_response(
        request, "api.devices.success", devices=localized_devices, count=len(devices)
    )


@router.get("/skill-levels")
async def get_skill_levels(request: Request):
    """Get available skill levels in the current language"""
    language = request.state.language
    i18n = request.state.i18n

    skill_levels = ["beginner", "intermediate", "expert"]

    localized_levels = {}
    for level in skill_levels:
        localized_levels[level] = i18n.translate(f"skill_levels.{level}", language)

    return get_localized_response(
        request,
        "api.skill_levels.success",
        skill_levels=localized_levels,
        count=len(skill_levels),
    )


@router.get("/guides/search")
async def search_repair_guides(
    request: Request,
    device_type: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 10,
):
    """Search for repair guides"""
    try:
        # Import here to avoid circular imports
        from ..clients.ifixit_client import IFixitClient
        from ..data.offline_repair_database import OfflineRepairDatabase

        # Initialize clients
        offline_db = OfflineRepairDatabase()
        ifixit_client = IFixitClient()

        guides = []

        # Search offline database first
        if query:
            offline_guides = offline_db.search_guides(
                query, device_type, limit=limit // 2
            )
            guides.extend([guide.__dict__ for guide in offline_guides])

        # Search iFixit if we have fewer than limit guides
        if len(guides) < limit and query:
            try:
                online_guides = ifixit_client.search_guides(
                    query, limit=limit - len(guides)
                )
                guides.extend([guide.__dict__ for guide in online_guides])
            except Exception:
                # Online search failed, continue with offline results
                pass

        return get_localized_response(
            request,
            "api.guides.search_success",
            guides=guides[:limit],
            count=len(guides[:limit]),
            query=query,
            device_type=device_type,
        )

    except Exception as e:
        raise get_localized_error(
            request, "api.errors.search_failed", status_code=500, error=str(e)
        )


@router.get("/languages")
async def get_supported_languages(request: Request):
    """Get list of supported languages"""
    languages = {"en": "English 🇺🇸", "ja": "日本語 🇯🇵"}

    return get_localized_response(
        request,
        "api.languages.success",
        languages=languages,
        current_language=request.state.language,
    )


@router.post("/analyze-image")
async def analyze_device_image(
    request: Request,
    file: UploadFile = File(...),
    language: Optional[str] = "en",
    context: Optional[str] = None,
):
    """
    Analyze device image for diagnosis

    Upload an image of a device for AI-powered damage assessment and
    repair recommendations. Supports JPG, PNG, and WebP formats up to 10MB.
    """
    try:
        # Import analysis models and service
        from ..schemas.image_analysis import (
            DamageAssessmentResponse,
            DeviceInfoResponse,
            ImageAnalysisResponse,
        )
        from ..services.image_analysis import ImageAnalysisService

        # Validate filename
        if file.filename:
            sanitize_filename(file.filename)

        # Validate file type
        allowed_types = [f"image/{ext}" for ext in settings.allowed_file_types]
        if not file.content_type or not validate_content_type(
            file.content_type, allowed_types
        ):
            logger.warning(f"Invalid file type uploaded: {file.content_type}")
            raise get_localized_error(
                request,
                "api.errors.invalid_file_type",
                status_code=400,
                error_code="INVALID_FILE_TYPE",
                allowed_types=list(settings.allowed_file_types),
            )

        # Read and validate file content
        content = await file.read()
        file_size = len(content)
        max_size = settings.max_image_size_mb * 1024 * 1024

        if file_size > max_size:
            logger.warning(f"File too large uploaded: {file_size} bytes")
            raise get_localized_error(
                request,
                "api.errors.file_too_large",
                status_code=400,
                error_code="FILE_TOO_LARGE",
                max_size_mb=settings.max_image_size_mb,
            )

        # Validate image content for security
        image_validation = validate_image_content(content, max_size)
        if not image_validation["valid"]:
            logger.warning(f"Invalid image content: {image_validation['error']}")
            raise get_localized_error(
                request,
                "api.errors.invalid_image_content",
                status_code=400,
                error_code="INVALID_IMAGE_CONTENT",
                error=image_validation["error"],
            )

        # Log warnings if any
        for warning in image_validation.get("warnings", []):
            logger.warning(f"Image security warning: {warning}")

        # Parse context if provided
        if context:
            try:
                json.loads(context)
            except json.JSONDecodeError:
                pass

        # Initialize image analysis service with secure configuration
        if not settings.openai_api_key:
            logger.error("OpenAI API key not configured")
            raise get_localized_error(
                request,
                "api.errors.service_unavailable",
                status_code=503,
                error_code="API_KEY_MISSING",
                service="OpenAI",
            )

        analysis_service = ImageAnalysisService(
            provider="openai", api_key=settings.openai_api_key
        )

        # Perform analysis
        result = await analysis_service.analyze_device_image(
            image_data=content, language=language or request.state.language
        )

        # Convert to response format
        device_info_response = DeviceInfoResponse(
            device_type=result.device_info.device_type.value,
            brand=result.device_info.brand,
            model=result.device_info.model,
            confidence=result.device_info.confidence,
        )

        damage_responses = [
            DamageAssessmentResponse(
                damage_type=damage.damage_type.value,
                confidence=damage.confidence,
                severity=damage.severity,
                location=damage.location,
                description=damage.description,
            )
            for damage in result.damage_detected
        ]

        analysis_response = ImageAnalysisResponse(
            device_info=device_info_response,
            damage_detected=damage_responses,
            overall_condition=result.overall_condition,
            repair_urgency=result.repair_urgency,
            estimated_repair_cost=result.estimated_repair_cost,
            repair_difficulty=result.repair_difficulty,
            analysis_confidence=result.analysis_confidence,
            recommended_actions=result.recommended_actions,
            warnings=result.warnings,
            language=result.language,
        )

        return get_localized_response(
            request,
            "api.image_analysis.success",
            analysis=analysis_response.dict(),
            file_name=file.filename,
            file_size=file_size,
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise get_localized_error(
            request,
            "api.errors.analysis_failed",
            status_code=500,
            error_code="ANALYSIS_FAILED",
            error=str(e),
        )


# Additional diagnosis models for the diagnose endpoint


class DiagnoseRequest(BaseModel):
    device_type: str
    device_model: Optional[str] = None
    issue_description: str
    symptoms: Optional[List[str]] = None
    skill_level: str = "beginner"
    language: Optional[str] = "en"

    @validator("device_type", "issue_description")
    def validate_required_fields(cls, v):
        """Validate required text fields"""
        if v:
            return sanitize_input(v, max_length=500)
        return v

    @validator("symptoms")
    def validate_symptoms(cls, v):
        """Validate and sanitize symptoms list"""
        if v:
            return [sanitize_input(symptom, max_length=200) for symptom in v[:10]]
        return v


class DiagnosisStep(BaseModel):
    step_number: int
    description: str
    expected_result: str
    warnings: Optional[List[str]] = None


class RepairRecommendation(BaseModel):
    title: str
    description: str
    difficulty: str
    estimated_time: str
    estimated_cost: str
    success_rate: str
    tools_required: List[str]
    parts_required: List[str]
    warnings: List[str]


class DiagnoseResponse(BaseModel):
    diagnosis_id: str
    device_type: str
    device_model: Optional[str] = None
    primary_issue: str
    possible_causes: List[str]
    severity: str
    confidence: float
    diagnostic_steps: List[DiagnosisStep]
    repair_recommendations: List[RepairRecommendation]
    recommend_professional: bool
    professional_reason: Optional[str] = None
    estimated_repair_time: str
    estimated_total_cost: str
    preventive_measures: List[str]
    language: str
    timestamp: str


@router.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose_device(diagnose_request: DiagnoseRequest, request: Request):
    """
    Diagnose device issues and provide repair recommendations with security logging

    This endpoint analyzes device problems and provides structured diagnosis results
    including possible causes, diagnostic steps, and repair recommendations.
    """
    # Create audit log for diagnosis request
    client_ip = get_client_ip(request)
    audit_entry = create_audit_log(
        action="diagnosis_request",
        ip_address=client_ip,
        details={
            "device_type": diagnose_request.device_type,
            "skill_level": diagnose_request.skill_level,
            "language": diagnose_request.language,
            "issue_length": len(diagnose_request.issue_description),
            "has_symptoms": bool(diagnose_request.symptoms),
        },
    )
    logger.info(f"Diagnosis request: {audit_entry}")

    try:
        import uuid
        from datetime import datetime

        # Import here to avoid circular imports
        from ..chat.llm_chatbot import RepairChatbot

        # Generate unique diagnosis ID
        diagnosis_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Initialize chatbot with context
        chatbot = RepairChatbot(preferred_model="auto")

        # Update chatbot context
        chatbot.update_context(
            device_type=diagnose_request.device_type,
            device_model=diagnose_request.device_model,
            issue_description=diagnose_request.issue_description,
            user_skill_level=diagnose_request.skill_level,
        )

        # Create diagnosis prompt
        diagnosis_prompt = f"""
        Please provide a structured diagnosis for the following device issue:
        
        Device: {diagnose_request.device_type} {diagnose_request.device_model or ''}
        Issue: {diagnose_request.issue_description}
        Symptoms: {', '.join(diagnose_request.symptoms) if diagnose_request.symptoms else 'None specified'}
        User Skill Level: {diagnose_request.skill_level}
        
        Please provide:
        1. Primary issue identification
        2. Possible causes (list)
        3. Severity assessment
        4. Diagnostic steps to confirm the issue
        5. Repair recommendations with difficulty levels
        6. Whether professional help is recommended
        7. Estimated time and cost if possible
        8. Preventive measures
        
        Format your response clearly and focus on safety and accuracy.
        """

        # Get diagnosis from chatbot
        raw_response = chatbot.chat(diagnosis_prompt)

        # Determine severity based on keywords
        severity = "medium"
        if any(
            word in diagnose_request.issue_description.lower()
            for word in ["broken", "dead", "won't turn on", "completely"]
        ):
            severity = "high"
        elif any(
            word in diagnose_request.issue_description.lower()
            for word in ["slow", "minor", "sometimes", "occasional"]
        ):
            severity = "low"

        # Determine if professional help is recommended
        recommend_professional = False
        professional_reason = None
        if diagnose_request.skill_level == "beginner" and severity in [
            "high",
            "critical",
        ]:
            recommend_professional = True
            professional_reason = "Complex repair requiring advanced technical skills and specialized tools"

        # Create basic diagnostic steps
        diagnostic_steps = [
            DiagnosisStep(
                step_number=1,
                description="Visual inspection of the device for obvious damage",
                expected_result="Identify any visible cracks, damage, or loose components",
                warnings=[
                    "Ensure device is powered off",
                    "Handle with care to avoid further damage",
                ],
            ),
            DiagnosisStep(
                step_number=2,
                description="Check power connections and charging cables",
                expected_result="Verify power delivery to the device",
                warnings=["Use only official chargers", "Check for frayed cables"],
            ),
        ]

        # Create repair recommendation
        repair_recommendations = [
            RepairRecommendation(
                title="Initial Troubleshooting",
                description=(
                    raw_response[:500] + "..."
                    if len(raw_response) > 500
                    else raw_response
                ),
                difficulty=(
                    "easy" if diagnose_request.skill_level != "beginner" else "medium"
                ),
                estimated_time="30-60 minutes",
                estimated_cost="$0-50",
                success_rate="70-85%",
                tools_required=["Screwdriver set", "Multimeter (optional)"],
                parts_required=["Replacement parts may be needed after diagnosis"],
                warnings=[
                    "Always power off device before opening",
                    "Work in anti-static environment",
                ],
            )
        ]

        # Determine confidence based on issue description specificity
        confidence = 0.8 if len(diagnose_request.issue_description) > 20 else 0.6
        if diagnose_request.symptoms:
            confidence += 0.1
        confidence = min(confidence, 1.0)

        return DiagnoseResponse(
            diagnosis_id=diagnosis_id,
            device_type=diagnose_request.device_type,
            device_model=diagnose_request.device_model,
            primary_issue=diagnose_request.issue_description,
            possible_causes=[
                "Hardware failure",
                "Software malfunction",
                "Power supply issues",
                "Component wear and tear",
            ],
            severity=severity,
            confidence=confidence,
            diagnostic_steps=diagnostic_steps,
            repair_recommendations=repair_recommendations,
            recommend_professional=recommend_professional,
            professional_reason=professional_reason,
            estimated_repair_time="1-3 hours",
            estimated_total_cost="$20-100",
            preventive_measures=[
                "Regular cleaning and maintenance",
                "Proper storage when not in use",
                "Avoid exposure to extreme temperatures",
                "Use protective cases when applicable",
            ],
            language=diagnose_request.language or request.state.language,
            timestamp=timestamp,
        )

    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        raise get_localized_error(
            request, "api.errors.diagnosis_failed", status_code=500, error=str(e)
        )
