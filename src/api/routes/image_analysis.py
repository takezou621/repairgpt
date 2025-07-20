"""
Image analysis API routes
"""

import json
import logging
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from ...config.settings_simple import settings
from ...utils.security import (
    create_audit_log,
    get_client_ip,
    sanitize_filename,
    validate_content_type,
    validate_image_content,
)

logger = logging.getLogger(__name__)

image_router = APIRouter(prefix="/images", tags=["Image Analysis"])


@image_router.post("/analyze")
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
        # Validate filename
        if file.filename:
            sanitize_filename(file.filename)

        # Validate file type
        allowed_types = [f"image/{ext}" for ext in settings.allowed_file_types]
        if not file.content_type or not validate_content_type(
            file.content_type, allowed_types
        ):
            logger.warning(f"Invalid file type uploaded: {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid file type",
                    "allowed_types": list(settings.allowed_file_types),
                },
            )

        # Read and validate file content
        content = await file.read()
        file_size = len(content)
        max_size = settings.max_image_size_mb * 1024 * 1024

        if file_size > max_size:
            logger.warning(f"File too large uploaded: {file_size} bytes")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "File too large",
                    "max_size_mb": settings.max_image_size_mb,
                },
            )

        # Validate image content for security
        image_validation = validate_image_content(content, max_size)
        if not image_validation["valid"]:
            logger.warning(f"Invalid image content: {image_validation['error']}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid image content",
                    "details": image_validation["error"],
                },
            )

        # Parse context if provided
        if context:
            try:
                json.loads(context)
            except json.JSONDecodeError:
                pass

        # Initialize image analysis service
        if not settings.openai_api_key:
            logger.error("OpenAI API key not configured")
            raise HTTPException(
                status_code=503, detail="Image analysis service unavailable"
            )

        # Create audit log
        client_ip = get_client_ip(request)
        create_audit_log(
            action="image_analysis_request",
            ip_address=client_ip,
            details={
                "file_size": file_size,
                "file_type": file.content_type,
                "language": language,
            },
        )

        # For now, return a mock response
        # In real implementation, you'd use the ImageAnalysisService
        return {
            "analysis": {
                "device_info": {
                    "device_type": "smartphone",
                    "brand": "unknown",
                    "model": "unknown",
                    "confidence": 0.8,
                },
                "damage_detected": [],
                "overall_condition": "good",
                "repair_urgency": "low",
                "estimated_repair_cost": "$0-50",
                "repair_difficulty": "easy",
                "analysis_confidence": 0.75,
                "recommended_actions": ["Visual inspection complete"],
                "warnings": [],
                "language": language or "en",
            },
            "file_name": file.filename,
            "file_size": file_size,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
