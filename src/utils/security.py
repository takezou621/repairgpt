"""
Security utilities for RepairGPT
Implements Issue #90: 🔒 設定管理とセキュリティ強化

This module provides:
- Input sanitization and validation
- API key validation
- Security headers middleware
- Rate limiting utilities
- File security utilities
"""

import hashlib
import hmac
import html
import logging
import re
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import bleach
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


# ============================================================================
# Input Sanitization
# ============================================================================


def sanitize_input(
    text: str,
    max_length: Optional[int] = None,
    allow_html: bool = False,
    allowed_tags: Optional[List[str]] = None,
) -> str:
    """
    Sanitize user input to prevent XSS and other injection attacks

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        allow_html: Whether to allow HTML tags
        allowed_tags: List of allowed HTML tags if allow_html is True

    Returns:
        str: Sanitized text

    Raises:
        ValueError: If input is too long or contains invalid content
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    # Remove null bytes and control characters
    text = text.replace("\x00", "").replace("\r", "").strip()

    # Check length
    if max_length and len(text) > max_length:
        raise ValueError(f"Input too long. Maximum length is {max_length} characters")

    if allow_html:
        # Use bleach to clean HTML
        if allowed_tags is None:
            allowed_tags = ["b", "i", "u", "em", "strong", "p", "br"]

        text = bleach.clean(text, tags=allowed_tags, strip=True)
    else:
        # Escape HTML entities
        text = html.escape(text)

    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"on\w+\s*=",
        r"data:text/html",
        r"data:application/javascript",
    ]

    for pattern in dangerous_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

    return text


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other attacks

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    if not filename:
        return "unnamed_file"

    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    # Prevent reserved names on Windows
    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }

    name_without_ext = Path(filename).stem.upper()
    if name_without_ext in reserved_names:
        filename = f"file_{filename}"

    # Ensure filename is not empty
    if not filename:
        return "unnamed_file"

    # Limit length
    if len(filename) > 255:
        name = Path(filename).stem[:200]
        suffix = Path(filename).suffix[:50]
        filename = f"{name}{suffix}"

    return filename


def is_safe_filename(filename: str) -> bool:
    """
    Check if filename is safe

    Args:
        filename: Filename to check

    Returns:
        bool: True if filename is safe
    """
    try:
        sanitized = sanitize_filename(filename)
        return sanitized == filename and len(filename) <= 255
    except Exception:
        return False


# ============================================================================
# API Key Validation
# ============================================================================


def validate_api_key(api_key: str, service: str) -> dict:
    """
    Validate API key format and basic structure

    Args:
        api_key: API key to validate
        service: Service name (openai, claude, ifixit)

    Returns:
        dict: Validation result with status and details
    """
    result = {"valid": False, "service": service, "error": None, "warnings": []}

    if not api_key:
        result["error"] = "API key is empty"
        return result

    if not isinstance(api_key, str):
        result["error"] = "API key must be a string"
        return result

    # Remove whitespace
    api_key = api_key.strip()

    # Service-specific validation
    if service == "openai":
        if not api_key.startswith("sk-"):
            result["error"] = "OpenAI API key must start with 'sk-'"
            return result

        if len(api_key) < 40:
            result["error"] = "OpenAI API key too short"
            return result

        if not re.match(r"^sk-[A-Za-z0-9]{40,}$", api_key):
            result["error"] = "Invalid OpenAI API key format"
            return result

    elif service == "claude":
        if not api_key.startswith("sk-ant-"):
            result["error"] = "Claude API key must start with 'sk-ant-'"
            return result

        if len(api_key) < 50:
            result["error"] = "Claude API key too short"
            return result

    elif service == "ifixit":
        if len(api_key) < 10:
            result["error"] = "iFixit API key too short"
            return result

    else:
        result["error"] = f"Unknown service: {service}"
        return result

    # Check for obvious test/placeholder keys
    test_patterns = ["test", "demo", "example", "placeholder", "your-key", "insert-key"]

    if any(pattern in api_key.lower() for pattern in test_patterns):
        result["warnings"].append("API key appears to be a placeholder")

    result["valid"] = True
    return result


def hash_api_key(api_key: str, salt: str = "") -> str:
    """
    Create a secure hash of an API key for logging/storage

    Args:
        api_key: API key to hash
        salt: Optional salt for hashing

    Returns:
        str: Hashed API key (first 8 chars of SHA256)
    """
    if not api_key:
        return "empty"

    full_key = f"{salt}{api_key}"
    hash_obj = hashlib.sha256(full_key.encode())
    return f"{api_key[:8]}...{hash_obj.hexdigest()[:8]}"


# ============================================================================
# Rate Limiting
# ============================================================================


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)

    def is_allowed(self, identifier: str) -> tuple[bool, dict]:
        """
        Check if request is allowed for given identifier

        Args:
            identifier: Unique identifier (IP, user ID, etc.)

        Returns:
            tuple: (is_allowed, rate_limit_info)
        """
        now = time.time()
        request_times = self.requests[identifier]

        # Remove old requests outside the window
        while request_times and request_times[0] < now - self.window_seconds:
            request_times.popleft()

        # Check if under limit
        current_requests = len(request_times)
        allowed = current_requests < self.max_requests

        if allowed:
            request_times.append(now)

        # Calculate rate limit info
        remaining = max(0, self.max_requests - current_requests - (1 if allowed else 0))
        reset_time = int(now + self.window_seconds)

        rate_limit_info = {
            "limit": self.max_requests,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": self.window_seconds if not allowed else None,
        }

        return allowed, rate_limit_info

    def cleanup_expired(self):
        """Clean up expired entries to prevent memory leaks"""
        now = time.time()
        cutoff = now - self.window_seconds

        for identifier in list(self.requests.keys()):
            request_times = self.requests[identifier]

            # Remove old requests
            while request_times and request_times[0] < cutoff:
                request_times.popleft()

            # Remove empty deques
            if not request_times:
                del self.requests[identifier]


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request, handling proxies

    Args:
        request: FastAPI request object

    Returns:
        str: Client IP address
    """
    # Check for forwarded headers (from proxies/load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fall back to direct connection
    return request.client.host if request.client else "unknown"


