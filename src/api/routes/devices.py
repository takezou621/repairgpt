"""
Device information API routes
"""

from fastapi import APIRouter, Request

devices_router = APIRouter(prefix="/devices", tags=["Devices"])


@devices_router.get("")
async def get_supported_devices(request: Request):
    """Get list of supported devices in the current language"""
    language = getattr(request.state, "language", "en")

    devices = [
        "nintendo_switch",
        "nintendo_switch_lite",
        "nintendo_switch_oled",
        "iphone",
        "ipad",
        "macbook",
        "imac",
        "playstation_5",
        "playstation_4",
        "xbox_series",
        "xbox_one",
        "samsung_galaxy",
        "google_pixel",
        "gaming_pc",
        "laptop",
        "desktop_pc",
        "other",
    ]

    # For now, return devices as-is
    # In a real implementation, you'd localize these
    return {"devices": devices, "count": len(devices), "language": language}


@devices_router.get("/skill-levels")
async def get_skill_levels(request: Request):
    """Get available skill levels in the current language"""
    language = getattr(request.state, "language", "en")

    skill_levels = ["beginner", "intermediate", "expert"]

    return {
        "skill_levels": skill_levels,
        "count": len(skill_levels),
        "language": language,
    }
