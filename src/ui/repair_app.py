"""
RepairGPT Streamlit Application
Implements Issue #11: Streamlit基本チャットUIの実装
Enhanced with Issue #90: 🔒 設定管理とセキュリティ強化
Enhanced with Issue #89: レスポンシブデザインとUI/UX改善
"""

import streamlit as st
import sys
import os
from datetime import datetime
from typing import Optional, List, Dict
import json
import io
from PIL import Image
import base64
import logging
import requests
import time

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from chat.llm_chatbot import RepairChatbot, RepairContext
    from clients.ifixit_client import IFixitClient, Guide
    from data.offline_repair_database import OfflineRepairDatabase
    from i18n import i18n, _
    from ui.language_selector import language_selector, get_localized_device_categories, get_localized_skill_levels
    
    # Import security and configuration
    from config.settings import settings
    from utils.security import sanitize_input, sanitize_filename, mask_sensitive_data
    
    # Import responsive design components
    from ui.responsive_design import initialize_responsive_design, enhance_ui_components
    from ui.ui_enhancements import show_responsive_design_info, add_responsive_navigation_hints
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Configure logging
logger = logging.getLogger(__name__)

# FastAPI server configuration
API_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
API_TIMEOUT = 30


def call_chat_api(message: str, device_context: Dict = None) -> str:
    """Call the FastAPI chat endpoint with security validation"""
    try:
        # Sanitize input message
        safe_message = sanitize_input(message, max_length=settings.max_text_length)
        
        payload = {
            "message": safe_message,
            "language": st.session_state.language
        }
        
        # Add device context if available
        if device_context:
            payload.update({
                "device_type": device_context.get("device_type"),
                "device_model": sanitize_input(device_context.get("device_model", ""), max_length=100) if device_context.get("device_model") else None,
                "issue_description": sanitize_input(device_context.get("issue_description", ""), max_length=500) if device_context.get("issue_description") else None,
                "skill_level": device_context.get("skill_level", "beginner")
            })
        
        response = requests.post(
            f"{API_BASE_URL}{settings.api_prefix}/chat",
            json=payload,
            timeout=API_TIMEOUT,
            headers={"Accept-Language": st.session_state.language}
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            error_msg = f"API Error {response.status_code}: {response.text}"
            logger.error(f"Chat API error: {mask_sensitive_data(error_msg)}")
            st.error(error_msg)
            return f"Sorry, I encountered an error: {error_msg}"
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        logger.error(f"Chat API connection error: {mask_sensitive_data(error_msg)}")
        st.error(error_msg)
        return f"Sorry, I couldn't connect to the repair service: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Chat API unexpected error: {mask_sensitive_data(error_msg)}")
        st.error(error_msg)
        return f"Sorry, something went wrong: {error_msg}"


