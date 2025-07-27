"""
RepairGPT Streamlit Application
Implements Issue #11: Streamlit基本チャットUIの実装
Enhanced with Issue #90: 🔒 設定管理とセキュリティ強化
Enhanced with Issue #89: レスポンシブデザインとUI/UX改善
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

import requests  # noqa: E402
import streamlit as st  # noqa: E402
from PIL import Image  # noqa: E402

from services.repair_guide_service import (  # noqa: E402
    SearchFilters,
    get_repair_guide_service,
)
from utils.japanese_device_mapper import (  # noqa: E402
    get_mapper,
    map_japanese_device,
)
from utils.logger import (  # noqa: E402
    get_logger,
    log_api_call,
    log_api_error,
    log_performance,
    log_user_action,
)

# Conditional imports with fallbacks to prevent circular dependencies
try:
    from config.settings import settings
except ImportError:
    # Fallback settings
    class FallbackSettings:
        app_name = "RepairGPT"
        debug = False
        environment = "development"
        max_text_length = 5000
        max_image_size_mb = 10
        allowed_file_types = ["jpg", "jpeg", "png"]
        api_prefix = "/api/v1"
        enable_security_headers = True

    settings = FallbackSettings()

try:
    from data.offline_repair_database import OfflineRepairDatabase
except ImportError:
    OfflineRepairDatabase = None

try:
    from utils.security import mask_sensitive_data, sanitize_input
except ImportError:

    def mask_sensitive_data(data):
        return data

    def sanitize_input(text, max_length=5000):
        return str(text)[:max_length] if text else ""


try:
    from i18n import _, i18n
except ImportError:

    def _(key, **kwargs):
        return key.format(**kwargs) if kwargs else key

    class MockI18n:
        def set_language(self, lang):
            pass

    i18n = MockI18n()

# Import UI components with fallbacks
try:
    from ui.language_selector import (
        get_localized_device_categories,
        get_localized_skill_levels,
        language_selector,
    )
except ImportError:
    try:
        from language_selector import (
            get_localized_device_categories,
            get_localized_skill_levels,
            language_selector,
        )
    except ImportError:
        # Fallback functions
        def language_selector():
            return "en"

        def get_localized_device_categories():
            return ["Select device", "Nintendo Switch", "iPhone", "PlayStation", "Laptop", "Desktop PC"]

        def get_localized_skill_levels():
            return ["Beginner", "Intermediate", "Expert"]


# Import responsive design components with fallbacks
try:
    from ui.responsive_design import (
        enhance_ui_components,
        initialize_responsive_design,
    )
    from ui.ui_enhancements import (
        add_responsive_navigation_hints,
        show_responsive_design_info,
    )
except ImportError:
    try:
        from responsive_design import (
            enhance_ui_components,
            initialize_responsive_design,
        )
        from ui_enhancements import (
            add_responsive_navigation_hints,
            show_responsive_design_info,
        )
    except ImportError:
        # Fallback functions if responsive design modules are not available
        def enhance_ui_components():
            return {}

        def initialize_responsive_design():
            return {}

        def add_responsive_navigation_hints():
            pass

        def show_responsive_design_info():
            pass


# Get logger instance
logger = get_logger(__name__)

# FastAPI server configuration
API_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
API_TIMEOUT = 30


# Japanese search functionality
def preprocess_japanese_search_query(query: str) -> str:
    """
    Preprocess Japanese search query to enhance search results.

    Args:
        query: Search query that may contain Japanese text

    Returns:
        Preprocessed query with Japanese device names converted to English
    """
    if not query:
        return query

    try:
        japanese_mapper = get_mapper()

        # Split query into words for processing
        import re

        words = re.split(r"[\s\u3000]+", query.strip())  # Split on spaces and full-width spaces
        processed_words = []

        for word in words:
            if not word:
                continue

            # Try direct device mapping first
            english_device = japanese_mapper.map_device_name(word)
            if english_device:
                processed_words.append(english_device)
                continue

            # Try fuzzy matching for partial matches
            fuzzy_result = japanese_mapper.find_best_match(word, threshold=0.7)
            if fuzzy_result:
                device_name, confidence = fuzzy_result
                processed_words.append(device_name)
                continue

            # If no device mapping found, keep original word
            processed_words.append(word)

        # Join processed words back into query
        processed_query = " ".join(processed_words)

        if processed_query != query:
            logger.info(f"Japanese query preprocessed: '{query}' -> '{processed_query}'")

        return processed_query

    except Exception as e:
        logger.warning(f"Japanese query preprocessing failed: {e}")
        return query


def get_japanese_search_suggestions() -> List[str]:
    """
    Get commonly used Japanese search queries for suggestions.

    Returns:
        List of Japanese search query suggestions
    """
    return [
        "スイッチ 画面割れ",
        "アイフォン バッテリー交換",
        "ノートパソコン 電源が入らない",
        "プレステ5 冷却ファン",
        "Joy-Con ドリフト",
        "マックブック キーボード修理",
        "iPad 充電できない",
        "スマホ 水没修理",
        "ゲーム機 読み込みエラー",
        "ヘッドフォン 音が出ない",
    ]


def normalize_japanese_filter_values(filters: Dict[str, str]) -> Dict[str, str]:
    """
    Normalize Japanese filter values to their English equivalents.

    Args:
        filters: Dictionary of filter values that may contain Japanese text

    Returns:
        Dictionary with normalized filter values
    """
    normalized = filters.copy()

    # Japanese difficulty mappings
    japanese_difficulty_map = {
        "初心者": "beginner",
        "中級者": "intermediate",
        "上級者": "expert",
        "簡単": "easy",
        "普通": "moderate",
        "難しい": "difficult",
    }

    # Japanese category mappings
    japanese_category_map = {
        "画面修理": "screen repair",
        "バッテリー交換": "battery replacement",
        "基板修理": "motherboard repair",
        "充電器修理": "charger repair",
        "ボタン修理": "button repair",
        "スピーカー修理": "speaker repair",
        "カメラ修理": "camera repair",
        "キーボード修理": "keyboard repair",
        "水没修理": "water damage repair",
    }

    # Normalize difficulty
    if "difficulty" in normalized and normalized["difficulty"] in japanese_difficulty_map:
        normalized["difficulty"] = japanese_difficulty_map[normalized["difficulty"]]

    # Normalize category
    if "category" in normalized and normalized["category"] in japanese_category_map:
        normalized["category"] = japanese_category_map[normalized["category"]]

    # Normalize device type using Japanese mapper
    if "device_type" in normalized and normalized["device_type"]:
        mapped_device = map_japanese_device(normalized["device_type"])
        if mapped_device:
            normalized["device_type"] = mapped_device

    return normalized


# Safe translation function with hardcoded fallbacks
def safe_translate(key: str, fallback: str = "") -> str:
    """安全な翻訳関数（フォールバック付き）"""
    # Hardcoded translations to avoid any i18n issues
    translations = {
        "api.health_warning": (
            "⚠️ API server is not running. Some features may be limited. "
            "Start the API server with: python3 src/api/main.py"
        ),
        "app.title": "RepairGPT - AI Repair Assistant",
        "app.tagline": "AI-Powered Electronic Device Repair Assistant",
        "sidebar.device_config": "Device Configuration",
        "sidebar.device_type": "Device Type",
        "sidebar.device_model": "Device Model",
        "sidebar.device_model_help": "Enter your device model for more specific guidance",
        "sidebar.issue_description": "Issue Description",
        "sidebar.issue_description_help": "Describe the problem you're experiencing",
        "sidebar.skill_level": "Skill Level",
        "chat.title": "💬 Chat with RepairGPT",
        "chat.input_placeholder": "Describe your repair issue or ask a question...",
        "chat.thinking": "RepairGPT is thinking...",
        "chat.clear_history": "Clear Chat History",
        # Japanese search functionality translations
        "search.title": "🔍 Smart Search",
        "search.japanese_input": "Japanese Search Input",
        "search.input_placeholder": "Enter device and issue (supports Japanese)",
        "search.input_placeholder_japanese": "例: スイッチ 画面割れ",
        "search.suggestions": "Search Suggestions",
        "search.filters": "Search Filters",
        "search.difficulty": "Difficulty Level",
        "search.category": "Repair Category",
        "search.device_filter": "Device Type Filter",
        "search.searching": "Searching repair guides...",
        "search.results_found": "Found {count} repair guides",
        "search.no_results": "No repair guides found",
        "search.error": "Search error occurred",
        "search.mapping_quality": "Mapping Quality",
        "search.confidence": "Confidence",
        "search.source": "Source",
        "search.last_updated": "Last Updated",
        "search.processing_time": "Processing Time",
        "search.history": "Search History",
        "search.bookmarks": "Bookmarks",
        "search.clear_history": "Clear History",
        "search.save_bookmark": "Save Bookmark",
        "search.remove_bookmark": "Remove Bookmark",
    }

    if key in translations:
        return translations[key]

    # Try original i18n system as backup
    try:
        from i18n import _

        return _(key)
    except (ImportError, Exception):
        return fallback or key


def call_chat_api(message: str, device_context: Dict = None) -> str:
    """Call the FastAPI chat endpoint with security validation"""
    start_time = time.time()

    # Log user action
    log_user_action(
        logger,
        "chat_request",
        message_length=len(message),
        has_device_context=bool(device_context),
    )

    try:
        # Sanitize input message
        safe_message = sanitize_input(message, max_length=settings.max_text_length)

        payload = {"message": safe_message, "language": st.session_state.language}

        # Add device context if available
        if device_context:
            payload.update(
                {
                    "device_type": device_context.get("device_type"),
                    "device_model": (
                        sanitize_input(device_context.get("device_model", ""), max_length=100)
                        if device_context.get("device_model")
                        else None
                    ),
                    "issue_description": (
                        sanitize_input(device_context.get("issue_description", ""), max_length=500)
                        if device_context.get("issue_description")
                        else None
                    ),
                    "skill_level": device_context.get("skill_level", "beginner"),
                }
            )

        # Log API call
        log_api_call(
            logger,
            f"{settings.api_prefix}/chat",
            "POST",
            language=st.session_state.language,
            message_length=len(safe_message),
        )

        response = requests.post(
            f"{API_BASE_URL}{settings.api_prefix}/chat",
            json=payload,
            timeout=API_TIMEOUT,
            headers={"Accept-Language": st.session_state.language},
        )

        if response.status_code == 200:
            result = response.json()["response"]

            # Log successful completion
            duration = time.time() - start_time
            log_performance(
                logger,
                "chat_api_call",
                duration,
                response_length=len(result),
                status_code=response.status_code,
            )

            logger.info(
                "Chat API call successful",
                extra={
                    "extra_data": {
                        "message_length": len(safe_message),
                        "response_length": len(result),
                        "duration_ms": duration * 1000,
                        "language": st.session_state.language,
                    }
                },
            )

            return result
        else:
            error_msg = f"API Error {response.status_code}: {response.text}"
            mask_sensitive_data(error_msg)

            log_api_error(
                logger,
                f"{settings.api_prefix}/chat",
                Exception(error_msg),
                status_code=response.status_code,
            )

            st.error(f"Chat service error: {response.status_code}")
            return "Sorry, I encountered an error. Please try again later."

    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        duration = time.time() - start_time

        log_api_error(
            logger,
            f"{settings.api_prefix}/chat",
            e,
            connection_error=True,
            duration=duration,
        )

        st.error("Unable to connect to chat service")
        return "Sorry, I couldn't connect to the repair service. Please check your internet connection and try again."
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        duration = time.time() - start_time

        logger.error(
            "Chat API unexpected error",
            exc_info=True,
            extra={
                "extra_data": {
                    "error_type": type(e).__name__,
                    "duration": duration,
                    "message_length": len(message) if message else 0,
                }
            },
        )

        st.error("An unexpected error occurred")
        return "Sorry, something went wrong. Please try again."


def call_diagnose_api(
    device_type: str,
    issue_description: str,
    device_model: str = None,
    symptoms: List[str] = None,
    skill_level: str = "beginner",
) -> Dict:
    """Call the FastAPI diagnose endpoint with security validation"""
    start_time = time.time()

    # Log user action
    log_user_action(
        logger,
        "diagnosis_request",
        device_type=device_type,
        issue_length=len(issue_description),
        has_symptoms=bool(symptoms),
        skill_level=skill_level,
    )

    try:
        payload = {
            "device_type": device_type,
            "issue_description": sanitize_input(issue_description, max_length=1000),
            "skill_level": skill_level,
            "language": st.session_state.language,
        }

        if device_model:
            payload["device_model"] = sanitize_input(device_model, max_length=100)
        if symptoms:
            payload["symptoms"] = [
                sanitize_input(symptom, max_length=200) for symptom in symptoms[:10]
            ]  # Limit to 10 symptoms

        # Log API call
        log_api_call(
            logger,
            f"{settings.api_prefix}/diagnose",
            "POST",
            device_type=device_type,
            language=st.session_state.language,
            symptoms_count=len(symptoms) if symptoms else 0,
        )

        response = requests.post(
            f"{API_BASE_URL}{settings.api_prefix}/diagnose",
            json=payload,
            timeout=API_TIMEOUT,
            headers={"Accept-Language": st.session_state.language},
        )

        if response.status_code == 200:
            result = response.json()

            # Log successful completion
            duration = time.time() - start_time
            log_performance(
                logger,
                "diagnose_api_call",
                duration,
                status_code=response.status_code,
                device_type=device_type,
            )

            logger.info(
                "Diagnosis API call successful",
                extra={
                    "extra_data": {
                        "device_type": device_type,
                        "duration_ms": duration * 1000,
                        "language": st.session_state.language,
                        "has_analysis": "analysis" in result,
                    }
                },
            )

            return result
        else:
            error_msg = f"Diagnosis API Error {response.status_code}: {response.text}"

            log_api_error(
                logger,
                f"{settings.api_prefix}/diagnose",
                Exception(error_msg),
                status_code=response.status_code,
                device_type=device_type,
            )

            st.error(f"Diagnosis service error: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        duration = time.time() - start_time

        log_api_error(
            logger,
            f"{settings.api_prefix}/diagnose",
            e,
            connection_error=True,
            duration=duration,
            device_type=device_type,
        )

        st.error("Unable to connect to diagnosis service")
        return None
    except Exception as e:
        duration = time.time() - start_time

        logger.error(
            "Diagnosis API unexpected error",
            exc_info=True,
            extra={
                "extra_data": {
                    "error_type": type(e).__name__,
                    "duration": duration,
                    "device_type": device_type,
                }
            },
        )

        st.error("An unexpected error occurred during diagnosis")
        return None


def check_api_health() -> bool:
    """Check if the FastAPI server is running"""
    try:
        start_time = time.time()
        # Use the correct /health endpoint (not /api/v1/health)
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)

        is_healthy = response.status_code == 200
        duration = time.time() - start_time

        logger.info(
            "API health check completed",
            extra={
                "extra_data": {
                    "healthy": is_healthy,
                    "status_code": response.status_code,
                    "duration_ms": duration * 1000,
                    "api_url": API_BASE_URL,
                }
            },
        )

        return is_healthy

    except Exception as e:
        logger.warning(
            "API health check failed",
            extra={
                "extra_data": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "api_url": API_BASE_URL,
                }
            },
        )
        return False


# Initialize i18n and set default language from session state
if "language" not in st.session_state:
    st.session_state.language = "en"

try:
    i18n.set_language(st.session_state.language)
except NameError:
    # i18n not available, use fallback
    pass

# Page configuration with security settings
st.set_page_config(
    page_title=f"{settings.app_name} - {safe_translate('app.title')}",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize responsive design (safely)
try:
    responsive_design = initialize_responsive_design()
except NameError:
    responsive_design = {}

# Custom CSS with responsive design
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


def main():
    """Main application function with security and responsive design"""
    # Log application startup
    logger.info(
        "RepairGPT application starting",
        extra={
            "extra_data": {
                "language": st.session_state.get("language", "en"),
                "api_base_url": API_BASE_URL,
                "debug_mode": settings.debug,
            }
        },
    )

    # Enhanced responsive UI components
    enhance_ui_components()

    # Main header with responsive design
    st.markdown('<h1 class="main-header">🔧 RepairGPT</h1>', unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align: center; margin-bottom: 2rem;'>{safe_translate('app.tagline')}</div>",
        unsafe_allow_html=True,
    )

    # API health check
    if not check_api_health():
        st.warning(safe_translate("api.health_warning"))

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
            st.subheader(safe_translate("chat.title"))

            # Initialize chat history
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            # Chat input with security validation
            user_message = st.chat_input(safe_translate("chat.input_placeholder"), max_chars=settings.max_text_length)

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
                    "skill_level": skill_level,
                }

                # Get AI response
                with st.spinner(safe_translate("chat.thinking")):
                    ai_response = call_chat_api(safe_message, device_context)

                # Add AI response to history
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

            # Display chat history
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(
                        f'<div class="chat-message user-message">{message["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="chat-message bot-message">{message["content"]}</div>',
                        unsafe_allow_html=True,
                    )

            # Clear chat button
            if st.session_state.chat_history:
                if st.button(safe_translate("chat.clear_history")):
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
                        skill_level=skill_level,
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
                            severity_color = {
                                "LOW": "🟢",
                                "MEDIUM": "🟡",
                                "HIGH": "🔴",
                            }.get(analysis["severity"], "⚪")
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
                help=f"{_('image_analysis.help')} ({settings.max_image_size_mb}MB max)",
            )

            if uploaded_file:
                # Validate file size
                if uploaded_file.size > settings.max_image_size_mb * 1024 * 1024:
                    st.error(f"{_('image_analysis.file_too_large')} ({settings.max_image_size_mb}MB)")
                else:
                    # Display image
                    image = Image.open(uploaded_file)
                    st.image(
                        image,
                        caption=_("image_analysis.uploaded_image"),
                        use_column_width=True,
                    )

                    if st.button(_("image_analysis.analyze_button")):
                        st.info(_("image_analysis.feature_coming_soon"))

    with col2:
        # Enhanced Repair guides with Japanese search
        if show_guides:
            st.subheader(safe_translate("search.title", "🔍 Smart Search"))

            # Initialize session state for search features
            if "search_history" not in st.session_state:
                st.session_state.search_history = []
            if "search_bookmarks" not in st.session_state:
                st.session_state.search_bookmarks = []
            if "last_search_time" not in st.session_state:
                st.session_state.last_search_time = None

            # Language-aware search input
            current_lang = st.session_state.get("language", "en")
            if current_lang == "ja":
                placeholder_text = safe_translate("search.input_placeholder_japanese", "例: スイッチ 画面割れ")
            else:
                placeholder_text = safe_translate(
                    "search.input_placeholder", "Enter device and issue (supports Japanese)"
                )

            # Main search input with enhanced features
            col_search, col_suggest = st.columns([3, 1])

            with col_search:
                search_query = st.text_input(
                    safe_translate("search.japanese_input", "Smart Search"),
                    placeholder=placeholder_text,
                    max_chars=200,
                    key="main_search_input",
                )

            with col_suggest:
                if st.button("💡 Suggestions", key="search_suggestions_btn"):
                    suggestions = get_japanese_search_suggestions()
                    selected_suggestion = st.selectbox(
                        safe_translate("search.suggestions", "Suggestions"),
                        ["Select suggestion..."] + suggestions,
                        key="suggestion_selector",
                    )
                    if selected_suggestion != "Select suggestion...":
                        st.session_state.main_search_input = selected_suggestion
                        st.rerun()

            # Advanced search filters with Japanese support
            with st.expander(safe_translate("search.filters", "🔧 Advanced Filters")):
                filter_col1, filter_col2, filter_col3 = st.columns(3)

                with filter_col1:
                    if current_lang == "ja":
                        difficulty_options = ["すべて", "初心者", "中級者", "上級者"]
                    else:
                        difficulty_options = ["All", "Beginner", "Intermediate", "Expert"]

                    difficulty_filter = st.selectbox(
                        safe_translate("search.difficulty", "Difficulty"), difficulty_options, key="difficulty_filter"
                    )

                with filter_col2:
                    if current_lang == "ja":
                        category_options = [
                            "すべて",
                            "画面修理",
                            "バッテリー交換",
                            "基板修理",
                            "ボタン修理",
                            "充電器修理",
                            "水没修理",
                        ]
                    else:
                        category_options = [
                            "All",
                            "Screen Repair",
                            "Battery Replacement",
                            "Motherboard Repair",
                            "Button Repair",
                            "Charger Repair",
                            "Water Damage",
                        ]

                    category_filter = st.selectbox(
                        safe_translate("search.category", "Category"), category_options, key="category_filter"
                    )

                with filter_col3:
                    device_filter = st.selectbox(
                        safe_translate("search.device_filter", "Device Filter"),
                        ["All Devices"] + get_localized_device_categories()[1:],  # Skip "Select device"
                        key="device_filter",
                    )

            # Search execution and results
            if search_query:
                start_time = time.time()
                safe_query = sanitize_input(search_query, max_length=200)

                # Preprocess Japanese query
                processed_query = preprocess_japanese_search_query(safe_query)

                # Normalize filter values
                filter_values = {
                    "difficulty": (
                        difficulty_filter if difficulty_filter != "All" and difficulty_filter != "すべて" else None
                    ),
                    "category": category_filter if category_filter != "All" and category_filter != "すべて" else None,
                    "device_type": device_filter if device_filter != "All Devices" else None,
                }
                normalized_filters = normalize_japanese_filter_values(filter_values)

                with st.spinner(safe_translate("search.searching", "Searching repair guides...")):
                    try:
                        # Initialize repair guide service
                        repair_service = get_repair_guide_service()

                        # Create search filters
                        search_filters = SearchFilters(
                            device_type=normalized_filters.get("device_type"),
                            difficulty_level=normalized_filters.get("difficulty"),
                            category=normalized_filters.get("category"),
                            language=current_lang,
                        )

                        # Perform search using the repair guide service
                        import asyncio

                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        try:
                            search_results = loop.run_until_complete(
                                repair_service.search_guides(query=processed_query, filters=search_filters, limit=8)
                            )
                        finally:
                            loop.close()

                        processing_time = time.time() - start_time
                        st.session_state.last_search_time = processing_time

                        # Add to search history
                        if search_query not in st.session_state.search_history:
                            st.session_state.search_history.insert(0, search_query)
                            # Keep only last 10 searches
                            st.session_state.search_history = st.session_state.search_history[:10]

                        # Display search results with enhanced information
                        if search_results:
                            # Search metrics
                            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                            with metrics_col1:
                                st.metric("Results Found", len(search_results))
                            with metrics_col2:
                                avg_confidence = sum(r.confidence_score for r in search_results) / len(search_results)
                                st.metric("Avg Confidence", f"{avg_confidence:.2f}")
                            with metrics_col3:
                                st.metric("Processing Time", f"{processing_time:.2f}s")

                            st.success(
                                safe_translate("search.results_found", "Found {count} repair guides").format(
                                    count=len(search_results)
                                )
                            )

                            # Display results with enhanced layout
                            for i, result in enumerate(search_results):
                                guide = result.guide

                                # Create expandable guide section with quality indicators
                                quality_indicator = (
                                    "🟢"
                                    if result.confidence_score > 0.8
                                    else "🟡" if result.confidence_score > 0.6 else "🔴"
                                )
                                source_icon = (
                                    "🌐" if result.source == "ifixit" else "💾" if result.source == "offline" else "📋"
                                )

                                with st.expander(f"{quality_indicator} {source_icon} {guide.title}"):
                                    # Guide metadata
                                    info_col1, info_col2, info_col3 = st.columns(3)

                                    with info_col1:
                                        st.markdown(f"**{_('guides.difficulty')}:** {guide.difficulty}")
                                        if hasattr(guide, "time_estimate") and guide.time_estimate:
                                            st.markdown(f"**Time:** {guide.time_estimate}")

                                    with info_col2:
                                        st.markdown(
                                            f"**{safe_translate('search.confidence', 'Confidence')}:** {result.confidence_score:.2f}"
                                        )
                                        st.markdown(
                                            f"**{safe_translate('search.source', 'Source')}:** {result.source.title()}"
                                        )

                                    with info_col3:
                                        if result.estimated_cost:
                                            st.markdown(f"**Cost Estimate:** {result.estimated_cost}")
                                        if result.success_rate:
                                            st.markdown(f"**Success Rate:** {result.success_rate:.0%}")

                                    # Guide content
                                    if guide.summary:
                                        st.markdown(f"**{_('guides.summary')}:** {guide.summary}")

                                    if result.difficulty_explanation:
                                        st.info(f"💡 {result.difficulty_explanation}")

                                    # Tools and parts
                                    if hasattr(guide, "tools_required") and guide.tools_required:
                                        st.markdown(f"**{_('guides.tools_required')}:**")
                                        for tool in guide.tools_required:
                                            st.markdown(f"- {tool}")

                                    if hasattr(guide, "parts") and guide.parts:
                                        st.markdown(f"**Parts Required:**")
                                        for part in guide.parts:
                                            st.markdown(f"- {part}")

                                    # Warnings
                                    if hasattr(guide, "warnings") and guide.warnings:
                                        for warning in guide.warnings:
                                            st.warning(f"⚠️ {warning}")

                                    # Bookmark functionality
                                    bookmark_col1, bookmark_col2 = st.columns([3, 1])
                                    with bookmark_col2:
                                        bookmark_key = f"{guide.guideid}_{guide.title[:20]}"
                                        if bookmark_key in st.session_state.search_bookmarks:
                                            if st.button("🔖 Remove", key=f"remove_bookmark_{i}"):
                                                st.session_state.search_bookmarks.remove(bookmark_key)
                                                st.rerun()
                                        else:
                                            if st.button("📌 Bookmark", key=f"add_bookmark_{i}"):
                                                st.session_state.search_bookmarks.append(bookmark_key)
                                                st.rerun()

                                    # Related guides
                                    if result.related_guides:
                                        st.markdown("**Related Guides:**")
                                        for related in result.related_guides[:2]:  # Show top 2
                                            st.markdown(f"- 🔗 {related.title}")

                        else:
                            st.info(safe_translate("search.no_results", "No repair guides found for your search."))

                            # Search suggestions for no results
                            if current_lang == "ja":
                                st.markdown("**検索のコツ:**")
                                st.markdown("- より一般的な用語を使用してみてください")
                                st.markdown("- デバイス名と問題を分けて検索してみてください")
                                st.markdown("- 英語での検索も試してみてください")
                            else:
                                st.markdown("**Search Tips:**")
                                st.markdown("- Try using more general terms")
                                st.markdown("- Search for device and issue separately")
                                st.markdown("- Japanese search is also supported")

                    except Exception as e:
                        logger.error(
                            "Enhanced guide search error",
                            exc_info=True,
                            extra={
                                "extra_data": {
                                    "error_type": type(e).__name__,
                                    "original_query": safe_query,
                                    "processed_query": processed_query,
                                    "filters": normalized_filters,
                                    "language": current_lang,
                                }
                            },
                        )
                        st.error(safe_translate("search.error", "An error occurred during search. Please try again."))

            # Search history and bookmarks sidebar
            if st.session_state.search_history or st.session_state.search_bookmarks:
                with st.expander("📚 History & Bookmarks"):
                    history_tab, bookmark_tab = st.tabs(["History", "Bookmarks"])

                    with history_tab:
                        if st.session_state.search_history:
                            st.markdown("**Recent Searches:**")
                            for i, query in enumerate(st.session_state.search_history[:5]):
                                if st.button(f"🔄 {query}", key=f"history_{i}"):
                                    st.session_state.main_search_input = query
                                    st.rerun()

                            if st.button(safe_translate("search.clear_history", "Clear History")):
                                st.session_state.search_history = []
                                st.rerun()
                        else:
                            st.info("No search history yet")

                    with bookmark_tab:
                        if st.session_state.search_bookmarks:
                            st.markdown("**Bookmarked Guides:**")
                            for bookmark in st.session_state.search_bookmarks:
                                st.markdown(f"🔖 {bookmark}")
                        else:
                            st.info("No bookmarks yet")

        # Responsive design info
        if settings.debug:
            show_responsive_design_info()

            # Debug info for Japanese search
            if st.session_state.get("last_search_time"):
                st.markdown("**Japanese Search Debug Info:**")
                st.json(
                    {
                        "last_processing_time": f"{st.session_state.last_search_time:.3f}s",
                        "search_history_count": len(st.session_state.search_history),
                        "bookmarks_count": len(st.session_state.search_bookmarks),
                        "current_language": st.session_state.get("language", "en"),
                        "japanese_mapper_available": get_mapper() is not None,
                    }
                )


if __name__ == "__main__":
    main()
