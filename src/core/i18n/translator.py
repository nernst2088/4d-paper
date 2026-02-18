import gettext
import os
from typing import Optional

class Translator:
    def __init__(self):
        self.locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
        self.translators = {}
        self.current_language = 'en'
        self._ensure_locales_dir()
        self._load_default_languages()
    
    def _ensure_locales_dir(self):
        """Ensure language directory exists"""
        if not os.path.exists(self.locales_dir):
            os.makedirs(self.locales_dir)
    
    def _load_default_languages(self):
        """Load default languages"""
        # Load at least English
        self.load_language('en')
    
    def load_language(self, language: str) -> bool:
        """Load specified language"""
        if language not in self.translators:
            try:
                lang_dir = os.path.join(self.locales_dir, language, 'LC_MESSAGES')
                if os.path.exists(lang_dir):
                    translator = gettext.translation('messages', self.locales_dir, [language])
                    self.translators[language] = translator
                    return True
                else:
                    # If language files don't exist, create a basic translator
                    self.translators[language] = gettext.NullTranslations()
                    return True
            except Exception as e:
                print(f"Error loading language {language}: {e}")
                return False
        return True
    
    def set_language(self, language: str) -> bool:
        """Set current language"""
        if self.load_language(language):
            self.current_language = language
            return True
        return False
    
    def gettext(self, message: str) -> str:
        """Translate text"""
        if self.current_language in self.translators:
            return self.translators[self.current_language].gettext(message)
        return message

# Global translation instance
translator = Translator()
_ = translator.gettext
