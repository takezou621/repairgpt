"""
Internationalization (i18n) module for RepairGPT
Supports Japanese and English languages
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class I18n:
    """Internationalization handler for RepairGPT"""

    def __init__(self, default_language: str = "en"):
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.locales_dir = Path(__file__).parent / "locales"

        # Load all available translations
        self._load_translations()

    def _load_translations(self):
        """Load translation files from locales directory"""
        if not self.locales_dir.exists():
            self.locales_dir.mkdir(parents=True, exist_ok=True)
            return

        for locale_file in self.locales_dir.glob("*.json"):
            language_code = locale_file.stem
            try:
                with open(locale_file, "r", encoding="utf-8") as f:
                    self.translations[language_code] = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load translation file {locale_file}: {e}")

    def set_language(self, language: str):
        """Set the current language"""
        if language in self.translations:
            self.current_language = language
        else:
            print(
                f"Warning: Language '{language}' not available, using default '{self.default_language}'"
            )
            self.current_language = self.default_language

    def get_language(self) -> str:
        """Get the current language"""
        return self.current_language

    def get_available_languages(self) -> list:
        """Get list of available languages"""
        return list(self.translations.keys())

    def t(self, key: str, **kwargs) -> str:
        """
        Translate a key to the current language

        Args:
            key: Translation key (supports dot notation, e.g., 'ui.buttons.submit')
            **kwargs: Parameters for string formatting

        Returns:
            Translated string
        """
        # Get translation for current language
        translation = self._get_nested_value(
            self.translations.get(self.current_language, {}), key
        )

        # Fallback to default language if not found
        if translation is None and self.current_language != self.default_language:
            translation = self._get_nested_value(
                self.translations.get(self.default_language, {}), key
            )

        # Fallback to key itself if still not found
        if translation is None:
            return key

        # Format with parameters if provided
        if kwargs:
            try:
                return translation.format(**kwargs)
            except (KeyError, ValueError):
                return translation

        return translation

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Optional[str]:
        """Get nested dictionary value using dot notation"""
        keys = key.split(".")
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return current if isinstance(current, str) else None

    def reload_translations(self):
        """Reload all translation files"""
        self.translations.clear()
        self._load_translations()


# Global i18n instance
i18n = I18n()


# Convenience function for translation
def _(key: str, **kwargs) -> str:
    """Shorthand for i18n.t()"""
    return i18n.t(key, **kwargs)
