"""
Authentication API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, validator

from ...features.auth import AuthenticationFeature
from ...utils.security import sanitize_input

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    language: str = "en"

    @validator("username")
    def validate_username(cls, v):
        if not v or len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return sanitize_input(v, max_length=50)

    @validator("email")
    def validate_email(cls, v):
        import re

        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, v):
            raise ValueError("Invalid email format")
        return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    expires_in: int


@auth_router.post("/register", response_model=AuthResponse)
async def register_user(register_request: RegisterRequest, request: Request):
    """Register a new user"""
    try:
        auth_feature = AuthenticationFeature()
        result = await auth_feature.register_user(
            email=register_request.email,
            password=register_request.password,
            language=register_request.language,
            username=register_request.username,
        )

        if result["success"]:
            return AuthResponse(
                access_token=result["token"]["access_token"],
                user_id=result["user"]["user_id"],
                username=result["user"]["username"],
                expires_in=3600,
            )
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.post("/login", response_model=AuthResponse)
async def login_user(login_request: LoginRequest, request: Request):
    """Login user"""
    try:
        auth_feature = AuthenticationFeature()
        result = await auth_feature.login_user(
            email=login_request.username,
            password=login_request.password,
        )

        if result["success"]:
            return AuthResponse(
                access_token=result["token"]["access_token"],
                user_id=result["user"]["user_id"],
                username=result["user"]["username"],
                expires_in=3600,
            )
        else:
            raise HTTPException(status_code=401, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.get("/me")
async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """Get current user information"""
    try:
        auth_feature = AuthenticationFeature()
        result = await auth_feature.verify_token(credentials.credentials)

        if result["success"]:
            return {"user": result["user"]}
        else:
            raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
