"""
API routes module
Organized route handlers by domain
"""

from .auth import auth_router
from .chat import chat_router
from .devices import devices_router
from .health import health_router

# Skip image_router for now due to multipart dependency
# from .image_analysis import image_router

__all__ = [
    "auth_router",
    "chat_router",
    "devices_router",
    "health_router",
    # "image_router"
]
