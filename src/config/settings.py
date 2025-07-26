"""
Configuration settings for RepairGPT with security and environment management
Implements Issue #90: 🔒 設定管理とセキュリティ強化
"""

import os
from enum import Enum
from typing import List, Optional, Set

from pydantic import Field, field_validator, ConfigDict

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings


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


class Settings(BaseSettings):
    """Application settings with environment-based configuration"""

    # Environment Configuration
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)
    log_level: LogLevel = Field(default=LogLevel.INFO)

    # Application Configuration
    app_name: str = Field(default="RepairGPT")
    app_version: str = Field(default="1.0.0")
    app_description: str = Field(default="AI-powered device repair assistant")

    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")

    # ============================================================================
    # Security Configuration
    # ============================================================================
    secret_key: str = Field(default="", description="Secret key for JWT and other cryptographic operations")
    allowed_hosts: List[str] = Field(default=["*"], description="Allowed hosts for CORS")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8501"],
        description="CORS allowed origins",
    )
    cors_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE"], description="CORS allowed methods")
    cors_headers: List[str] = Field(default=["*"], description="CORS allowed headers")

    # Rate limiting
    rate_limit_requests_per_minute: int = Field(default=60, description="Rate limit: requests per minute per IP")
    rate_limit_burst: int = Field(default=10, description="Rate limit: burst size")

    # Security headers
    enable_security_headers: bool = Field(default=True, description="Enable security headers")
    hsts_max_age: int = Field(default=31536000, description="HSTS max age in seconds")  # 1 year

    # ============================================================================
    # API Keys and External Services
    # ============================================================================
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key for GPT models")
    claude_api_key: Optional[str] = Field(default=None, description="Claude API key for Anthropic models")
    ifixit_api_key: Optional[str] = Field(default=None, description="iFixit API key for repair guides")

    # API endpoints
    openai_api_base: str = Field(default="https://api.openai.com/v1", description="OpenAI API base URL")
    claude_api_base: str = Field(default="https://api.anthropic.com", description="Claude API base URL")
    ifixit_api_base: str = Field(default="https://www.ifixit.com/api/2.0", description="iFixit API base URL")

    # API timeouts and limits
    api_timeout_seconds: int = Field(default=30, description="API request timeout in seconds")
    max_image_size_mb: int = Field(default=10, description="Maximum image upload size in MB")
    max_text_length: int = Field(default=10000, description="Maximum text input length")

    # ============================================================================
    # Database Configuration
    # ============================================================================
    database_url: str = Field(default="sqlite:///./repairgpt.db", description="Database connection URL")
    database_echo: bool = Field(default=False, description="Enable SQLAlchemy query logging")
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Database connection pool max overflow")

    # ============================================================================
    # Cache Configuration (Redis)
    # ============================================================================
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching",
    )
    cache_ttl_seconds: int = Field(default=3600, description="Default cache TTL in seconds")  # 1 hour
    cache_enabled: bool = Field(default=True, description="Enable caching")

    # ============================================================================
    # File Storage Configuration
    # ============================================================================
    upload_dir: str = Field(default="./uploads", description="Directory for file uploads")
    temp_dir: str = Field(default="./temp", description="Directory for temporary files")
    allowed_file_types: Set[str] = Field(
        default={"jpg", "jpeg", "png", "webp"}, description="Allowed file upload types"
    )

    # ============================================================================
    # Internationalization
    # ============================================================================
    default_language: str = Field(default="en", description="Default application language")
    supported_languages: List[str] = Field(default=["en", "ja"], description="Supported languages")

    # ============================================================================
    # Monitoring and Observability
    # ============================================================================
    enable_metrics: bool = Field(default=False, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, description="Metrics server port")

    enable_tracing: bool = Field(default=False, description="Enable distributed tracing")
    jaeger_endpoint: Optional[str] = Field(default=None, description="Jaeger tracing endpoint")

    # ============================================================================
    # Validators
    # ============================================================================

    @field_validator("debug")
    @classmethod
    def set_debug_mode(cls, v, info):
        """Set debug mode based on environment"""
        if info.data.get("environment") == Environment.DEVELOPMENT:
            return True
        return v

    @field_validator("log_level")
    @classmethod
    def set_log_level(cls, v, info):
        """Set log level based on environment"""
        env = info.data.get("environment")
        if env == Environment.DEVELOPMENT:
            return LogLevel.DEBUG
        elif env == Environment.PRODUCTION:
            return LogLevel.WARNING
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v, info):
        """Validate secret key is set for production"""
        if info.data.get("environment") == Environment.PRODUCTION and not v:
            raise ValueError("Secret key must be set in production environment")
        if v and len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v):
        """Validate OpenAI API key format"""
        if v and not v.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format")
        return v

    @field_validator("claude_api_key")
    @classmethod
    def validate_claude_key(cls, v):
        """Validate Claude API key format"""
        if v and not v.startswith("sk-ant-"):
            raise ValueError("Invalid Claude API key format")
        return v

    @field_validator("allowed_hosts")
    @classmethod
    def validate_allowed_hosts(cls, v, info):
        """Validate allowed hosts for production"""
        if info.data.get("environment") == Environment.PRODUCTION and "*" in v:
            raise ValueError("Wildcard hosts not allowed in production")
        return v

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v, info):
        """Validate CORS origins for production"""
        if info.data.get("environment") == Environment.PRODUCTION:
            for origin in v:
                if "localhost" in origin:
                    raise ValueError("Localhost origins not allowed in production")
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v, info):
        """Validate database URL"""
        if info.data.get("environment") == Environment.PRODUCTION and v.startswith("sqlite"):
            raise ValueError("SQLite not recommended for production")
        return v

    @field_validator("rate_limit_requests_per_minute")
    @classmethod
    def validate_rate_limit(cls, v):
        """Validate rate limit values"""
        if v <= 0:
            raise ValueError("Rate limit must be greater than 0")
        return v

    @field_validator("max_image_size_mb")
    @classmethod
    def validate_max_image_size(cls, v):
        """Validate maximum image size"""
        if v <= 0 or v > 50:
            raise ValueError("Maximum image size must be between 1 and 50 MB")
        return v

    @field_validator("upload_dir", "temp_dir")
    @classmethod
    def validate_directories(cls, v):
        """Ensure directories exist"""
        os.makedirs(v, exist_ok=True)
        return v

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION

    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.environment == Environment.TESTING

    def get_api_keys(self) -> dict:
        """Get all configured API keys (for validation)"""
        return {
            "openai": self.openai_api_key,
            "claude": self.claude_api_key,
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

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="REPAIRGPT_",
        json_schema_extra={
            "example": {
                "environment": "development",
                "debug": True,
                "openai_api_key": "sk-your-openai-key-here",
                "claude_api_key": "sk-ant-your-claude-key-here",
                "secret_key": "your-super-secret-key-here-min-32-chars",
                "cors_origins": ["http://localhost:3000", "http://localhost:8501"],
            }
        }
    )


# Global settings instance
settings = Settings()


# Utility functions
def get_settings() -> Settings:
    """Get settings instance (for dependency injection)"""
    return settings


def validate_api_keys() -> dict:
    """
    Validate all API keys and return validation results

    Returns:
        dict: Validation results for each API key
    """
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
    """
    Get list of required environment variables for production

    Returns:
        List[str]: Required environment variable names
    """
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
    """
    Validate production configuration and return list of issues

    Returns:
        List[str]: List of configuration issues
    """
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
