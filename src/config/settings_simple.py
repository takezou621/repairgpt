"""
Simplified configuration settings for RepairGPT
"""

import os
from enum import Enum
from typing import List, Set


class Environment(str, Enum):
    """Environment types"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Log levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings:
    """Application settings with environment-based configuration"""

    def __init__(self):
        # Environment Configuration
        self.environment = Environment(os.getenv("REPAIRGPT_ENVIRONMENT", "development"))
        self.debug = os.getenv("REPAIRGPT_DEBUG", "false").lower() == "true"
        self.log_level = LogLevel(os.getenv("REPAIRGPT_LOG_LEVEL", "INFO"))

        # Application Configuration
        self.app_name = os.getenv("REPAIRGPT_APP_NAME", "RepairGPT")
        self.app_version = os.getenv("REPAIRGPT_APP_VERSION", "1.0.0")
        self.app_description = os.getenv("REPAIRGPT_APP_DESCRIPTION", "AI-powered device repair assistant")

        # API Configuration
        self.api_host = os.getenv("REPAIRGPT_API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("REPAIRGPT_API_PORT", "8000"))
        self.api_prefix = os.getenv("REPAIRGPT_API_PREFIX", "/api/v1")

        # Security Configuration
        self.secret_key = os.getenv("REPAIRGPT_SECRET_KEY", "")
        self.allowed_hosts = self._parse_list(os.getenv("REPAIRGPT_ALLOWED_HOSTS", "*"))
        self.cors_origins = self._parse_list(
            os.getenv("REPAIRGPT_CORS_ORIGINS", "http://localhost:3000,http://localhost:8501")
        )
        self.cors_methods = self._parse_list(os.getenv("REPAIRGPT_CORS_METHODS", "GET,POST,PUT,DELETE"))
        self.cors_headers = self._parse_list(os.getenv("REPAIRGPT_CORS_HEADERS", "*"))

        # Rate limiting
        self.rate_limit_requests_per_minute = int(os.getenv("REPAIRGPT_RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
        self.rate_limit_burst = int(os.getenv("REPAIRGPT_RATE_LIMIT_BURST", "10"))

        # Security headers
        self.enable_security_headers = os.getenv("REPAIRGPT_ENABLE_SECURITY_HEADERS", "true").lower() == "true"
        self.hsts_max_age = int(os.getenv("REPAIRGPT_HSTS_MAX_AGE", "31536000"))

        # API Keys and External Services
        self.openai_api_key = os.getenv("REPAIRGPT_OPENAI_API_KEY")
        self.claude_api_key = os.getenv("REPAIRGPT_CLAUDE_API_KEY")
        self.ifixit_api_key = os.getenv("REPAIRGPT_IFIXIT_API_KEY")
        
        # AI Configuration
        self.anthropic_api_key = os.getenv("REPAIRGPT_ANTHROPIC_API_KEY", self.claude_api_key)  # Alias
        self.use_mock_ai = os.getenv("REPAIRGPT_USE_MOCK_AI", "auto").lower()  # "auto", "true", "false"

        # API endpoints
        self.openai_api_base = os.getenv("REPAIRGPT_OPENAI_API_BASE", "https://api.openai.com/v1")
        self.claude_api_base = os.getenv("REPAIRGPT_CLAUDE_API_BASE", "https://api.anthropic.com")
        self.ifixit_api_base = os.getenv("REPAIRGPT_IFIXIT_API_BASE", "https://www.ifixit.com/api/2.0")

        # API timeouts and limits
        self.api_timeout_seconds = int(os.getenv("REPAIRGPT_API_TIMEOUT_SECONDS", "30"))
        self.max_image_size_mb = int(os.getenv("REPAIRGPT_MAX_IMAGE_SIZE_MB", "10"))
        self.max_text_length = int(os.getenv("REPAIRGPT_MAX_TEXT_LENGTH", "10000"))

        # Database Configuration
        self.database_url = os.getenv("REPAIRGPT_DATABASE_URL", "sqlite:///./repairgpt.db")
        self.database_echo = os.getenv("REPAIRGPT_DATABASE_ECHO", "false").lower() == "true"
        self.database_pool_size = int(os.getenv("REPAIRGPT_DATABASE_POOL_SIZE", "5"))
        self.database_max_overflow = int(os.getenv("REPAIRGPT_DATABASE_MAX_OVERFLOW", "10"))

        # Cache Configuration (Redis)
        self.redis_url = os.getenv("REPAIRGPT_REDIS_URL", "redis://localhost:6379/0")
        self.cache_ttl_seconds = int(os.getenv("REPAIRGPT_CACHE_TTL_SECONDS", "3600"))
        self.cache_enabled = os.getenv("REPAIRGPT_CACHE_ENABLED", "true").lower() == "true"

        # File Storage Configuration
        self.upload_dir = os.getenv("REPAIRGPT_UPLOAD_DIR", "./uploads")
        self.temp_dir = os.getenv("REPAIRGPT_TEMP_DIR", "./temp")
        self.allowed_file_types = self._parse_set(os.getenv("REPAIRGPT_ALLOWED_FILE_TYPES", "jpg,jpeg,png,webp"))

        # Internationalization
        self.default_language = os.getenv("REPAIRGPT_DEFAULT_LANGUAGE", "en")
        self.supported_languages = self._parse_list(os.getenv("REPAIRGPT_SUPPORTED_LANGUAGES", "en,ja"))

        # Ensure directories exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def _parse_list(self, value: str) -> List[str]:
        """Parse comma-separated string into list"""
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    def _parse_set(self, value: str) -> Set[str]:
        """Parse comma-separated string into set"""
        if not value:
            return set()
        return {item.strip() for item in value.split(",") if item.strip()}

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION

    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.environment == Environment.TESTING

    def should_use_mock_ai(self) -> bool:
        """Determine if mock AI should be used"""
        if self.use_mock_ai == "true":
            return True
        elif self.use_mock_ai == "false":
            return False
        else:  # auto
            # Use mock if no API keys are configured
            return not (self.openai_api_key or self.anthropic_api_key)

    def get_api_keys(self) -> dict:
        """Get all configured API keys (for validation)"""
        return {
            "openai": self.openai_api_key,
            "claude": self.claude_api_key,
            "anthropic": self.anthropic_api_key,
            "ifixit": self.ifixit_api_key,
        }

    def get_cors_config(self) -> dict:
        """Get CORS configuration"""
        return {
            "allow_origins": self.cors_origins,
            "allow_methods": self.cors_methods,
            "allow_headers": self.cors_headers,
            "allow_credentials": True,
        }

    def get_security_headers(self) -> dict:
        """Get security headers configuration"""
        if not self.enable_security_headers:
            return {}

        return {
            "Strict-Transport-Security": f"max-age={self.hsts_max_age}; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
        }


# Global settings instance
settings = Settings()


# Utility functions
def get_settings() -> Settings:
    """Get settings instance (for dependency injection)"""
    return settings


def validate_api_keys() -> dict:
    """Validate all API keys and return validation results"""
    results = {}
    api_keys = settings.get_api_keys()

    for service, key in api_keys.items():
        if key:
            if service == "openai" and key.startswith("sk-"):
                results[service] = {"valid": True, "configured": True}
            elif service == "claude" and key.startswith("sk-ant-"):
                results[service] = {"valid": True, "configured": True}
            elif service == "ifixit":
                results[service] = {"valid": True, "configured": True}
            else:
                results[service] = {
                    "valid": False,
                    "configured": True,
                    "error": "Invalid format",
                }
        else:
            results[service] = {
                "valid": False,
                "configured": False,
                "error": "Not configured",
            }

    return results


def get_required_env_vars() -> List[str]:
    """Get list of required environment variables for production"""
    required_vars = [
        "REPAIRGPT_SECRET_KEY",
        "REPAIRGPT_DATABASE_URL",
        "REPAIRGPT_ENVIRONMENT",
    ]

    # Add API keys if services are expected to be available
    if settings.environment == Environment.PRODUCTION:
        required_vars.extend(
            [
                "REPAIRGPT_OPENAI_API_KEY",
                "REPAIRGPT_ALLOWED_HOSTS",
                "REPAIRGPT_CORS_ORIGINS",
            ]
        )

    return required_vars


def validate_production_config() -> List[str]:
    """Validate production configuration and return list of issues"""
    issues = []

    if not settings.is_production():
        return issues

    # Check required environment variables
    for var in get_required_env_vars():
        if not os.getenv(var):
            issues.append(f"Missing required environment variable: {var}")

    # Check security settings
    if not settings.secret_key:
        issues.append("Secret key not configured")

    if "*" in settings.allowed_hosts:
        issues.append("Wildcard hosts not allowed in production")

    if any("localhost" in origin for origin in settings.cors_origins):
        issues.append("Localhost origins not recommended in production")

    if settings.debug:
        issues.append("Debug mode should be disabled in production")

    if settings.database_url.startswith("sqlite"):
        issues.append("SQLite not recommended for production")

    return issues
