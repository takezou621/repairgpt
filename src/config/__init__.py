"""
Configuration package for RepairGPT
"""

try:
    from .settings import settings
except ImportError:
    # Fallback to simplified settings
    from .settings_simple import settings

__all__ = ["settings"]
