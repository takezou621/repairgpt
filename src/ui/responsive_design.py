"""
Responsive Design and UI/UX Enhancement Module for RepairGPT
Implements Issue #89: レスポンシブデザインとUI/UX改善

This module provides responsive design components and enhanced CSS styling
for the RepairGPT Streamlit application to improve mobile and desktop user experience.
"""

from typing import Any, Dict, List

import streamlit as st


class ResponsiveDesignManager:
    """
    Manager class for implementing responsive design and UI/UX improvements
    in the RepairGPT Streamlit application.
    """

    def __init__(self) -> None:
        """Initialize the ResponsiveDesignManager"""
        self.breakpoints = {"mobile": "768px", "tablet": "1024px", "desktop": "1200px"}

    def get_responsive_css(self) -> str:
        """
        Generate responsive CSS for the RepairGPT application.

        Returns:
            str: Complete CSS string with responsive design rules
        """
        return """
        <style>
        /* Mobile-first responsive design */
        :root {
            --primary-color: #4ECDC4;
            --secondary-color: #FF6B6B;
            --background-color: #f8f9fa;
            --text-color: #2c3e50;
            --border-radius: 8px;
            --box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            --padding-xs: 0.5rem;
            --padding-sm: 1rem;
            --padding-md: 1.5rem;
            --padding-lg: 2rem;
        }

        /* Main header responsive styling */
        .main-header {
            text-align: center;
            padding: var(--padding-sm) 0;
            background: linear-gradient(90deg, var(--secondary-color), var(--primary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: clamp(1.5rem, 5vw, 3rem);
            font-weight: bold;
            margin-bottom: var(--padding-md);
            line-height: 1.2;
        }

        /* Enhanced device card with mobile optimization */
        .device-card {
            background: var(--background-color);
            padding: var(--padding-sm);
            border-radius: var(--border-radius);
            border-left: 4px solid var(--primary-color);
            margin: var(--padding-sm) 0;
            box-shadow: var(--box-shadow);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .device-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        /* Responsive safety warning */
        .safety-warning {
            background: #fff3cd;
            border: 1px solid #ffecb5;
            border-radius: var(--border-radius);
            padding: var(--padding-sm);
            margin: var(--padding-sm) 0;
            font-size: clamp(0.875rem, 2.5vw, 1rem);
        }

        /* Enhanced step container */
        .step-container {
            background: #e8f5e8;
            padding: var(--padding-sm);
            border-radius: var(--border-radius);
            margin: 0.5rem 0;
            border-left: 3px solid #28a745;
            transition: all 0.2s ease;
        }

        .step-container:hover {
            background: #d4edda;
            border-left-width: 5px;
        }

        /* Responsive chat messages */
        .chat-message {
            padding: var(--padding-sm);
            margin: 0.5rem 0;
            border-radius: var(--border-radius);
            word-wrap: break-word;
            overflow-wrap: break-word;
        }

        .user-message {
            background: #e3f2fd;
            margin-left: clamp(0rem, 5vw, 2rem);
            border-left: 3px solid #2196f3;
        }

        .assistant-message {
            background: #f1f8e9;
            margin-right: clamp(0rem, 5vw, 2rem);
            border-left: 3px solid #4caf50;
        }

        /* Responsive button styling */
        .stButton > button {
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            border-radius: var(--border-radius);
            padding: var(--padding-xs) var(--padding-sm);
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
            min-height: 44px; /* Touch-friendly minimum */
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
        }

        /* Enhanced sidebar styling */
        .css-1d391kg {
            padding-top: var(--padding-sm);
        }

        /* Responsive text input and text area */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border-radius: var(--border-radius);
            border: 2px solid #e1e8ed;
            transition: border-color 0.2s ease;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(78, 205, 196, 0.2);
        }

        /* Mobile-specific optimizations */
        @media (max-width: 768px) {
            .main-header {
                font-size: clamp(1.2rem, 8vw, 2rem);
                padding: var(--padding-xs) 0;
            }

            .device-card {
                margin: var(--padding-xs) 0;
                padding: var(--padding-xs);
            }

            .chat-message {
                margin: 0.3rem 0;
                padding: var(--padding-xs);
            }

            .user-message,
            .assistant-message {
                margin-left: 0;
                margin-right: 0;
            }

            /* Improve button touch targets */
            .stButton > button {
                min-height: 48px;
                font-size: 16px; /* Prevent zoom on iOS */
            }

            /* Hide sidebar initially on mobile */
            .css-1d391kg {
                width: 100% !important;
            }
        }

        /* Tablet optimizations */
        @media (min-width: 769px) and (max-width: 1024px) {
            .main-header {
                font-size: clamp(2rem, 6vw, 2.5rem);
            }

            .user-message {
                margin-left: 1rem;
            }

            .assistant-message {
                margin-right: 1rem;
            }
        }

        /* Desktop optimizations */
        @media (min-width: 1025px) {
            .device-card {
                max-width: 800px;
                margin: var(--padding-sm) auto;
            }

            .chat-message {
                max-width: 85%;
            }

            .user-message {
                margin-left: auto;
                margin-right: 0;
            }

            .assistant-message {
                margin-left: 0;
                margin-right: auto;
            }
        }

        /* Enhanced accessibility */
        .stButton > button:focus,
        .stSelectbox > div > div:focus,
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
        }

        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            :root {
                --background-color: #2c3e50;
                --text-color: #ecf0f1;
            }

            .device-card {
                background: #34495e;
                color: var(--text-color);
            }

            .safety-warning {
                background: #f39c12;
                color: #2c3e50;
            }
        }

        /* Loading spinner enhancement */
        .stSpinner > div {
            border-top-color: var(--primary-color) !important;
        }

        /* Improved spacing for better visual hierarchy */
        .element-container {
            margin-bottom: var(--padding-xs);
        }

        /* Enhanced selectbox styling */
        .stSelectbox > div > div {
            border-radius: var(--border-radius);
        }

        /* File uploader enhancement */
        .stFileUploader > div {
            border-radius: var(--border-radius);
            border: 2px dashed var(--primary-color);
            transition: all 0.3s ease;
        }

        .stFileUploader > div:hover {
            border-color: var(--secondary-color);
            background-color: rgba(78, 205, 196, 0.05);
        }

        /* Progress bar enhancement */
        .stProgress .st-bo {
            background-color: var(--primary-color);
        }

        /* Success/error message styling */
        .stSuccess,
        .stError,
        .stWarning,
        .stInfo {
            border-radius: var(--border-radius);
            border: none;
            box-shadow: var(--box-shadow);
        }
        </style>
        """

    def apply_responsive_design(self) -> None:
        """
        Apply responsive design CSS to the current Streamlit page.
        This method should be called once per page load.
        """
        st.markdown(self.get_responsive_css(), unsafe_allow_html=True)

    def create_responsive_columns(
        self, mobile_ratio: List[int], tablet_ratio: List[int], desktop_ratio: List[int]
    ) -> List[Any]:
        """
        Create responsive columns that adapt to different screen sizes.

        Args:
            mobile_ratio: Column ratios for mobile devices
            tablet_ratio: Column ratios for tablet devices
            desktop_ratio: Column ratios for desktop devices

        Returns:
            List[Any]: Streamlit column objects
        """
        # Use JavaScript to detect screen size and choose appropriate ratio
        # For now, we'll use a sensible default that works across devices
        return st.columns(desktop_ratio)

    def create_mobile_friendly_form(
        self, title: str, fields: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a mobile-friendly form with proper spacing and touch targets.

        Args:
            title: Form title
            fields: List of field configurations

        Returns:
            Dict[str, Any]: Form field values
        """
        st.subheader(title)

        values = {}

        with st.form(key=f"mobile_form_{title.lower().replace(' ', '_')}"):
            for field in fields:
                field_type = field.get("type", "text")
                field_key = field.get("key", "")
                field_label = field.get("label", "")
                field_help = field.get("help", "")

                if field_type == "text":
                    values[field_key] = st.text_input(
                        field_label, help=field_help, key=f"mobile_{field_key}"
                    )
                elif field_type == "textarea":
                    values[field_key] = st.text_area(
                        field_label,
                        help=field_help,
                        height=100,
                        key=f"mobile_{field_key}",
                    )
                elif field_type == "selectbox":
                    values[field_key] = st.selectbox(
                        field_label,
                        field.get("options", []),
                        help=field_help,
                        key=f"mobile_{field_key}",
                    )
                elif field_type == "multiselect":
                    values[field_key] = st.multiselect(
                        field_label,
                        field.get("options", []),
                        help=field_help,
                        key=f"mobile_{field_key}",
                    )

            # Mobile-friendly submit button
            submitted = st.form_submit_button(
                "Submit", use_container_width=True, type="primary"
            )

        return values if submitted else {}

    def create_responsive_image_gallery(
        self,
        images: List[Dict[str, str]],
        mobile_cols: int = 1,
        tablet_cols: int = 2,
        desktop_cols: int = 3,
    ) -> None:
        """
        Create a responsive image gallery that adapts to screen size.

        Args:
            images: List of image dictionaries with 'url' and 'caption' keys
            mobile_cols: Number of columns on mobile
            tablet_cols: Number of columns on tablet
            desktop_cols: Number of columns on desktop
        """
        # Use CSS Grid for better responsive behavior
        st.markdown(
            f"""
        <style>
        .responsive-gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }}

        .gallery-item {{
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: var(--box-shadow);
            transition: transform 0.2s ease;
        }}

        .gallery-item:hover {{
            transform: scale(1.02);
        }}

        .gallery-item img {{
            width: 100%;
            height: auto;
            object-fit: cover;
        }}

        .gallery-caption {{
            padding: 0.5rem;
            background: var(--background-color);
            font-size: 0.875rem;
            text-align: center;
        }}

        @media (max-width: 768px) {{
            .responsive-gallery {{
                grid-template-columns: repeat({mobile_cols}, 1fr);
            }}
        }}

        @media (min-width: 769px) and (max-width: 1024px) {{
            .responsive-gallery {{
                grid-template-columns: repeat({tablet_cols}, 1fr);
            }}
        }}

        @media (min-width: 1025px) {{
            .responsive-gallery {{
                grid-template-columns: repeat({desktop_cols}, 1fr);
            }}
        }}
        </style>
        """,
            unsafe_allow_html=True,
        )

        gallery_html = '<div class="responsive-gallery">'
        for image in images:
            gallery_html += f"""
            <div class="gallery-item">
                <img src="{image.get('url', '')}" alt="{image.get('caption', '')}" />
                <div class="gallery-caption">{image.get('caption', '')}</div>
            </div>
            """
        gallery_html += "</div>"

        st.markdown(gallery_html, unsafe_allow_html=True)

    def add_touch_friendly_navigation(self, pages: Dict[str, str]) -> str:
        """
        Add touch-friendly navigation for mobile devices.

        Args:
            pages: Dictionary mapping page names to URLs or page keys

        Returns:
            str: Selected page key
        """
        st.markdown(
            """
        <style>
        .touch-nav {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 1rem 0;
            justify-content: center;
        }

        .nav-button {
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            min-height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: none;
            cursor: pointer;
        }

        .nav-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
        }

        .nav-button.active {
            background: var(--text-color);
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Use Streamlit radio buttons styled with custom CSS
        selected_page = st.radio(
            "Navigation",
            options=list(pages.keys()),
            format_func=lambda x: x,
            horizontal=True,
            label_visibility="collapsed",
        )

        return selected_page

    def optimize_for_mobile_performance(self) -> None:
        """
        Apply mobile performance optimizations.
        """
        # Add lazy loading and performance hints
        st.markdown(
            """
        <style>
        /* Reduce animation complexity on mobile */
        @media (max-width: 768px) {
            * {
                animation-duration: 0.1s !important;
                transition-duration: 0.1s !important;
            }
        }

        /* Optimize scrolling */
        .main .block-container {
            scroll-behavior: smooth;
        }

        /* Reduce motion for users who prefer it */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
        </style>
        """,
            unsafe_allow_html=True,
        )


def initialize_responsive_design() -> ResponsiveDesignManager:
    """
    Initialize and return a ResponsiveDesignManager instance.
    This function should be called once in the main application.

    Returns:
        ResponsiveDesignManager: Configured responsive design manager
    """
    manager = ResponsiveDesignManager()
    manager.apply_responsive_design()
    manager.optimize_for_mobile_performance()
    return manager


def enhance_ui_components() -> None:
    """
    Apply UI/UX enhancements to existing Streamlit components.
    This function improves the visual appeal and usability of standard components.
    """
    st.markdown(
        """
    <style>
    /* Enhanced component styling */
    .stAlert {
        border-radius: var(--border-radius);
        border: none;
        box-shadow: var(--box-shadow);
    }

    .stMetric {
        background: var(--background-color);
        padding: var(--padding-sm);
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
    }

    .stExpander {
        border: 1px solid #e1e8ed;
        border-radius: var(--border-radius);
        overflow: hidden;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: var(--border-radius) var(--border-radius) 0 0;
        background: var(--background-color);
    }

    /* Enhanced sidebar */
    .css-1d391kg .stSelectbox,
    .css-1d391kg .stTextInput,
    .css-1d391kg .stTextArea {
        margin-bottom: var(--padding-xs);
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
