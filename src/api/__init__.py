"""
FastAPI backend for RepairGPT with internationalization support
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import json
import os
from pathlib import Path


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
                    with open(locale_file, 'r', encoding='utf-8') as f:
                        self.translations[language_code] = json.load(f)
                except Exception as e:
                    print(f"Warning: Failed to load translation file {locale_file}: {e}")
    
    def get_language_from_request(self, request: Request) -> str:
        """Extract language from request headers or query parameters"""
        # Check query parameter first
        lang = request.query_params.get('lang')
        if lang and lang in self.translations:
            return lang
        
        # Check Accept-Language header
        accept_language = request.headers.get('accept-language', '')
        for lang_range in accept_language.split(','):
            lang = lang_range.split(';')[0].strip()[:2]  # Get first 2 chars
            if lang in self.translations:
                return lang
        
        return 'en'  # Default to English
    
    def translate(self, key: str, language: str, **kwargs) -> str:
        """Translate a key to the specified language"""
        translation = self._get_nested_value(
            self.translations.get(language, {}), 
            key
        )
        
        if translation is None and language != 'en':
            translation = self._get_nested_value(
                self.translations.get('en', {}), 
                key
            )
        
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
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current if isinstance(current, str) else None


def create_app() -> FastAPI:
    """Create and configure FastAPI application with i18n support"""
    
    app = FastAPI(
        title="RepairGPT API",
        description="AI-Powered Electronic Device Repair Assistant API",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
    
    return app


# Helper functions for API routes
def get_localized_response(request: Request, message_key: str, **kwargs) -> dict:
    """Get a localized API response"""
    language = getattr(request.state, 'language', 'en')
    i18n = getattr(request.state, 'i18n', None)
    
    if i18n:
        message = i18n.translate(message_key, language, **kwargs)
    else:
        message = message_key
    
    return {
        "message": message,
        "language": language,
        **kwargs
    }


def get_localized_error(request: Request, error_key: str, status_code: int = 400, **kwargs) -> HTTPException:
    """Get a localized error response"""
    language = getattr(request.state, 'language', 'en')
    i18n = getattr(request.state, 'i18n', None)
    
    if i18n:
        message = i18n.translate(error_key, language, **kwargs)
    else:
        message = error_key
    
    return HTTPException(
        status_code=status_code,
        detail={
            "message": message,
            "language": language,
            "error_code": error_key
        }
    )