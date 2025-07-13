"""
Language selector component for RepairGPT
"""

import streamlit as st
from i18n import i18n


def language_selector():
    """
    Language selector widget for the sidebar
    """
    st.sidebar.markdown("---")
    
    # Language selection
    languages = {
        'en': 'English 🇺🇸',
        'ja': '日本語 🇯🇵'
    }
    
    current_language = st.session_state.get('language', 'en')
    
    selected_language = st.sidebar.selectbox(
        "🌐 Language / 言語",
        options=list(languages.keys()),
        format_func=lambda x: languages[x],
        index=list(languages.keys()).index(current_language),
        key="language_selector"
    )
    
    # Update language if changed
    if selected_language != current_language:
        st.session_state.language = selected_language
        i18n.set_language(selected_language)
        st.rerun()
    
    return selected_language


def get_localized_device_categories():
    """
    Get device categories in the current language
    """
    from i18n import _
    
    return [
        _("ui.placeholders.select_device"),
        _("devices.nintendo_switch"),
        _("devices.nintendo_switch_lite"), 
        _("devices.nintendo_switch_oled"),
        _("devices.iphone"),
        _("devices.ipad"),
        _("devices.macbook"),
        _("devices.imac"),
        _("devices.playstation_5"),
        _("devices.playstation_4"),
        _("devices.xbox_series"),
        _("devices.xbox_one"),
        _("devices.samsung_galaxy"),
        _("devices.google_pixel"),
        _("devices.gaming_pc"),
        _("devices.laptop"),
        _("devices.desktop_pc"),
        _("devices.other")
    ]


def get_localized_skill_levels():
    """
    Get skill levels in the current language
    """
    from i18n import _
    
    return [
        _("skill_levels.beginner"),
        _("skill_levels.intermediate"),
        _("skill_levels.expert")
    ]