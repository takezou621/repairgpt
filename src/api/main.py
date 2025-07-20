"""
FastAPI main application - Refactored for better maintainability
"""

import logging

from fastapi import Request

from ..config.settings_simple import settings
from . import create_app
from .routes import auth_router, chat_router, devices_router, health_router

# Create FastAPI app
app = create_app()

# Include all route modules
app.include_router(health_router)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(chat_router, prefix=settings.api_prefix)
app.include_router(devices_router, prefix=settings.api_prefix)


@app.get("/")
async def root(request: Request):
    """Root endpoint"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment.value,
        "docs": "/docs",
        "supported_languages": settings.supported_languages,
    }


if __name__ == "__main__":
    import uvicorn

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.value),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")

    # Run with secure configuration
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.value.lower(),
        reload=settings.debug,
    )