def hash_ip_address(ip: str, salt: str = "repairgpt") -> str:
    """
    Create a hash of IP address for privacy-preserving rate limiting

    Args:
        ip: IP address to hash
        salt: Salt for hashing

    Returns:
        str: Hashed IP address
    """
    full_string = f"{salt}:{ip}"
    return hashlib.sha256(full_string.encode()).hexdigest()[:16]


# ============================================================================
# Security Headers Middleware
# ============================================================================


class SecurityHeaders(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    """

    def __init__(self, app, headers: Optional[Dict[str, str]] = None):
        """
        Initialize security headers middleware

        Args:
            app: FastAPI application
            headers: Custom security headers
        """
        super().__init__(app)

        self.default_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "img-src 'self' data: https:; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "connect-src 'self' https:; "
                "font-src 'self' data:; "
                "media-src 'self';"
            ),
        }

        if headers:
            self.default_headers.update(headers)

    async def dispatch(self, request: Request, call_next):
        """
        Add security headers to response

        Args:
            request: Request object
            call_next: Next middleware in chain

        Returns:
            Response with security headers
        """
        response = await call_next(request)

        # Add security headers
        for header, value in self.default_headers.items():
            response.headers[header] = value

        return response


# ============================================================================
# Rate Limiting Middleware
# ============================================================================


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests
    """

    def __init__(
        self,
        app,
        rate_limiter: RateLimiter,
        hash_ips: bool = True,
        exempt_paths: Optional[List[str]] = None,
    ):
        """
        Initialize rate limiting middleware

        Args:
            app: FastAPI application
            rate_limiter: RateLimiter instance
            hash_ips: Whether to hash IP addresses for privacy
            exempt_paths: Paths exempt from rate limiting
        """
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.hash_ips = hash_ips
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next):
        """
        Apply rate limiting to request

        Args:
            request: Request object
            call_next: Next middleware in chain

        Returns:
            Response or rate limit error
        """
        # Check if path is exempt
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # Get client identifier
        client_ip = get_client_ip(request)
        identifier = hash_ip_address(client_ip) if self.hash_ips else client_ip

        # Check rate limit
        allowed, rate_info = self.rate_limiter.is_allowed(identifier)

        if not allowed:
            logger.warning(f"Rate limit exceeded for {identifier}")

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "rate_limit": rate_info,
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info["retry_after"]),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to successful responses
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])

        return response


# ============================================================================
# Content Validation
# ============================================================================


