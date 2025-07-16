"""
API routes for RepairGPT with internationalization support
"""

from fastapi import APIRouter, Request, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import logging

from . import get_localized_response, get_localized_error

logger = logging.getLogger(__name__)


# Import models from centralized models file
from .models import (
    ChatRequest, ChatResponse, DeviceInfo, RepairGuide, HealthResponse,
    DiagnoseRequest, DiagnoseResponse, DiagnosisStep, RepairRecommendation,
    DeviceType, SkillLevel, RepairUrgency, RepairDifficulty
)


# Create router
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check endpoint with localized response"""
    return HealthResponse(
        status="healthy",
        message=request.state.i18n.translate("api.health.message", request.state.language),
        language=request.state.language,
        version="1.0.0"
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest, request: Request):
    """Chat endpoint for repair assistance"""
    try:
        # Import here to avoid circular imports
        from ..chat.llm_chatbot import RepairChatbot
        
        # Initialize chatbot
        chatbot = RepairChatbot(preferred_model="auto")
        
        # Update context if provided
        if chat_request.device_type:
            chatbot.update_context(
                device_type=chat_request.device_type.value if hasattr(chat_request.device_type, 'value') else chat_request.device_type,
                device_model=chat_request.device_model,
                issue_description=chat_request.issue_description,
                user_skill_level=chat_request.skill_level.value if hasattr(chat_request.skill_level, 'value') else chat_request.skill_level
            )
        
        # Get response
        response = chatbot.chat(chat_request.message)
        
        return ChatResponse(
            response=response,
            language=request.state.language,
            context={
                "device_type": chat_request.device_type.value if hasattr(chat_request.device_type, 'value') else chat_request.device_type,
                "device_model": chat_request.device_model,
                "issue_description": chat_request.issue_description,
                "skill_level": chat_request.skill_level.value if hasattr(chat_request.skill_level, 'value') else chat_request.skill_level
            }
        )
    
    except Exception as e:
        raise get_localized_error(
            request, 
            "api.errors.chat_failed", 
            status_code=500,
            error=str(e)
        )


@router.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose_device(diagnose_request: DiagnoseRequest, request: Request):
    """
    Diagnose device issues and provide repair recommendations
    
    This endpoint analyzes device problems and provides structured diagnosis results
    including possible causes, diagnostic steps, and repair recommendations.
    """
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
            device_type=diagnose_request.device_type.value,
            device_model=diagnose_request.device_model,
            issue_description=diagnose_request.issue_description,
            user_skill_level=diagnose_request.skill_level.value
        )
        
        # Create diagnosis prompt
        diagnosis_prompt = f"""
        Please provide a structured diagnosis for the following device issue:
        
        Device: {diagnose_request.device_type.value} {diagnose_request.device_model or ''}
        Issue: {diagnose_request.issue_description}
        Symptoms: {', '.join(diagnose_request.symptoms) if diagnose_request.symptoms else 'None specified'}
        User Skill Level: {diagnose_request.skill_level.value}
        
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
        
        # Parse and structure the response (simplified implementation)
        # In a production system, you might use more sophisticated NLP parsing
        
        # Determine severity based on keywords
        severity = RepairUrgency.MEDIUM
        if any(word in diagnose_request.issue_description.lower() for word in ['broken', 'dead', 'won\'t turn on', 'completely']):
            severity = RepairUrgency.HIGH
        elif any(word in diagnose_request.issue_description.lower() for word in ['slow', 'minor', 'sometimes', 'occasional']):
            severity = RepairUrgency.LOW
        
        # Determine if professional help is recommended
        recommend_professional = False
        professional_reason = None
        if diagnose_request.skill_level == SkillLevel.BEGINNER and severity in [RepairUrgency.HIGH, RepairUrgency.CRITICAL]:
            recommend_professional = True
            professional_reason = "Complex repair requiring advanced technical skills and specialized tools"
        
        # Create basic diagnostic steps
        diagnostic_steps = [
            DiagnosisStep(
                step_number=1,
                description="Visual inspection of the device for obvious damage",
                expected_result="Identify any visible cracks, damage, or loose components",
                warnings=["Ensure device is powered off", "Handle with care to avoid further damage"]
            ),
            DiagnosisStep(
                step_number=2,
                description="Check power connections and charging cables",
                expected_result="Verify power delivery to the device",
                warnings=["Use only official chargers", "Check for frayed cables"]
            )
        ]
        
        # Create repair recommendation
        repair_recommendations = [
            RepairRecommendation(
                title="Initial Troubleshooting",
                description=raw_response[:500] + "..." if len(raw_response) > 500 else raw_response,
                difficulty=RepairDifficulty.EASY if diagnose_request.skill_level != SkillLevel.BEGINNER else RepairDifficulty.MEDIUM,
                estimated_time="30-60 minutes",
                estimated_cost="$0-50",
                success_rate="70-85%",
                tools_required=["Screwdriver set", "Multimeter (optional)"],
                parts_required=["Replacement parts may be needed after diagnosis"],
                warnings=["Always power off device before opening", "Work in anti-static environment"]
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
                "Component wear and tear"
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
                "Use protective cases when applicable"
            ],
            language=diagnose_request.language or request.state.language,
            timestamp=timestamp
        )
    
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        raise get_localized_error(
            request,
            "api.errors.diagnosis_failed",
            status_code=500,
            error=str(e)
        )


