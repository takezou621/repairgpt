"""
RepairGPT Streamlit Application - FALLBACK VERSION
api.health_warning エラーを完全に回避
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List

# Add src directory to path for imports FIRST
current_dir = Path(__file__).parent
src_root = current_dir.parent
sys.path.insert(0, str(src_root))

import requests
import streamlit as st
from PIL import Image

# Safe translation function with hardcoded fallbacks
def safe_translate(key: str, fallback: str = "") -> str:
    """安全な翻訳関数（フォールバック付き）"""
    # Hardcoded translations to avoid any i18n issues
    translations = {
        "api.health_warning": "⚠️ API server is not running. Some features may be limited. Start the API server with: python3 src/api/main.py",
        "app.title": "RepairGPT - AI Repair Assistant",
        "app.tagline": "AI-Powered Electronic Device Repair Assistant",
        "sidebar.device_config": "Device Configuration",
        "sidebar.device_type": "Device Type",
        "sidebar.device_model": "Device Model",
        "sidebar.device_model_help": "Enter your device model for more specific guidance",
        "sidebar.issue_description": "Issue Description",
        "sidebar.issue_description_help": "Describe the problem you're experiencing",
        "sidebar.skill_level": "Skill Level"
    }
    
    if key in translations:
        return translations[key]
    
    # Try original i18n system as backup
    try:
        from i18n import _
        return _(key)
    except:
        return fallback or key

# Import other necessary modules
try:
    from utils.logger import (
        get_logger,
        log_api_call,
        log_api_error,
        log_performance,
        log_user_action,
    )
    from config.settings_simple import settings
    from ui.language_selector import get_localized_device_categories, get_localized_skill_levels
    
except Exception as e:
    st.error(f"Import error: {e}")
    st.stop()

# Get logger instance
logger = get_logger(__name__)

# FastAPI server configuration
API_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
API_TIMEOUT = 30

def check_api_health() -> bool:
    """Check if the FastAPI server is running"""
    try:
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        
        is_healthy = response.status_code == 200
        duration = time.time() - start_time
        
        logger.info(
            "API health check completed",
            extra={
                "extra_data": {
                    "healthy": is_healthy,
                    "duration": duration,
                    "status_code": response.status_code if response else None,
                }
            },
        )
        
        return is_healthy
        
    except Exception as e:
        logger.warning(f"API health check failed: {e}")
        return False

def main():
    """Main Streamlit application"""
    # Page configuration
    st.set_page_config(
        page_title=safe_translate("app.title"),
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Main header
    st.markdown('<h1 class="main-header">🔧 RepairGPT</h1>', unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align: center; margin-bottom: 2rem;'>{safe_translate('app.tagline')}</div>",
        unsafe_allow_html=True,
    )
    
    # API health check with safe translation
    if not check_api_health():
        st.warning(safe_translate("api.health_warning"))
    
    # Sidebar
    with st.sidebar:
        st.subheader(safe_translate("sidebar.device_config"))
        
        device_categories = get_localized_device_categories()
        device_type = st.selectbox(
            safe_translate("sidebar.device_type"),
            options=device_categories,
            index=0,
        )
        
        device_model = st.text_input(
            safe_translate("sidebar.device_model"),
            max_chars=100,
            help=safe_translate("sidebar.device_model_help"),
        )
        
        issue_description = st.text_area(
            safe_translate("sidebar.issue_description"),
            max_chars=500,
            help=safe_translate("sidebar.issue_description_help"),
        )
        
        skill_levels = get_localized_skill_levels()
        skill_level = st.selectbox(
            safe_translate("sidebar.skill_level"),
            options=skill_levels,
            index=0,
        )
    
    # Main content area
    st.write("RepairGPT is ready to help you with device repairs!")
    st.write("This is the fallback version with hardcoded translations to avoid api.health_warning errors.")
    
    if st.button("Test API Health"):
        if check_api_health():
            st.success("API is healthy!")
        else:
            st.warning(safe_translate("api.health_warning"))

if __name__ == "__main__":
    main()