def validate_content_type(content_type: str, allowed_types: List[str]) -> bool:
    """
    Validate content type against allowed types

    Args:
        content_type: Content type to validate
        allowed_types: List of allowed content types

    Returns:
        bool: True if content type is allowed
    """
    if not content_type:
        return False

    # Remove charset and other parameters
    main_type = content_type.split(";")[0].strip().lower()

    return main_type in allowed_types


def validate_image_content(content: bytes, max_size: int = 10 * 1024 * 1024) -> dict:
    """
    Validate image content for security

    Args:
        content: Image content bytes
        max_size: Maximum allowed size in bytes

    Returns:
        dict: Validation result
    """
    result = {
        "valid": False,
        "error": None,
        "warnings": [],
        "size": len(content),
        "format": None,
    }

    # Check size
    if len(content) > max_size:
        result["error"] = f"Image too large. Maximum size is {max_size} bytes"
        return result

    if len(content) < 100:
        result["error"] = "Image too small to be valid"
        return result

    # Check for common image headers
    if content.startswith(b"\xff\xd8\xff"):
        result["format"] = "jpeg"
    elif content.startswith(b"\x89PNG\r\n\x1a\n"):
        result["format"] = "png"
    elif content.startswith(b"RIFF") and b"WEBP" in content[:20]:
        result["format"] = "webp"
    elif content.startswith(b"GIF87a") or content.startswith(b"GIF89a"):
        result["format"] = "gif"
    else:
        result["error"] = "Unknown or unsupported image format"
        return result

    # Check for embedded content (basic check)
    suspicious_patterns = [
        b"<script",
        b"javascript:",
        b"<?php",
        b"<%",
        b"exec(",
        b"eval(",
    ]

    content_lower = content.lower()
    for pattern in suspicious_patterns:
        if pattern in content_lower:
            result["warnings"].append(
                f"Suspicious pattern found: {pattern.decode('utf-8', errors='ignore')}"
            )

    result["valid"] = True
    return result


# ============================================================================
# Secure Logging
# ============================================================================


def sanitize_log_data(data: Any) -> Any:
    """
    Sanitize data before logging to remove sensitive information

    Args:
        data: Data to sanitize

    Returns:
        Sanitized data safe for logging
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()

            # Redact sensitive keys
            if any(
                sensitive in key_lower
                for sensitive in ["key", "token", "password", "secret", "auth"]
            ):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = sanitize_log_data(value)

        return sanitized

    elif isinstance(data, list):
        return [sanitize_log_data(item) for item in data]

    elif isinstance(data, str):
        # Redact potential API keys or tokens in strings
        patterns = [
            (r"sk-[A-Za-z0-9]{40,}", "sk-[REDACTED]"),
            (r"sk-ant-[A-Za-z0-9-]{40,}", "sk-ant-[REDACTED]"),
            (r"Bearer [A-Za-z0-9-_.]{20,}", "Bearer [REDACTED]"),
            (r"[A-Za-z0-9]{32,}", "[REDACTED_TOKEN]"),
        ]

        for pattern, replacement in patterns:
            data = re.sub(pattern, replacement, data)

        return data

    else:
        return data


def create_audit_log(
    action: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create structured audit log entry

    Args:
        action: Action being performed
        user_id: User ID if available
        ip_address: Client IP address
        details: Additional details

    Returns:
        dict: Structured audit log entry
    """
    log_entry = {
        "timestamp": time.time(),
        "action": action,
        "user_id": user_id,
        "ip_hash": hash_ip_address(ip_address) if ip_address else None,
        "details": sanitize_log_data(details) if details else {},
    }

    return log_entry


# ============================================================================
# Utility Functions
# ============================================================================


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token

    Args:
        length: Token length in bytes

    Returns:
        str: Secure random token in hex format
    """
    import secrets

    return secrets.token_hex(length)


def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks

    Args:
        a: First string
        b: Second string

    Returns:
        bool: True if strings are equal
    """
    return hmac.compare_digest(a.encode(), b.encode())


def mask_sensitive_data(data: str, show_chars: int = 4) -> str:
    """
    Mask sensitive data for display

    Args:
        data: Sensitive data to mask
        show_chars: Number of characters to show at start

    Returns:
        str: Masked data
    """
    if not data or len(data) <= show_chars:
        return "*" * len(data) if data else ""

    return data[:show_chars] + "*" * (len(data) - show_chars)
