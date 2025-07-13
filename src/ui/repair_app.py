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
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()


# Page configuration
st.set_page_config(
    page_title="RepairGPT - AI Repair Assistant",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
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
    }
    
    .user-message {
        background: #e3f2fd;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background: #f1f8e9;
        margin-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
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
    st.sidebar.header("🔧 Device Information")
    
    # Device selection
    device_categories = [
        "Select Device Type...",
        "Nintendo Switch", "Nintendo Switch Lite", "Nintendo Switch OLED",
        "iPhone", "iPad", "MacBook", "iMac",
        "PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One",
        "Samsung Galaxy", "Google Pixel",
        "Gaming PC", "Laptop", "Desktop PC",
        "Other"
    ]
    
    selected_device = st.sidebar.selectbox(
        "Device Type",
        device_categories,
        index=0
    )
    
    device_model = ""
    if selected_device != "Select Device Type...":
        if selected_device == "Other":
            device_model = st.sidebar.text_input("Enter device name:")
            selected_device = device_model
        else:
            device_model = st.sidebar.text_input("Model/Version (optional):")
    
    # Issue description
    issue_description = st.sidebar.text_area(
        "Describe the issue:",
        placeholder="e.g., Joy-Con drift, cracked screen, won't turn on..."
    )
    
    # Skill level
    skill_level = st.sidebar.selectbox(
        "Your repair experience:",
        ["beginner", "intermediate", "expert"]
    )
    
    # Update context
    if selected_device != "Select Device Type...":
        st.session_state.device_context.update({
            'device_type': selected_device,
            'device_model': device_model,
            'issue_description': issue_description,
            'skill_level': skill_level
        })
        
        # Update chatbot context
        st.session_state.chatbot.update_context(
            device_type=selected_device,
            device_model=device_model,
            issue_description=issue_description,
            user_skill_level=skill_level
        )
    
    # Show current context
    if st.session_state.device_context['device_type']:
        with st.sidebar.expander("Current Context", expanded=False):
            st.write(f"**Device:** {st.session_state.device_context['device_type']}")
            if st.session_state.device_context['device_model']:
                st.write(f"**Model:** {st.session_state.device_context['device_model']}")
            if st.session_state.device_context['issue_description']:
                st.write(f"**Issue:** {st.session_state.device_context['issue_description']}")
            st.write(f"**Skill Level:** {st.session_state.device_context['skill_level']}")


def image_upload_section():
    """Image upload and analysis section"""
    st.sidebar.header("📸 Image Upload")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload device photo",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear photo of your device or the problem area"
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        # Display thumbnail in sidebar
        st.sidebar.image(image, caption="Uploaded Image", width=200)
        
        # Store in session state
        st.session_state.uploaded_image = image
        
        if st.sidebar.button("🔍 Analyze Image", type="primary"):
            st.sidebar.success("Image uploaded successfully!")
            st.sidebar.info("AI-powered image analysis coming soon...")
            
            # TODO: Integrate with vision AI
            # For now, add context about image upload
            st.session_state.chatbot.add_message(
                "system", 
                f"User uploaded an image of their {st.session_state.device_context['device_type']}. Image analysis capabilities will be available in future updates."
            )
    
    if st.sidebar.button("🗑️ Clear Image"):
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
    st.markdown("### AI-Powered Electronic Device Repair Assistant")
    
    # Safety warning
    st.markdown("""
    <div class="safety-warning">
        <strong>⚠️ Safety First:</strong> Always power off devices before repair. 
        Work in a static-free environment. If unsure, consult a professional.
    </div>
    """, unsafe_allow_html=True)
    
    # Device context display
    if st.session_state.device_context['device_type']:
        device_info = st.session_state.device_context
        st.markdown(f"""
        <div class="device-card">
            <h4>🔧 Current Device: {device_info['device_type']}</h4>
            {f"<strong>Model:</strong> {device_info['device_model']}<br>" if device_info['device_model'] else ""}
            {f"<strong>Issue:</strong> {device_info['issue_description']}<br>" if device_info['issue_description'] else ""}
            <strong>Skill Level:</strong> {device_info['skill_level'].title()}
        </div>
        """, unsafe_allow_html=True)
    
    # Chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>RepairGPT:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    chat_input_container = st.container()
    with chat_input_container:
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_area(
                "Describe your repair issue or ask a question:",
                placeholder="e.g., My Nintendo Switch Joy-Con is drifting. How can I fix it?",
                height=100,
                key="chat_input"
            )
        
        with col2:
            st.write("")  # Spacing
            send_button = st.button("Send 🚀", type="primary", use_container_width=True)
            clear_button = st.button("Clear Chat 🗑️", use_container_width=True)
    
    # Handle user input
    if send_button and user_input.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get bot response
        with st.spinner("RepairGPT is thinking..."):
            try:
                response = st.session_state.chatbot.chat(user_input)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_response = f"I apologize, but I encountered an error: {e}"
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
        st.markdown("### 💡 Quick Start Examples")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎮 Joy-Con Drift Fix", use_container_width=True):
                example_text = "My Nintendo Switch Joy-Con is drifting. What are my options to fix this?"
                st.session_state.messages.append({"role": "user", "content": example_text})
                with st.spinner("Getting response..."):
                    response = st.session_state.chatbot.chat(example_text)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col2:
            if st.button("📱 Cracked Screen Repair", use_container_width=True):
                example_text = "I dropped my iPhone and the screen is cracked. Is it worth repairing myself?"
                st.session_state.messages.append({"role": "user", "content": example_text})
                with st.spinner("Getting response..."):
                    response = st.session_state.chatbot.chat(example_text)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col3:
            if st.button("💻 Laptop Won't Boot", use_container_width=True):
                example_text = "My laptop won't turn on after a power surge. What should I check first?"
                st.session_state.messages.append({"role": "user", "content": example_text})
                with st.spinner("Getting response..."):
                    response = st.session_state.chatbot.chat(example_text)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()


def footer():
    """Application footer"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🔧 RepairGPT - Open Source AI Repair Assistant</p>
        <p>Always prioritize safety and consider professional help for complex repairs.</p>
        <p>Powered by AI • Data from iFixit • Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    sidebar_device_setup()
    image_upload_section()
    ifixit_guides_section()
    
    # Main interface
    main_chat_interface()
    quick_help_section()
    footer()
    
    # Debug info (only in development)
    if st.sidebar.checkbox("Show Debug Info"):
        st.sidebar.json({
            "Active LLM Client": st.session_state.chatbot.active_client,
            "Message Count": len(st.session_state.messages),
            "Device Context": st.session_state.device_context,
            "Has Image": st.session_state.uploaded_image is not None,
            "iFixit Guides": len(st.session_state.repair_guides),
            "Offline Guides": len(st.session_state.offline_guides),
            "Total Offline DB": len(st.session_state.offline_db.guides),
            "Available Devices": st.session_state.offline_db.get_all_devices()
        })


if __name__ == "__main__":
    main()