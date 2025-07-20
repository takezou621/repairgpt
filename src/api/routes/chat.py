"""
Chat API routes for repair assistance
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, validator

from ...config.settings_simple import settings
from ...utils.security import create_audit_log, get_client_ip, sanitize_input

chat_router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    device_type: Optional[str] = None
    device_model: Optional[str] = None
    issue_description: Optional[str] = None
    skill_level: str = "beginner"
    language: str = "en"

    @validator("message")
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return sanitize_input(v, max_length=settings.max_text_length)

    @validator("device_type", "device_model", "issue_description")
    def validate_text_fields(cls, v):
        if v:
            return sanitize_input(v, max_length=500)
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


class ChatResponse(BaseModel):
    response: str
    language: str
    context: Dict[str, Any]


@chat_router.post("", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest, request: Request):
    """Chat endpoint for repair assistance with security logging"""
    # Create audit log
    client_ip = get_client_ip(request)
    create_audit_log(
        action="chat_request",
        ip_address=client_ip,
        details={
            "device_type": chat_request.device_type,
            "skill_level": chat_request.skill_level,
            "language": chat_request.language,
            "message_length": len(chat_request.message),
        },
    )

    try:
        # Import here to avoid circular imports
        from ...chat.llm_chatbot import RepairChatbot

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
            language=getattr(request.state, "language", chat_request.language),
            context={
                "device_type": chat_request.device_type,
                "device_model": chat_request.device_model,
                "issue_description": chat_request.issue_description,
                "skill_level": chat_request.skill_level,
            },
        )

    except Exception as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
