"""Authentication test fixtures and data"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

import pytest


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing registration"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "preferred_language": "en",
        "skill_level": "beginner",
    }


@pytest.fixture
def multiple_users_data() -> List[Dict[str, Any]]:
    """Multiple user data for batch testing"""
    return [
        {
            "username": "user1",
            "email": "user1@example.com",
            "password": "password123",
            "preferred_language": "en",
            "skill_level": "beginner",
        },
        {
            "username": "user2",
            "email": "user2@example.com",
            "password": "password456",
            "preferred_language": "ja",
            "skill_level": "intermediate",
        },
        {
            "username": "user3",
            "email": "user3@example.com",
            "password": "password789",
            "preferred_language": "en",
            "skill_level": "expert",
        },
    ]


@pytest.fixture
def admin_user_data() -> Dict[str, Any]:
    """Admin user data for testing elevated permissions"""
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "preferred_language": "en",
        "skill_level": "expert",
        "role": "admin",
        "permissions": ["read", "write", "admin"],
    }


@pytest.fixture
def valid_login_credentials() -> Dict[str, str]:
    """Valid login credentials for testing"""
    return {"username": "testuser", "password": "testpassword123"}


@pytest.fixture
def invalid_login_credentials() -> List[Dict[str, str]]:
    """Various invalid login credentials for testing"""
    return [
        {"username": "nonexistent", "password": "password123"},
        {"username": "testuser", "password": "wrongpassword"},
        {"username": "", "password": "password123"},
        {"username": "testuser", "password": ""},
        {"username": "", "password": ""},
    ]


@pytest.fixture
def mock_jwt_token() -> str:
    """Mock JWT token for testing"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTY0NjA2NDAwMH0.mock_signature"


