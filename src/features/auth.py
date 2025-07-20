"""
Authentication feature module
JWT-based user authentication and management
"""

from datetime import datetime, timezone
from typing import Dict

from ..auth.jwt_auth import (
    UserAuth,
    decode_token,
    get_jwt_manager,
    hash_password,
    verify_password,
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AuthenticationFeature:
    """JWT Authentication and user management system"""

    def __init__(self):
        """Initialize authentication feature"""
        self.jwt_manager = get_jwt_manager()
        self.users_db = {}  # In-memory user storage for demo
        logger.info("Authentication Feature initialized")

    async def register_user(self, email: str, password: str, username: str, language: str = "en") -> Dict[str, any]:
        """
        Register new user

        Args:
            email: User email
            password: Plain text password
            username: Username
            language: User preferred language

        Returns:
            Registration result
        """
        try:
            # Check if user exists
            if email in self.users_db:
                return {"success": False, "error": "User already exists"}

            # Create user
            user_id = f"user_{len(self.users_db) + 1}"
            hashed_pwd = hash_password(password)

            user = UserAuth(
                user_id=user_id,
                email=email,
                hashed_password=hashed_pwd,
                language=language,
            )

            self.users_db[email] = user

            # Create tokens
            tokens = self.jwt_manager.create_token_pair(user_id)

            logger.info(f"User registered: {email}")
            return {
                "success": True,
                "user": {"user_id": user_id, "username": username, "email": email},
                "token": {
                    "access_token": tokens.access_token,
                    "refresh_token": tokens.refresh_token,
                    "token_type": tokens.token_type,
                    "expires_in": tokens.expires_in,
                },
            }

        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return {"success": False, "error": str(e)}

    async def login_user(self, email: str, password: str) -> Dict[str, any]:
        """
        Authenticate user and return tokens

        Args:
            email: User email
            password: Plain text password

        Returns:
            Login result with tokens
        """
        try:
            # Get user
            user = self.users_db.get(email)
            if not user:
                return {"success": False, "error": "Invalid credentials"}

            # Verify password
            if not verify_password(password, user.hashed_password):
                return {"success": False, "error": "Invalid credentials"}

            # Check if active
            if not user.is_active:
                return {"success": False, "error": "Account disabled"}

            # Create tokens
            tokens = self.jwt_manager.create_token_pair(user.user_id)

            # Update last login
            user.last_login = datetime.now(timezone.utc)

            logger.info(f"User logged in: {email}")
            return {
                "success": True,
                "token": {
                    "access_token": tokens.access_token,
                    "refresh_token": tokens.refresh_token,
                    "token_type": tokens.token_type,
                    "expires_in": tokens.expires_in,
                },
                "user": {
                    "user_id": user.user_id,
                    "username": user.email,  # Use email as username for now
                    "email": user.email,
                    "language": user.language,
                },
            }

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return {"success": False, "error": str(e)}

    async def verify_token(self, token: str) -> Dict[str, any]:
        """
        Verify JWT token

        Args:
            token: JWT token to verify

        Returns:
            Verification result
        """
        try:
            token_data = decode_token(token)

            if not token_data:
                return {"success": False, "error": "Invalid or expired token"}

            return {
                "success": True,
                "user": {
                    "user_id": token_data.sub,
                    "token_type": token_data.type,
                    "expires_at": token_data.exp.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return {"success": False, "error": str(e)}

    async def refresh_token(self, refresh_token: str) -> Dict[str, any]:
        """
        Refresh access token

        Args:
            refresh_token: Refresh token

        Returns:
            New access token
        """
        try:
            new_access_token = self.jwt_manager.refresh_access_token(refresh_token)

            if not new_access_token:
                return {"success": False, "error": "Invalid refresh token"}

            return {
                "success": True,
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": int(self.jwt_manager.access_token_expire.total_seconds()),
            }

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return {"success": False, "error": str(e)}

    def get_user_stats(self) -> Dict[str, any]:
        """Get user statistics"""
        return {
            "total_users": len(self.users_db),
            "active_users": sum(1 for user in self.users_db.values() if user.is_active),
        }