@router.get("/devices")
async def get_supported_devices(request: Request):
    """Get list of supported devices in the current language"""
    language = request.state.language
    i18n = request.state.i18n
    
    devices = [
        "nintendo_switch", "nintendo_switch_lite", "nintendo_switch_oled",
        "iphone", "ipad", "macbook", "imac",
        "playstation_5", "playstation_4", "xbox_series", "xbox_one",
        "samsung_galaxy", "google_pixel",
        "gaming_pc", "laptop", "desktop_pc", "other"
    ]
    
    localized_devices = {}
    for device in devices:
        localized_devices[device] = i18n.translate(f"devices.{device}", language)
    
    return get_localized_response(
        request,
        "api.devices.success",
        devices=localized_devices,
        count=len(devices)
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
        count=len(skill_levels)
    )


@router.get("/guides/search")
async def search_repair_guides(
    request: Request,
    device_type: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 10
):
    """Search for repair guides"""
    try:
        # Import here to avoid circular imports
        from ..data.offline_repair_database import OfflineRepairDatabase
        from ..clients.ifixit_client import IFixitClient
        
        # Initialize clients
        offline_db = OfflineRepairDatabase()
        ifixit_client = IFixitClient()
        
        guides = []
        
        # Search offline database first
        if query:
            offline_guides = offline_db.search_guides(query, device_type, limit=limit//2)
            guides.extend([guide.__dict__ for guide in offline_guides])
        
        # Search iFixit if we have fewer than limit guides
        if len(guides) < limit and query:
            try:
                online_guides = ifixit_client.search_guides(query, limit=limit-len(guides))
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
            device_type=device_type
        )
    
    except Exception as e:
        raise get_localized_error(
            request,
            "api.errors.search_failed",
            status_code=500,
            error=str(e)
        )


@router.get("/languages")
async def get_supported_languages(request: Request):
    """Get list of supported languages"""
    languages = {
        "en": "English 🇺🇸",
        "ja": "日本語 🇯🇵"
    }
    
    return get_localized_response(
        request,
        "api.languages.success",
        languages=languages,
        current_language=request.state.language
    )


@router.post("/analyze-image")
async def analyze_device_image(
    request: Request,
    file: UploadFile = File(...),
    language: Optional[str] = "en",
    context: Optional[str] = None
):
    """
    Analyze device image for diagnosis
    
    Upload an image of a device for AI-powered damage assessment and repair recommendations.
    Supports JPG, PNG, and WebP formats up to 10MB.
    """
    try:
        # Import analysis models and service
        from ..schemas.image_analysis import (
            ImageAnalysisResponse, 
            ImageAnalysisError,
            DeviceInfoResponse,
            DamageAssessmentResponse
        )
        from ..services.image_analysis import ImageAnalysisService
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise get_localized_error(
                request,
                "api.errors.invalid_file_type",
                status_code=400,
                error_code="INVALID_FILE_TYPE"
            )
        
        # Validate file size (10MB limit)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise get_localized_error(
                request,
                "api.errors.file_too_large",
                status_code=400,
                error_code="FILE_TOO_LARGE"
            )
        
        # Parse context if provided
        parsed_context = {}
        if context:
            try:
                parsed_context = json.loads(context)
            except json.JSONDecodeError:
                pass
        
        # Initialize image analysis service
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise get_localized_error(
                request,
                "api.errors.service_unavailable",
                status_code=503,
                error_code="API_KEY_MISSING"
            )
        
        analysis_service = ImageAnalysisService(
            provider="openai",
            api_key=openai_api_key
        )
        
        # Perform analysis
        result = await analysis_service.analyze_device_image(
            image_data=content,
            language=language or request.state.language
        )
        
        # Convert to response format
        device_info_response = DeviceInfoResponse(
            device_type=result.device_info.device_type.value,
            brand=result.device_info.brand,
            model=result.device_info.model,
            confidence=result.device_info.confidence
        )
        
        damage_responses = [
            DamageAssessmentResponse(
                damage_type=damage.damage_type.value,
                confidence=damage.confidence,
                severity=damage.severity,
                location=damage.location,
                description=damage.description
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
            language=result.language
        )
        
        return get_localized_response(
            request,
            "api.image_analysis.success",
            analysis=analysis_response.dict(),
            file_name=file.filename,
            file_size=file_size
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
            error=str(e)
        )