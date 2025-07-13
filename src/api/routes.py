"""
API routes for RepairGPT with internationalization support
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json

from . import get_localized_response, get_localized_error


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    device_type: Optional[str] = None
    device_model: Optional[str] = None
    issue_description: Optional[str] = None
    skill_level: Optional[str] = "beginner"
    language: Optional[str] = "en"


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
                device_type=chat_request.device_type,
                device_model=chat_request.device_model,
                issue_description=chat_request.issue_description,
                user_skill_level=chat_request.skill_level
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
                "skill_level": chat_request.skill_level
            }
        )
    
    except Exception as e:
        raise get_localized_error(
            request, 
            "api.errors.chat_failed", 
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