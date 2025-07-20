"""
Health check API routes
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

health_router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    message: str
    language: str
    version: str


@health_router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check endpoint with localized response"""
    language = getattr(request.state, "language", "en")

    return HealthResponse(
        status="healthy",
        message="Service is running",
        language=language,
        version="1.0.0",
    )
