#!/usr/bin/env python3
"""
JWT Authentication Feature Implementation for Issue #60
Integrates JWT authentication and user management system
"""

import asyncio
import os
from datetime import datetime, timezone
from typing import Dict, Optional

from auth.jwt_auth import (
    JWTAuthManager,
    UserAuth,
    Token,
    get_jwt_manager,
    hash_password,
    verify_password,
    create_access_token,
    decode_token
)
from utils.logger import get_logger

logger = get_logger(__name__)


class AuthenticationFeature:
    """Main feature class for JWT authentication"""
    
    def __init__(self):
        """Initialize authentication feature"""
        self.jwt_manager = get_jwt_manager()
        self.users_db = {}  # In-memory user storage for demo
        logger.info("Authentication Feature initialized")
    
    def register_user(
        self,
        email: str,
        password: str,
        language: str = "en"
    ) -> Dict[str, any]:
        """
        Register new user
        
        Args:
            email: User email
            password: Plain text password
            language: User preferred language
            
        Returns:
            Registration result
        """
        try:
            # Check if user exists
            if email in self.users_db:
                return {
                    "success": False,
                    "error": "User already exists",
                    "issue": 60
                }
            
            # Create user
            user_id = f"user_{len(self.users_db) + 1}"
            hashed_pwd = hash_password(password)
            
            user = UserAuth(
                user_id=user_id,
                email=email,
                hashed_password=hashed_pwd,
                language=language
            )
            
            self.users_db[email] = user
            
            logger.info(f"User registered: {email}")
            return {
                "success": True,
                "user_id": user_id,
                "email": email,
                "issue": 60
            }
            
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "issue": 60
            }
    
    def login_user(self, email: str, password: str) -> Dict[str, any]:
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
                return {
                    "success": False,
                    "error": "Invalid credentials",
                    "issue": 60
                }
            
            # Verify password
            if not verify_password(password, user.hashed_password):
                return {
                    "success": False,
                    "error": "Invalid credentials",
                    "issue": 60
                }
            
            # Check if active
            if not user.is_active:
                return {
                    "success": False,
                    "error": "Account disabled",
                    "issue": 60
                }
            
            # Create tokens
            tokens = self.jwt_manager.create_token_pair(user.user_id)
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            
            logger.info(f"User logged in: {email}")
            return {
                "success": True,
                "tokens": {
                    "access_token": tokens.access_token,
                    "refresh_token": tokens.refresh_token,
                    "token_type": tokens.token_type,
                    "expires_in": tokens.expires_in
                },
                "user": {
                    "user_id": user.user_id,
                    "email": user.email,
                    "language": user.language
                },
                "issue": 60
            }
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "issue": 60
            }
    
    def verify_token(self, token: str) -> Dict[str, any]:
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
                return {
                    "success": False,
                    "error": "Invalid or expired token",
                    "issue": 60
                }
            
            return {
                "success": True,
                "user_id": token_data.sub,
                "token_type": token_data.type,
                "expires_at": token_data.exp.isoformat(),
                "issue": 60
            }
            
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "issue": 60
            }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, any]:
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
                return {
                    "success": False,
                    "error": "Invalid refresh token",
                    "issue": 60
                }
            
            return {
                "success": True,
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": int(self.jwt_manager.access_token_expire.total_seconds()),
                "issue": 60
            }
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "issue": 60
            }
    
    def get_stats(self) -> Dict[str, any]:
        """Get authentication system statistics"""
        return {
            "total_users": len(self.users_db),
            "jwt_algorithm": self.jwt_manager.algorithm,
            "access_token_expire_minutes": int(self.jwt_manager.access_token_expire.total_seconds() / 60),
            "refresh_token_expire_days": int(self.jwt_manager.refresh_token_expire.total_seconds() / 86400),
            "issue": 60
        }


def demo_auth_flow():
    """Demonstrate the authentication flow"""
    feature = AuthenticationFeature()
    
    print("🔐 JWT Authentication Feature Demo")
    print("=" * 50)
    
    # Register user
    print("\n1️⃣ Registering new user...")
    reg_result = feature.register_user(
        email="test@example.com",
        password="SecurePassword123!",
        language="en"
    )
    print(f"   Registration: {'✅ Success' if reg_result['success'] else '❌ Failed'}")
    if reg_result['success']:
        print(f"   User ID: {reg_result['user_id']}")
    
    # Login
    print("\n2️⃣ Logging in...")
    login_result = feature.login_user(
        email="test@example.com",
        password="SecurePassword123!"
    )
    print(f"   Login: {'✅ Success' if login_result['success'] else '❌ Failed'}")
    
    if login_result['success']:
        access_token = login_result['tokens']['access_token']
        refresh_token = login_result['tokens']['refresh_token']
        print(f"   Access Token: {access_token[:20]}...")
        print(f"   Expires in: {login_result['tokens']['expires_in']} seconds")
        
        # Verify token
        print("\n3️⃣ Verifying access token...")
        verify_result = feature.verify_token(access_token)
        print(f"   Verification: {'✅ Valid' if verify_result['success'] else '❌ Invalid'}")
        if verify_result['success']:
            print(f"   User ID: {verify_result['user_id']}")
            print(f"   Expires at: {verify_result['expires_at']}")
        
        # Refresh token
        print("\n4️⃣ Refreshing access token...")
        refresh_result = feature.refresh_token(refresh_token)
        print(f"   Refresh: {'✅ Success' if refresh_result['success'] else '❌ Failed'}")
        if refresh_result['success']:
            print(f"   New Token: {refresh_result['access_token'][:20]}...")
    
    # Show stats
    print("\n📊 Authentication Statistics:")
    stats = feature.get_stats()
    for key, value in stats.items():
        if key != 'issue':
            print(f"   {key}: {value}")


def auto_feature_60():
    """Entry point for auto-generated feature"""
    print("🔐 JWT Authentication and User Management System")
    print("=" * 50)
    
    # Check if JWT secret is configured
    if not os.getenv("JWT_SECRET_KEY"):
        print("⚠️  Warning: JWT_SECRET_KEY not set")
        print("   Using auto-generated key (not for production)")
    
    # Run the demo
    demo_auth_flow()
    
    return {
        "status": "implemented",
        "issue": 60,
        "features": [
            "JWT token generation and validation",
            "User registration and login",
            "Password hashing with bcrypt",
            "Token refresh mechanism",
            "Configurable token expiration",
            "Multi-language user preferences",
            "Secure session management"
        ]
    }


if __name__ == "__main__":
    result = auto_feature_60()
    print(f"\n✅ Feature implementation complete!")
    print(f"   Issue: #{result['issue']}")
    print(f"   Status: {result['status']}")
    print(f"   Features: {len(result['features'])} capabilities")
