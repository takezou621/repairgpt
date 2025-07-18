"""
FastAPI backend for RepairGPT with internationalization support
Implements Issue #90: 🔒 設定管理とセキュリティ強化
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import json
import os
from pathlib import Path

# Import security and configuration
from ..config.settings import settings, validate_api_keys
from ..utils.security import (
    SecurityHeaders,
    RateLimitMiddleware,
    RateLimiter,
    sanitize_log_data,
    create_audit_log,
)


class I18nMiddleware:
    """Middleware to handle internationalization for API responses"""

    def __init__(self, app: FastAPI):
        self.app = app
        self.translations = {}
        self._load_translations()

    def _load_translations(self):
        """Load translation files"""
        locales_dir = Path(__file__).parent.parent / "i18n" / "locales"
        if locales_dir.exists():
            for locale_file in locales_dir.glob("*.json"):
                language_code = locale_file.stem
                try:
                    with open(locale_file, "r", encoding="utf-8") as f:
                        self.translations[language_code] = json.load(f)
                except Exception as e:
                    print(
                        f"Warning: Failed to load translation file {locale_file}: {e}"
                    )

    def get_language_from_request(self, request: Request) -> str:
        """Extract language from request headers or query parameters"""
        # Check query parameter first
        lang = request.query_params.get("lang")
        if lang and lang in self.translations:
            return lang

        # Check Accept-Language header
        accept_language = request.headers.get("accept-language", "")
        for lang_range in accept_language.split(","):
            lang = lang_range.split(";")[0].strip()[:2]  # Get first 2 chars
            if lang in self.translations:
                return lang

        return "en"  # Default to English

    def translate(self, key: str, language: str, **kwargs) -> str:
        """Translate a key to the specified language"""
        translation = self._get_nested_value(self.translations.get(language, {}), key)

        if translation is None and language != "en":
            translation = self._get_nested_value(self.translations.get("en", {}), key)

        if translation is None:
            return key

        if kwargs:
            try:
                return translation.format(**kwargs)
            except (KeyError, ValueError):
                return translation

        return translation

    def _get_nested_value(self, data: dict, key: str) -> Optional[str]:
        """Get nested dictionary value using dot notation"""
        keys = key.split(".")
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return current if isinstance(current, str) else None


def create_app() -> FastAPI:
    """Create and configure FastAPI application with i18n and security support"""

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        debug=settings.debug,
    )

    # Add security headers middleware
    if settings.enable_security_headers:
        app.add_middleware(SecurityHeaders, headers=settings.get_security_headers())

    # Add rate limiting middleware
    rate_limiter = RateLimiter(
        max_requests=settings.rate_limit_requests_per_minute, window_seconds=60
    )
    app.add_middleware(
        RateLimitMiddleware,
        rate_limiter=rate_limiter,
        hash_ips=True,
        exempt_paths=["/health", "/docs", "/openapi.json", "/redoc"],
    )

    # Add CORS middleware with secure configuration
    cors_config = settings.get_cors_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config["allow_origins"],
        allow_credentials=cors_config["allow_credentials"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
    )

    # Add i18n middleware
    i18n_middleware = I18nMiddleware(app)

    @app.middleware("http")
    async def add_i18n_context(request: Request, call_next):
        """Add i18n context to request"""
        language = i18n_middleware.get_language_from_request(request)
        request.state.language = language
        request.state.i18n = i18n_middleware

        response = await call_next(request)
        response.headers["Content-Language"] = language
        return response

    # Add startup event for validation
    @app.on_event("startup")
    async def startup_event():
        """Validate configuration on startup"""
        import logging

        logger = logging.getLogger(__name__)

        # Validate production configuration
        if settings.is_production():
            from ..config.settings import validate_production_config

            issues = validate_production_config()
            if issues:
                logger.error("Production configuration issues found:")
                for issue in issues:
                    logger.error(f"  - {issue}")
                raise RuntimeError("Invalid production configuration")

        # Validate API keys
        api_validation = validate_api_keys()
        for service, result in api_validation.items():
            if result["configured"]:
                if result["valid"]:
                    logger.info(f"{service.upper()} API key configured and valid")
                else:
                    logger.warning(
                        f"{service.upper()} API key configured but invalid: {result.get('error', 'Unknown error')}"
                    )
            else:
                logger.warning(f"{service.upper()} API key not configured")

        logger.info(f"RepairGPT API starting in {settings.environment} mode")
        logger.info(
            f"Security headers: {'enabled' if settings.enable_security_headers else 'disabled'}"
        )
        logger.info(
            f"Rate limiting: {settings.rate_limit_requests_per_minute} requests/minute"
        )

    return app


# Helper functions for API routes
def get_localized_response(request: Request, message_key: str, **kwargs) -> dict:
    """Get a localized API response"""
    language = getattr(request.state, "language", "en")
    i18n = getattr(request.state, "i18n", None)

    if i18n:
        message = i18n.translate(message_key, language, **kwargs)
    else:
        message = message_key

    return {"message": message, "language": language, **kwargs}


def get_localized_error(
    request: Request, error_key: str, status_code: int = 400, **kwargs
) -> HTTPException:
    """Get a localized error response"""
    language = getattr(request.state, "language", "en")
    i18n = getattr(request.state, "i18n", None)

    if i18n:
        message = i18n.translate(error_key, language, **kwargs)
    else:
        message = error_key

    return HTTPException(
        status_code=status_code,
        detail={"message": message, "language": language, "error_code": error_key},
    )