@pytest.fixture
def expired_jwt_token() -> str:
    """Expired JWT token for testing"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTY0MDAwMDAwMH0.expired_signature"


@pytest.fixture
def malformed_jwt_tokens() -> List[str]:
    """Various malformed JWT tokens for testing"""
    return [
        "invalid.token.format",
        "not-a-jwt-token",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid_payload.signature",
        "valid_header.eyJzdWIiOiJ0ZXN0dXNlciJ9.missing_exp",
        "",
        "Bearer token_without_bearer_prefix",
    ]


@pytest.fixture
def auth_headers_valid(mock_jwt_token) -> Dict[str, str]:
    """Valid authorization headers for testing"""
    return {"Authorization": f"Bearer {mock_jwt_token}"}


@pytest.fixture
def auth_headers_invalid() -> List[Dict[str, str]]:
    """Various invalid authorization headers for testing"""
    return [
        {"Authorization": "Bearer invalid_token"},
        {"Authorization": "InvalidType token123"},
        {"Authorization": "Bearer "},
        {"Authorization": ""},
        {},  # No authorization header
        {"Authorization": "token_without_bearer"},
    ]


@pytest.fixture
def password_test_cases() -> List[Dict[str, Any]]:
    """Various password test cases for validation testing"""
    return [
        {"password": "validpassword123", "should_pass": True, "reason": "valid password"},
        {"password": "123", "should_pass": False, "reason": "too short"},
        {"password": "", "should_pass": False, "reason": "empty password"},
        {"password": "a" * 200, "should_pass": False, "reason": "too long"},
        {"password": "password", "should_pass": False, "reason": "too common"},
        {"password": "Password123!", "should_pass": True, "reason": "strong password"},
        {"password": "   spaced   ", "should_pass": False, "reason": "contains spaces"},
        {"password": "日本語パスワード", "should_pass": True, "reason": "unicode characters"},
    ]


@pytest.fixture
def username_test_cases() -> List[Dict[str, Any]]:
    """Various username test cases for validation testing"""
    return [
        {"username": "validuser", "should_pass": True, "reason": "valid username"},
        {"username": "user123", "should_pass": True, "reason": "alphanumeric"},
        {"username": "a", "should_pass": False, "reason": "too short"},
        {"username": "", "should_pass": False, "reason": "empty username"},
        {"username": "a" * 100, "should_pass": False, "reason": "too long"},
        {"username": "user@domain", "should_pass": False, "reason": "contains @"},
        {"username": "user space", "should_pass": False, "reason": "contains space"},
        {"username": "user_123", "should_pass": True, "reason": "underscore allowed"},
        {"username": "user-123", "should_pass": True, "reason": "hyphen allowed"},
        {"username": "123user", "should_pass": True, "reason": "starts with number"},
        {"username": "_user", "should_pass": True, "reason": "starts with underscore"},
        {"username": "-user", "should_pass": False, "reason": "starts with hyphen"},
    ]


@pytest.fixture
def email_test_cases() -> List[Dict[str, Any]]:
    """Various email test cases for validation testing"""
    return [
        {"email": "test@example.com", "should_pass": True, "reason": "valid email"},
        {"email": "user.name@domain.co.uk", "should_pass": True, "reason": "complex valid email"},
        {"email": "test+tag@example.com", "should_pass": True, "reason": "plus addressing"},
        {"email": "notanemail", "should_pass": False, "reason": "missing @"},
        {"email": "@example.com", "should_pass": False, "reason": "missing local part"},
        {"email": "test@", "should_pass": False, "reason": "missing domain"},
        {"email": "test..test@example.com", "should_pass": False, "reason": "double dots"},
        {"email": "test@.com", "should_pass": False, "reason": "domain starts with dot"},
        {"email": "", "should_pass": False, "reason": "empty email"},
        {"email": "test@example", "should_pass": False, "reason": "no TLD"},
        {"email": "test@exam ple.com", "should_pass": False, "reason": "space in domain"},
    ]


@pytest.fixture
def security_test_payloads() -> List[Dict[str, Any]]:
    """Security test payloads for injection testing"""
    return [
        {
            "type": "sql_injection",
            "username": "'; DROP TABLE users; --",
            "password": "password",
            "description": "SQL injection attempt",
        },
        {
            "type": "sql_injection",
            "username": "admin' OR '1'='1",
            "password": "password",
            "description": "SQL injection with OR condition",
        },
        {
            "type": "xss",
            "username": "<script>alert('xss')</script>",
            "password": "password",
            "description": "XSS attempt",
        },
        {
            "type": "command_injection",
            "username": "; rm -rf /",
            "password": "password",
            "description": "Command injection attempt",
        },
        {"type": "ldap_injection", "username": "*)(&", "password": "password", "description": "LDAP injection attempt"},
    ]


@pytest.fixture
def rate_limiting_test_data() -> Dict[str, Any]:
    """Data for rate limiting testing"""
    return {
        "max_attempts": 5,
        "time_window": 300,  # 5 minutes
        "lockout_duration": 900,  # 15 minutes
        "test_credentials": {"username": "ratelimituser", "password": "wrongpassword"},
    }


@pytest.fixture
def session_test_data() -> Dict[str, Any]:
    """Data for session management testing"""
    return {
        "session_timeout": 3600,  # 1 hour
        "refresh_threshold": 300,  # 5 minutes
        "max_concurrent_sessions": 3,
        "remember_me_duration": 2592000,  # 30 days
    }


@pytest.fixture
def mock_user_profile() -> Dict[str, Any]:
    """Mock user profile data for testing"""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "preferred_language": "en",
        "skill_level": "beginner",
        "is_active": True,
        "created_at": datetime.now() - timedelta(days=30),
        "updated_at": datetime.now(),
        "last_login": datetime.now() - timedelta(hours=2),
        "login_count": 15,
        "profile": {
            "display_name": "Test User",
            "bio": "A test user for RepairGPT",
            "location": "Test City",
            "website": "https://test.example.com",
        },
        "preferences": {"theme": "light", "notifications": True, "privacy_level": "public"},
    }
