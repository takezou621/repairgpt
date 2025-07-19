"""
UI/UX Enhancement Components for RepairGPT
Implements additional UI improvements as part of Issue #89

This module provides enhanced UI components that complement the responsive design
and improve the overall user experience of the RepairGPT application.
"""

from typing import Any, Dict, List, Optional

import streamlit as st

from ui.responsive_design import ResponsiveDesignManager


def create_enhanced_info_card(
    title: str, content: str, icon: str = "ℹ️", card_type: str = "info"
) -> None:
    """
    Create an enhanced information card with responsive design.

    Args:
        title: Card title
        content: Card content
        icon: Icon to display (emoji or HTML entity)
        card_type: Type of card (info, success, warning, error)
    """
    color_map = {
        "info": "#e3f2fd",
        "success": "#e8f5e8",
        "warning": "#fff3cd",
        "error": "#ffebee",
    }

    border_color_map = {
        "info": "#2196f3",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
    }

    bg_color = color_map.get(card_type, "#e3f2fd")
    border_color = border_color_map.get(card_type, "#2196f3")

    st.markdown(
        f"""
    <div style="
        background: {bg_color};
        border-left: 4px solid {border_color};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    " onmouseover="this.style.transform='translateY(-2px)'" 
       onmouseout="this.style.transform='translateY(0)'">
        <h4 style="margin: 0 0 0.5rem 0; color: {border_color};">
            {icon} {title}
        </h4>
        <p style="margin: 0; line-height: 1.5;">
            {content}
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def create_feature_showcase() -> None:
    """
    Create a showcase of the responsive design and UI improvements.
    This function demonstrates the enhancements made in Issue #89.
    """
    st.markdown("### 🎨 UI/UX Improvements Showcase")

    # Enhanced info cards
    col1, col2 = st.columns(2)

    with col1:
        create_enhanced_info_card(
            "Responsive Design",
            "The interface now adapts seamlessly to mobile, tablet, and desktop screens with optimized layouts and touch-friendly controls.",
            "📱",
            "info",
        )

        create_enhanced_info_card(
            "Enhanced Accessibility",
            "Improved focus indicators, keyboard navigation, and color contrast for better accessibility compliance.",
            "♿",
            "success",
        )

    with col2:
        create_enhanced_info_card(
            "Mobile Optimization",
            "Touch-friendly buttons, optimized forms, and improved navigation for mobile devices.",
            "👆",
            "warning",
        )

        create_enhanced_info_card(
            "Performance Improvements",
            "Reduced animations on mobile, lazy loading, and optimized rendering for better performance.",
            "⚡",
            "error",
        )

    # Interactive demo section
    st.markdown("### 🔧 Interactive Demo")

    # Responsive form demo
    with st.expander("📋 Responsive Form Demo"):
        manager = ResponsiveDesignManager()

        form_fields = [
            {
                "type": "text",
                "key": "device_name",
                "label": "Device Name",
                "help": "Enter the name of your device",
            },
            {
                "type": "selectbox",
                "key": "issue_type",
                "label": "Issue Type",
                "options": [
                    "Hardware Problem",
                    "Software Issue",
                    "Performance Problem",
                    "Other",
                ],
                "help": "Select the type of issue you are experiencing",
            },
            {
                "type": "textarea",
                "key": "description",
                "label": "Issue Description",
                "help": "Provide a detailed description of the problem",
            },
        ]

        form_data = manager.create_mobile_friendly_form("Repair Request", form_fields)

        if form_data:
            st.success("✅ Form submitted successfully!")
            st.json(form_data)

    # Responsive button demo
    with st.expander("🎯 Responsive Button Demo"):
        st.markdown("These buttons are optimized for touch interaction:")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Primary Action", type="primary", use_container_width=True):
                st.balloons()
        with col2:
            if st.button("Secondary Action", use_container_width=True):
                st.success("Secondary action triggered!")
        with col3:
            if st.button("Tertiary Action", use_container_width=True):
                st.info("Tertiary action triggered!")

    # Color scheme demo
    with st.expander("🎨 Color Scheme and Theme"):
        st.markdown(
            """
        The enhanced design includes:
        - **Consistent Color Palette**: Primary (#4ECDC4) and Secondary (#FF6B6B) colors
        - **CSS Variables**: Easily customizable theme properties
        - **Dark Mode Support**: Automatic adaptation to user's system preferences
        - **Improved Contrast**: Better readability and accessibility
        """
        )

        # Color swatches
        st.markdown(
            """
        <div style="display: flex; gap: 1rem; margin: 1rem 0;">
            <div style="background: #4ECDC4; padding: 1rem; border-radius: 8px; color: white; text-align: center; flex: 1;">
                Primary<br>#4ECDC4
            </div>
            <div style="background: #FF6B6B; padding: 1rem; border-radius: 8px; color: white; text-align: center; flex: 1;">
                Secondary<br>#FF6B6B
            </div>
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; color: #2c3e50; text-align: center; flex: 1; border: 1px solid #e1e8ed;">
                Background<br>#f8f9fa
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def create_responsive_metrics_display(metrics: List[Dict[str, Any]]) -> None:
    """
    Create a responsive metrics display that adapts to screen size.

    Args:
        metrics: List of metric dictionaries with 'label', 'value', and optional 'delta' keys
    """
    # Determine number of columns based on metrics count
    num_metrics = len(metrics)
    if num_metrics <= 2:
        cols = st.columns(num_metrics)
    elif num_metrics <= 4:
        cols = st.columns(2)
    else:
        cols = st.columns(3)

    for i, metric in enumerate(metrics):
        col_index = i % len(cols)
        with cols[col_index]:
            st.metric(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                delta=metric.get("delta"),
            )


def add_responsive_navigation_hints() -> None:
    """
    Add helpful navigation hints for different device types.
    """
    st.markdown(
        """
    <div style="
        background: linear-gradient(45deg, #e3f2fd, #f1f8e9);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        font-size: 0.9rem;
        line-height: 1.4;
    ">
        <strong>💡 Navigation Tips:</strong><br>
        📱 <strong>Mobile:</strong> Swipe left to access the sidebar menu<br>
        💻 <strong>Desktop:</strong> Use keyboard shortcuts: Tab for navigation, Enter to activate<br>
        🖥️ <strong>All devices:</strong> Long press for additional options
    </div>
    """,
        unsafe_allow_html=True,
    )


def show_responsive_design_info() -> None:
    """
    Display information about the responsive design implementation.
    This function can be called to show users what improvements have been made.
    """
    st.markdown(
        """
    ## 🎨 Responsive Design & UI/UX Improvements
    
    ### What's New:
    
    **📱 Mobile-First Design**
    - Optimized layouts for smartphones and tablets
    - Touch-friendly buttons with 44px minimum height
    - Improved text sizing with clamp() functions
    - Better spacing and padding on smaller screens
    
    **🎯 Enhanced User Experience**
    - Smooth animations and transitions
    - Hover effects and visual feedback
    - Improved color contrast and accessibility
    - Consistent design language throughout the app
    
    **⚡ Performance Optimizations**
    - Reduced motion for users who prefer it
    - Optimized animations for mobile devices
    - Better resource loading and rendering
    
    **🌙 Dark Mode Support**
    - Automatic adaptation to system preferences
    - Improved readability in low-light conditions
    
    **♿ Accessibility Improvements**
    - Better focus indicators
    - Keyboard navigation support
    - Screen reader friendly markup
    - WCAG 2.1 compliance considerations
    """
    )

    # Show the feature showcase
    create_feature_showcase()
