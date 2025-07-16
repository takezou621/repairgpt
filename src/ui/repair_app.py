"""
RepairGPT Streamlit Application
Implements Issue #11: Streamlit基本チャットUIの実装
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

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from chat.llm_chatbot import RepairChatbot, RepairContext
    from clients.ifixit_client import IFixitClient, Guide
    from data.offline_repair_database import OfflineRepairDatabase
    from i18n import i18n, _
    from ui.language_selector import language_selector, get_localized_device_categories, get_localized_skill_levels
    from ui.responsive_design import initialize_responsive_design, enhance_ui_components
    from ui.ui_enhancements import show_responsive_design_info, add_responsive_navigation_hints
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()


# Initialize i18n and set default language from session state
if 'language' not in st.session_state:
    st.session_state.language = 'en'
i18n.set_language(st.session_state.language)

# Page configuration
st.set_page_config(
    page_title=_("app.title"),
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize responsive design and UI enhancements
responsive_manager = initialize_responsive_design()
enhance_ui_components()


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = RepairChatbot(preferred_model="auto")
    
    if 'ifixit_client' not in st.session_state:
        st.session_state.ifixit_client = IFixitClient()
    
    if 'offline_db' not in st.session_state:
        st.session_state.offline_db = OfflineRepairDatabase()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'device_context' not in st.session_state:
        st.session_state.device_context = {
            'device_type': '',
            'device_model': '',
            'issue_description': '',
            'skill_level': 'beginner'
        }
    
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    
    if 'repair_guides' not in st.session_state:
        st.session_state.repair_guides = []
    
    if 'offline_guides' not in st.session_state:
        st.session_state.offline_guides = []


def sidebar_device_setup():
    """Sidebar for device and context setup"""
    st.sidebar.header(_("ui.headers.device_info"))
    
    # Device selection
    device_categories = get_localized_device_categories()
    
    selected_device = st.sidebar.selectbox(
        _("ui.labels.device_type"),
        device_categories,
        index=0
    )
    
    device_model = ""
    if selected_device != _("ui.placeholders.select_device"):
        if selected_device == _("devices.other"):
            device_model = st.sidebar.text_input(_("ui.placeholders.device_model"))
            selected_device = device_model
        else:
            device_model = st.sidebar.text_input(_("ui.labels.device_model"))
    
    # Issue description
    issue_description = st.sidebar.text_area(
        _("ui.labels.issue_description"),
        placeholder=_("ui.placeholders.issue_description")
    )
    
    # Skill level
    skill_levels = get_localized_skill_levels()
    skill_level = st.sidebar.selectbox(
        _("ui.labels.skill_level"),
        skill_levels
    )
    
    # Convert localized skill level back to English for internal use
    skill_level_map = {
        _("skill_levels.beginner"): "beginner",
        _("skill_levels.intermediate"): "intermediate", 
        _("skill_levels.expert"): "expert"
    }
    internal_skill_level = skill_level_map.get(skill_level, "beginner")
    
    # Update context
    if selected_device != _("ui.placeholders.select_device"):
        st.session_state.device_context.update({
            'device_type': selected_device,
            'device_model': device_model,
            'issue_description': issue_description,
            'skill_level': internal_skill_level
        })
        
        # Update chatbot context
        st.session_state.chatbot.update_context(
            device_type=selected_device,
            device_model=device_model,
            issue_description=issue_description,
            user_skill_level=internal_skill_level
        )
    
    # Show current context
    if st.session_state.device_context['device_type']:
        with st.sidebar.expander(_("ui.labels.current_context"), expanded=False):
            device_label = _("guide.device")
            st.write(f"**{device_label}:** {st.session_state.device_context['device_type']}")
            if st.session_state.device_context['device_model']:
                model_label = _("ui.labels.device_model")
                st.write(f"**{model_label}:** {st.session_state.device_context['device_model']}")
            if st.session_state.device_context['issue_description']:
                issue_label = _("ui.labels.issue_description")
                st.write(f"**{issue_label}:** {st.session_state.device_context['issue_description']}")
            skill_label = _("ui.labels.skill_level")
            st.write(f"**{skill_label}:** {skill_level}")


def format_analysis_for_chat(analysis_result):
    """Format image analysis results for chat context"""
    device_info = analysis_result.device_info
    damage_list = analysis_result.damage_detected
    
    summary = []
    
    # Device information
    device_desc = f"{device_info.device_type.value}"
    if device_info.brand:
        device_desc += f" ({device_info.brand}"
        if device_info.model:
            device_desc += f" {device_info.model}"
        device_desc += ")"
    
    summary.append(f"Device: {device_desc} (confidence: {device_info.confidence:.0%})")
    summary.append(f"Overall condition: {analysis_result.overall_condition}")
    summary.append(f"Repair urgency: {analysis_result.repair_urgency}")
    
    # Damage assessment
    if damage_list:
        summary.append("\nDetected issues:")
        for damage in damage_list:
            damage_desc = f"- {damage.damage_type.value.replace('_', ' ').title()}"
            if damage.location:
                damage_desc += f" ({damage.location})"
            damage_desc += f" - {damage.severity} severity"
            if damage.description:
                damage_desc += f": {damage.description}"
            summary.append(damage_desc)
    else:
        summary.append("\nNo significant damage detected")
    
    # Recommendations
    if analysis_result.recommended_actions:
        summary.append("\nRecommended actions:")
        for action in analysis_result.recommended_actions:
            summary.append(f"- {action}")
    
    # Warnings
    if analysis_result.warnings:
        summary.append("\nWarnings:")
        for warning in analysis_result.warnings:
            summary.append(f"⚠️ {warning}")
    
    return "\n".join(summary)


def display_analysis_results(analysis_result):
    """Display detailed analysis results in sidebar"""
    device_info = analysis_result.device_info
    
    st.sidebar.subheader("🔍 Analysis Results")
    
    # Device information
    st.sidebar.write(f"**Device**: {device_info.device_type.value.title()}")
    if device_info.brand:
        st.sidebar.write(f"**Brand**: {device_info.brand}")
    if device_info.model:
        st.sidebar.write(f"**Model**: {device_info.model}")
    
    # Overall assessment
    condition_emoji = {
        "excellent": "✨",
        "good": "✅", 
        "fair": "⚠️",
        "poor": "❌",
        "critical": "🚨"
    }
    
    urgency_emoji = {
        "none": "✅",
        "low": "🟢",
        "medium": "🟡", 
        "high": "🟠",
        "critical": "🔴"
    }
    
    st.sidebar.write(f"**Condition**: {condition_emoji.get(analysis_result.overall_condition, '❓')} {analysis_result.overall_condition.title()}")
    st.sidebar.write(f"**Urgency**: {urgency_emoji.get(analysis_result.repair_urgency, '❓')} {analysis_result.repair_urgency.title()}")
    
    if analysis_result.estimated_repair_cost:
        st.sidebar.write(f"**Est. Cost**: {analysis_result.estimated_repair_cost}")
    
    if analysis_result.repair_difficulty:
        st.sidebar.write(f"**Difficulty**: {analysis_result.repair_difficulty.title()}")
    
    # Damage details
    if analysis_result.damage_detected:
        st.sidebar.subheader("🔧 Issues Found")
        for damage in analysis_result.damage_detected:
            severity_color = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🟠", 
                "critical": "🔴"
            }
            
            st.sidebar.write(f"{severity_color.get(damage.severity, '❓')} **{damage.damage_type.value.replace('_', ' ').title()}**")
            if damage.location:
                st.sidebar.write(f"   📍 Location: {damage.location}")
            if damage.description:
                st.sidebar.write(f"   📝 {damage.description}")
            st.sidebar.write(f"   🎯 Confidence: {damage.confidence:.0%}")
    
    # Warnings
    if analysis_result.warnings:
        st.sidebar.subheader("⚠️ Warnings")
        for warning in analysis_result.warnings:
            st.sidebar.warning(warning)


def image_upload_section():
    """Image upload and analysis section"""
    st.sidebar.header(_("ui.headers.image_upload"))
    
    uploaded_file = st.sidebar.file_uploader(
        _("ui.labels.upload_image"),
        type=['png', 'jpg', 'jpeg'],
        help=_("ui.help.upload_image")
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        # Display thumbnail in sidebar
        st.sidebar.image(image, caption="Uploaded Image", width=200)
        
        # Store in session state
        st.session_state.uploaded_image = image
        
        if st.sidebar.button(_("ui.buttons.analyze_image"), type="primary"):
            st.sidebar.success(_("ui.messages.image_uploaded"))
            
            # Perform AI image analysis
            with st.sidebar.spinner("🔍 Analyzing image..."):
                try:
                    # Import image analysis service
                    from services.image_analysis import ImageAnalysisService
                    
                    # Convert PIL image to bytes
                    img_byte_array = io.BytesIO()
                    image.save(img_byte_array, format='JPEG')
                    image_bytes = img_byte_array.getvalue()
                    
                    # Initialize analysis service
                    openai_api_key = os.getenv('OPENAI_API_KEY')
                    if openai_api_key:
                        analysis_service = ImageAnalysisService(
                            provider="openai",
                            api_key=openai_api_key
                        )
                        
                        # Perform analysis
                        import asyncio
                        async def analyze_image():
                            return await analysis_service.analyze_device_image(
                                image_data=image_bytes,
                                language=st.session_state.language
                            )
                        
                        # Run async analysis
                        result = asyncio.run(analyze_image())
                        
                        # Format analysis results for chat
                        analysis_summary = format_analysis_for_chat(result)
                        
                        # Add analysis to chat context
                        st.session_state.chatbot.add_message(
                            "system", 
                            f"AI Image Analysis Results:\n{analysis_summary}"
                        )
                        
                        # Display analysis results in sidebar
                        display_analysis_results(result)
                        
                    else:
                        st.sidebar.warning("OpenAI API key not configured. Image analysis disabled.")
                        st.session_state.chatbot.add_message(
                            "system", 
                            f"User uploaded an image of their device, but image analysis is not available (API key missing)."
                        )
                        
                except Exception as e:
                    st.sidebar.error(f"Analysis failed: {str(e)}")
                    st.session_state.chatbot.add_message(
                        "system", 
                        f"User uploaded an image but analysis failed: {str(e)}"
                    )
    
    if st.sidebar.button(_("ui.buttons.clear_image")):
        st.session_state.uploaded_image = None
        st.rerun()


def ifixit_guides_section():
    """iFixit and offline repair guides integration"""
    st.sidebar.header("📚 Repair Guides")
    
    device_type = st.session_state.device_context.get('device_type', '')
    issue_description = st.session_state.device_context.get('issue_description', '')
    
    # Search buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        online_search = st.button("🌐 Online", help="Search iFixit guides online")
    
    with col2:
        offline_search = st.button("💾 Offline", help="Search built-in repair database")
    
    # Online search
    if device_type and online_search:
        with st.spinner("Searching iFixit guides..."):
            try:
                # Search for device-specific guides  
                search_query = f"{device_type} {issue_description}".strip()
                guides = st.session_state.ifixit_client.search_guides(search_query, limit=5)
                st.session_state.repair_guides = guides
                
                if guides:
                    st.sidebar.success(f"Found {len(guides)} online guides!")
                else:
                    st.sidebar.warning("No online guides found. Try offline guides.")
                    
            except Exception as e:
                st.sidebar.error(f"Online search failed: {e}")
                st.sidebar.info("Try offline guides instead!")
    
    # Offline search
    if offline_search:
        with st.spinner("Searching offline repair database..."):
            try:
                search_query = f"{device_type} {issue_description}".strip()
                offline_guides = st.session_state.offline_db.search_guides(
                    search_query, device_type, limit=5
                )
                st.session_state.offline_guides = offline_guides
                
                if offline_guides:
                    st.sidebar.success(f"Found {len(offline_guides)} offline guides!")
                else:
                    st.sidebar.warning("No matching offline guides found.")
                    
            except Exception as e:
                st.sidebar.error(f"Offline search failed: {e}")
    
    # Display online guides
    if st.session_state.repair_guides:
        st.sidebar.subheader("🌐 Online Guides (iFixit):")
        for guide in st.session_state.repair_guides[:3]:
            with st.sidebar.expander(f"{guide.title[:45]}..."):
                st.write(f"**Difficulty:** {guide.difficulty}")
                st.write(f"**Device:** {guide.device}")
                if guide.summary:
                    st.write(f"**Summary:** {guide.summary[:100]}...")
                if guide.url:
                    st.markdown(f"[View Full Guide]({guide.url})")
    
    # Display offline guides
    if st.session_state.offline_guides:
        st.sidebar.subheader("💾 Offline Guides:")
        for guide in st.session_state.offline_guides[:3]:
            with st.sidebar.expander(f"{guide.title[:45]}..."):
                st.write(f"**Difficulty:** {guide.difficulty}")
                st.write(f"**Time:** {guide.time_estimate}")
                st.write(f"**Cost:** {guide.cost_estimate}")
                st.write(f"**Success Rate:** {guide.success_rate}")
                if st.button(f"View Details", key=f"view_{guide.id}"):
                    show_offline_guide_details(guide)


def show_offline_guide_details(guide):
    """Display detailed offline guide information"""
    st.markdown(f"## 🔧 {guide.title}")
    
    # Basic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Difficulty", guide.difficulty)
    with col2:
        st.metric("Time", guide.time_estimate)
    with col3:
        st.metric("Cost", guide.cost_estimate)
    
    # Success rate
    st.info(f"**Success Rate:** {guide.success_rate}")
    
    # Tools required
    st.markdown("### 🛠️ Tools Required")
    for tool in guide.tools_required:
        st.write(f"• {tool}")
    
    # Parts required
    if guide.parts_required:
        st.markdown("### 🔧 Parts Required")
        for part in guide.parts_required:
            st.write(f"• {part}")
    
    # Warnings
    if guide.warnings:
        st.markdown("### ⚠️ Important Warnings")
        for warning in guide.warnings:
            st.warning(f"⚠️ {warning}")
    
    # Steps
    st.markdown("### 📋 Repair Steps")
    for step in guide.steps:
        with st.expander(f"Step {step['step']}: {step['title']}"):
            st.write(step['description'])
    
    # Tips
    if guide.tips:
        st.markdown("### 💡 Pro Tips")
        for tip in guide.tips:
            st.success(f"💡 {tip}")


def main_chat_interface():
    """Main chat interface"""
    # Header
    st.markdown('<h1 class="main-header">🔧 RepairGPT</h1>', unsafe_allow_html=True)
    subtitle = _("app.subtitle")
    st.markdown(f"### {subtitle}")
    
    # Safety warning
    safety_warning = _("ui.messages.safety_warning")
    st.markdown(f"""
    <div class="safety-warning">
        {safety_warning}
    </div>
    """, unsafe_allow_html=True)
    
    # Device context display
    if st.session_state.device_context['device_type']:
        device_info = st.session_state.device_context
        # Get localized skill level for display
        skill_level_display_map = {
            "beginner": _("skill_levels.beginner"),
            "intermediate": _("skill_levels.intermediate"), 
            "expert": _("skill_levels.expert")
        }
        skill_display = skill_level_display_map.get(device_info['skill_level'], device_info['skill_level'])
        
        current_device_header = _("ui.headers.current_device", device=device_info['device_type'])
        device_model_label = _("ui.labels.device_model")
        issue_label = _("ui.labels.issue_description") 
        skill_level_label = _("ui.labels.skill_level")
        
        model_html = f"<strong>{device_model_label}:</strong> {device_info['device_model']}<br>" if device_info['device_model'] else ""
        issue_html = f"<strong>{issue_label}:</strong> {device_info['issue_description']}<br>" if device_info['issue_description'] else ""
        
        st.markdown(f"""
        <div class="device-card">
            <h4>{current_device_header}</h4>
            {model_html}
            {issue_html}
            <strong>{skill_level_label}:</strong> {skill_display}
        </div>
        """, unsafe_allow_html=True)
    
    # Chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>{_("chat.you")}:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>{_("chat.repairgpt")}:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    chat_input_container = st.container()
    with chat_input_container:
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_area(
                _("ui.labels.chat_input"),
                placeholder=_("ui.placeholders.chat_input"),
                height=100,
                key="chat_input"
            )
        
        with col2:
            st.write("")  # Spacing
            send_button = st.button(_("ui.buttons.send"), type="primary", use_container_width=True)
            clear_button = st.button(_("ui.buttons.clear_chat"), use_container_width=True)
    
    # Handle user input
    if send_button and user_input.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get bot response
        with st.spinner(_("ui.messages.thinking")):
            try:
                response = st.session_state.chatbot.chat(user_input)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_response = _("ui.messages.error_response", error=str(e))
                st.session_state.messages.append({"role": "assistant", "content": error_response})
        
        # Clear input and rerun
        st.rerun()
    
    # Clear chat
    if clear_button:
        st.session_state.messages = []
        st.session_state.chatbot.reset_conversation()
        st.rerun()


def quick_help_section():
    """Quick help and examples section"""
    if not st.session_state.messages:  # Only show when chat is empty
        quick_start_header = _("ui.headers.quick_start")
        st.markdown(f"### {quick_start_header}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(_("ui.examples.joycon_drift"), use_container_width=True):
                example_text = _("ui.examples.joycon_text")
                st.session_state.messages.append({"role": "user", "content": example_text})
                with st.spinner(_("ui.messages.getting_response")):
                    response = st.session_state.chatbot.chat(example_text)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col2:
            if st.button(_("ui.examples.cracked_screen"), use_container_width=True):
                example_text = _("ui.examples.screen_text")
                st.session_state.messages.append({"role": "user", "content": example_text})
                with st.spinner(_("ui.messages.getting_response")):
                    response = st.session_state.chatbot.chat(example_text)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col3:
            if st.button(_("ui.examples.laptop_boot"), use_container_width=True):
                example_text = _("ui.examples.laptop_text")
                st.session_state.messages.append({"role": "user", "content": example_text})
                with st.spinner(_("ui.messages.getting_response")):
                    response = st.session_state.chatbot.chat(example_text)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()


def footer():
    """Application footer"""
    st.markdown("---")
    footer_description = _("app.footer.description")
    footer_safety = _("app.footer.safety")
    footer_powered = _("app.footer.powered")
    
    st.markdown(f"""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>{footer_description}</p>
        <p>{footer_safety}</p>
        <p>{footer_powered}</p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Language selector
    language_selector()
    
    # Update i18n with current language
    i18n.set_language(st.session_state.language)
    
    # Sidebar
    sidebar_device_setup()
    image_upload_section()
    ifixit_guides_section()
    
    # Main interface
    main_chat_interface()
    quick_help_section()
    
    # Add responsive design navigation hints
    add_responsive_navigation_hints()
    
    footer()
    
    # Debug info (only in development)
    with st.sidebar.expander("🔧 Development Options"):
        if st.checkbox("Show Debug Info"):
            st.json({
                "Active LLM Client": st.session_state.chatbot.active_client,
                "Message Count": len(st.session_state.messages),
                "Device Context": st.session_state.device_context,
                "Has Image": st.session_state.uploaded_image is not None,
                "iFixit Guides": len(st.session_state.repair_guides),
                "Offline Guides": len(st.session_state.offline_guides),
                "Total Offline DB": len(st.session_state.offline_db.guides),
                "Available Devices": st.session_state.offline_db.get_all_devices()
            })
        
        if st.checkbox("Show UI/UX Improvements"):
            show_responsive_design_info()


if __name__ == "__main__":
    main()