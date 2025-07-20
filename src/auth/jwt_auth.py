"""
JWT Authentication Implementation for Issue #60
Provides secure JWT token management for user authentication
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """Token payload data"""

    sub: str  # Subject (user_id)
    exp: datetime
    iat: datetime
    type: str = "access"  # "access" or "refresh"


class Token(BaseModel):
    """Token response model"""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = Field(description="Expiration time in seconds")


class UserAuth(BaseModel):
    """User authentication data"""

    user_id: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    language: str = "en"


class JWTAuthManager:
    """JWT Authentication Manager"""

    def __init__(
        self,
        secret_key: str = SECRET_KEY,
        algorithm: str = ALGORITHM,
        access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days: int = REFRESH_TOKEN_EXPIRE_DAYS,
    ):
        """Initialize JWT authentication manager"""
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire = timedelta(minutes=access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=refresh_token_expire_days)

        # Warn if using default secret key
        if secret_key == SECRET_KEY and not os.getenv("JWT_SECRET_KEY"):
            logger.warning(
                "Using default JWT secret key. Set JWT_SECRET_KEY environment variable in production!"
            )

    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    def create_token(
        self,
        user_id: str,
        token_type: str = "access",
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create JWT token

        Args:
            user_id: User identifier
            token_type: Token type (access or refresh)
            additional_claims: Additional JWT claims

        Returns:
            Encoded JWT token
        """
        now = datetime.now(timezone.utc)

        if token_type == "access":
            expire = now + self.access_token_expire
        elif token_type == "refresh":
            expire = now + self.refresh_token_expire
        else:
            raise ValueError(f"Invalid token type: {token_type}")

        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": now,
            "type": token_type,
            "jti": secrets.token_urlsafe(16),  # JWT ID for revocation
        }

        if additional_claims:
            payload.update(additional_claims)

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        logger.info(f"Created {token_type} token for user {user_id}")
        return token

    def create_token_pair(self, user_id: str) -> Token:
        """
        Create access and refresh token pair

        Args:
            user_id: User identifier

        Returns:
            Token object with both tokens
        """
        access_token = self.create_token(user_id, "access")
        refresh_token = self.create_token(user_id, "refresh")

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(self.access_token_expire.total_seconds()),
        )

    def decode_token(self, token: str) -> Optional[TokenData]:
        """
        Decode and validate JWT token

        Args:
            token: JWT token to decode

        Returns:
            TokenData if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Convert timestamps
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)

            return TokenData(
                sub=payload["sub"], exp=exp, iat=iat, type=payload.get("type", "access")
            )

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token decode error: {e}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Create new access token from refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token if refresh token is valid
        """
        token_data = self.decode_token(refresh_token)

        if not token_data:
            return None

        if token_data.type != "refresh":
            logger.warning("Token is not a refresh token")
            return None

        # Create new access token
        return self.create_token(token_data.sub, "access")

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token (requires token blacklist implementation)

        Args:
            token: Token to revoke

        Returns:
            True if revoked successfully
        """
        # TODO: Implement token blacklist storage
        # For now, just decode to validate
        token_data = self.decode_token(token)
        if token_data:
            logger.info(f"Token revoked for user {token_data.sub}")
            return True
        return False


# Global JWT manager instance
_jwt_manager: Optional[JWTAuthManager] = None


def get_jwt_manager() -> JWTAuthManager:
    """Get global JWT manager instance"""
    global _jwt_manager
    if _jwt_manager is None:
        _jwt_manager = JWTAuthManager()
    return _jwt_manager


def reset_jwt_manager():
    """Reset global JWT manager (for testing)"""
    global _jwt_manager
    _jwt_manager = None


# Convenience functions
def hash_password(password: str) -> str:
    """Hash password using global JWT manager"""
    return get_jwt_manager().hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using global JWT manager"""
    return get_jwt_manager().verify_password(plain_password, hashed_password)


def create_access_token(user_id: str) -> str:
    """Create access token using global JWT manager"""
    return get_jwt_manager().create_token(user_id, "access")


def create_refresh_token(user_id: str) -> str:
    """Create refresh token using global JWT manager"""
    return get_jwt_manager().create_token(user_id, "refresh")


def decode_token(token: str) -> Optional[TokenData]:
    """Decode token using global JWT manager"""
    return get_jwt_manager().decode_token(token)
