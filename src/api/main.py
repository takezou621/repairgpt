"""
FastAPI main application with i18n and security support
Implements Issue #90: 🔒 設定管理とセキュリティ強化
"""

from fastapi import FastAPI, Request
from . import create_app, get_localized_response
from .routes import router
from ..config.settings import settings

# Create FastAPI app with i18n and security support
app = create_app()

# Include API routes with configured prefix
app.include_router(router, prefix=settings.api_prefix)


# Root endpoint with secure configuration
@app.get("/")
async def root(request: Request):
    """Root endpoint with localized response"""
    return get_localized_response(
        request,
        "api.root.message",
        app_name=settings.app_name,
        version=settings.app_version,
        docs="/docs",
        environment=settings.environment.value,
        security_enabled=settings.enable_security_headers,
        supported_languages=settings.supported_languages,
    )


# Health check endpoint
@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint"""
    return get_localized_response(
        request,
        "api.health.message",
        status="healthy",
        environment=settings.environment.value,
        version=settings.app_version,
    )


if __name__ == "__main__":
    import uvicorn
    import logging

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