def call_diagnose_api(device_type: str, issue_description: str, device_model: str = None, 
                     symptoms: List[str] = None, skill_level: str = "beginner") -> Dict:
    """Call the FastAPI diagnose endpoint with security validation"""
    try:
        payload = {
            "device_type": device_type,
            "issue_description": sanitize_input(issue_description, max_length=1000),
            "skill_level": skill_level,
            "language": st.session_state.language
        }
        
        if device_model:
            payload["device_model"] = sanitize_input(device_model, max_length=100)
        if symptoms:
            payload["symptoms"] = [sanitize_input(symptom, max_length=200) for symptom in symptoms[:10]]  # Limit to 10 symptoms
            
        response = requests.post(
            f"{API_BASE_URL}{settings.api_prefix}/diagnose",
            json=payload,
            timeout=API_TIMEOUT,
            headers={"Accept-Language": st.session_state.language}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"Diagnosis API Error {response.status_code}: {response.text}"
            logger.error(f"Diagnose API error: {mask_sensitive_data(error_msg)}")
            st.error(error_msg)
            return None
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        logger.error(f"Diagnose API connection error: {mask_sensitive_data(error_msg)}")
        st.error(error_msg)
        return None
    except Exception as e:
        error_msg = f"Diagnosis error: {str(e)}"
        logger.error(f"Diagnose API unexpected error: {mask_sensitive_data(error_msg)}")
        st.error(error_msg)
        return None


def check_api_health() -> bool:
    """Check if the FastAPI server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}{settings.api_prefix}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


# Initialize i18n and set default language from session state
if 'language' not in st.session_state:
    st.session_state.language = 'en'
i18n.set_language(st.session_state.language)

# Page configuration with security settings
st.set_page_config(
    page_title=f"{settings.app_name} - {_('app.title')}",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize responsive design
responsive_design = initialize_responsive_design()

# Custom CSS with responsive design
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .device-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4ECDC4;
        margin: 1rem 0;
    }
    
    .safety-warning {
        background: #fff3cd;
        border: 1px solid #ffecb5;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .step-container {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #28a745;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        max-width: 100%;
        word-wrap: break-word;
    }
    
    .user-message {
        background: #007bff;
        color: white;
        margin-left: 2rem;
    }
    
    .bot-message {
        background: #f1f3f4;
        color: #333;
        margin-right: 2rem;
    }
    
    /* Responsive improvements */
    @media (max-width: 768px) {
        .user-message, .bot-message {
            margin-left: 0.5rem;
            margin-right: 0.5rem;
            padding: 0.75rem;
        }
        
        .main-header {
            font-size: 2rem;
            padding: 0.5rem 0;
        }
        
        .device-card, .safety-warning, .step-container {
            padding: 0.75rem;
            margin: 0.75rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application function with security and responsive design"""
    # Enhanced responsive UI components
    enhance_ui_components()
    
    # Main header with responsive design
    st.markdown('<h1 class="main-header">🔧 RepairGPT</h1>', unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; margin-bottom: 2rem;'>{_('app.tagline')}</div>", unsafe_allow_html=True)
    
    # API health check
    if not check_api_health():
        st.warning(_("api.health_warning"))
    
    # Sidebar with enhanced navigation
    with st.sidebar:
        add_responsive_navigation_hints()
        
        # Language selector
        selected_language = language_selector()
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            i18n.set_language(selected_language)
            st.rerun()
        
        st.markdown("---")
        
        # Device configuration with security validation
        st.subheader(_("sidebar.device_config"))
        
        device_categories = get_localized_device_categories()
        device_type = st.selectbox(
            _("sidebar.device_type"),
            options=list(device_categories.keys()),
            format_func=lambda x: device_categories[x]
        )
        
        device_model = st.text_input(
            _("sidebar.device_model"),
            max_chars=100,
            help=_("sidebar.device_model_help")
        )
        
        issue_description = st.text_area(
            _("sidebar.issue_description"),
            max_chars=500,
            help=_("sidebar.issue_description_help")
        )
        
        skill_levels = get_localized_skill_levels()
        skill_level = st.selectbox(
            _("sidebar.skill_level"),
            options=list(skill_levels.keys()),
            format_func=lambda x: skill_levels[x]
        )
        
        st.markdown("---")
        
        # Features section
        st.subheader(_("sidebar.features"))
        show_chat = st.checkbox(_("sidebar.show_chat"), value=True)
        show_guides = st.checkbox(_("sidebar.show_guides"))
        show_diagnosis = st.checkbox(_("sidebar.show_diagnosis"))
        show_image_analysis = st.checkbox(_("sidebar.show_image_analysis"))
        
        if settings.debug:
            st.markdown("---")
            st.subheader("🔒 Security Info")
            st.info(f"Environment: {settings.environment.value}")
            st.info(f"Security Headers: {'✅' if settings.enable_security_headers else '❌'}")
    
    # Main content area with responsive layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        if show_chat:
            st.subheader(_("chat.title"))
            
            # Initialize chat history
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            
            # Chat input with security validation
            user_message = st.chat_input(
                _("chat.input_placeholder"),
                max_chars=settings.max_text_length
            )
            
            if user_message:
                # Sanitize and validate input
                safe_message = sanitize_input(user_message, max_length=settings.max_text_length)
                
                # Add to chat history
                st.session_state.chat_history.append({"role": "user", "content": safe_message})
                
                # Get device context
                device_context = {
                    "device_type": device_type,
                    "device_model": device_model,
                    "issue_description": issue_description,
                    "skill_level": skill_level
                }
                
                # Get AI response
                with st.spinner(_("chat.thinking")):
                    ai_response = call_chat_api(safe_message, device_context)
                
                # Add AI response to history
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            
            # Display chat history
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message bot-message">{message["content"]}</div>', unsafe_allow_html=True)
            
            # Clear chat button
            if st.session_state.chat_history:
                if st.button(_("chat.clear_history")):
                    st.session_state.chat_history = []
                    st.rerun()
        
        # Diagnosis feature
        if show_diagnosis and issue_description:
            st.subheader(_("diagnosis.title"))
            
            if st.button(_("diagnosis.start_button")):
                with st.spinner(_("diagnosis.analyzing")):
                    symptoms = issue_description.split(",") if "," in issue_description else [issue_description]
                    diagnosis_result = call_diagnose_api(
                        device_type=device_type,
                        issue_description=issue_description,
                        device_model=device_model,
                        symptoms=symptoms,
                        skill_level=skill_level
                    )
                
                if diagnosis_result:
                    st.success(_("diagnosis.completed"))
                    
                    # Display diagnosis results
                    if "analysis" in diagnosis_result:
                        analysis = diagnosis_result["analysis"]
                        
                        # Primary issue
                        if "primary_issue" in analysis:
                            st.markdown(f"**{_('diagnosis.primary_issue')}:** {analysis['primary_issue']}")
                        
                        # Severity
                        if "severity" in analysis:
                            severity_color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}.get(analysis["severity"], "⚪")
                            st.markdown(f"**{_('diagnosis.severity')}:** {severity_color} {analysis['severity']}")
                        
                        # Confidence
                        if "confidence" in analysis:
                            confidence_percent = int(analysis["confidence"] * 100)
                            st.progress(analysis["confidence"])
                            st.caption(f"{_('diagnosis.confidence')}: {confidence_percent}%")
        
        # Image analysis feature
        if show_image_analysis:
            st.subheader(_("image_analysis.title"))
            
            uploaded_file = st.file_uploader(
                _("image_analysis.upload"),
                type=list(settings.allowed_file_types),
                help=f"{_('image_analysis.help')} ({settings.max_image_size_mb}MB max)"
            )
            
            if uploaded_file:
                # Validate file size
                if uploaded_file.size > settings.max_image_size_mb * 1024 * 1024:
                    st.error(f"{_('image_analysis.file_too_large')} ({settings.max_image_size_mb}MB)")
                else:
                    # Display image
                    image = Image.open(uploaded_file)
                    st.image(image, caption=_("image_analysis.uploaded_image"), use_column_width=True)
                    
                    if st.button(_("image_analysis.analyze_button")):
                        st.info(_("image_analysis.feature_coming_soon"))
    
    with col2:
        # Repair guides
        if show_guides:
            st.subheader(_("guides.title"))
            
            # Search guides
            search_query = st.text_input(
                _("guides.search_placeholder"),
                max_chars=100
            )
            
            if search_query:
                safe_query = sanitize_input(search_query, max_length=100)
                
                with st.spinner(_("guides.searching")):
                    try:
                        # Initialize databases
                        offline_db = OfflineRepairDatabase()
                        
                        # Search offline guides
                        guides = offline_db.search_guides(safe_query, device_type, limit=5)
                        
                        if guides:
                            for guide in guides:
                                with st.expander(f"🔧 {guide.title}"):
                                    st.markdown(f"**{_('guides.difficulty')}:** {guide.difficulty}")
                                    st.markdown(f"**{_('guides.time_estimate')}:** {guide.time_estimate}")
                                    
                                    if guide.summary:
                                        st.markdown(f"**{_('guides.summary')}:** {guide.summary}")
                                    
                                    if guide.tools_required:
                                        st.markdown(f"**{_('guides.tools_required')}:**")
                                        for tool in guide.tools_required:
                                            st.markdown(f"- {tool}")
                                    
                                    if guide.warnings:
                                        for warning in guide.warnings:
                                            st.warning(f"⚠️ {warning}")
                        else:
                            st.info(_("guides.no_results"))
                    
                    except Exception as e:
                        logger.error(f"Guide search error: {mask_sensitive_data(str(e))}")
                        st.error(_("guides.search_error"))
        
        # Responsive design info
        if settings.debug:
            show_responsive_design_info()


if __name__ == "__main__":
    main()