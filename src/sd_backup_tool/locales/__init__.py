# -*- coding: utf-8 -*-
"""
Language manager module for SD Backup Tool
Uses a single translations file with English comments for reference
"""

from . import translations

# Available languages (currently only Traditional Chinese)
LANGUAGES = {
    'zh_TW': translations.UI_TEXT,  # Traditional Chinese (default)
}

# Default language
DEFAULT_LANG = 'zh_TW'

class LanguageManager:
    """Language manager class"""
    
    def __init__(self):
        """Initialize language manager"""
        self.current_lang = DEFAULT_LANG
        self.texts = LANGUAGES[self.current_lang]
    
    def get_text(self, key, *args, **kwargs):
        """Get text for the given key with optional formatting"""
        try:
            text = self.texts.get(key, key)
            if args or kwargs:
                return text.format(*args, **kwargs)
            return text
        except Exception as e:
            print(f"Error formatting text for key '{key}': {e}")
            return key
    
    def set_language(self, lang_code):
        """Set current language"""
        if lang_code in LANGUAGES:
            self.current_lang = lang_code
            self.texts = LANGUAGES[lang_code]
            return True
        return False
    
    def get_available_languages(self):
        """Get list of available languages"""
        return list(LANGUAGES.keys())
    
    def get_current_language(self):
        """Get current language code"""
        return self.current_lang 