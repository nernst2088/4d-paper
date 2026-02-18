from fastapi import Request
from src.core.i18n.translator import translator

async def get_language(request: Request):
    """Get language setting from request"""
    # Get language preference from request header
    accept_language = request.headers.get('Accept-Language', 'en')
    # Extract first language code (e.g. 'en-US,en;q=0.9' -> 'en')
    language = accept_language.split(',')[0].split(';')[0].split('-')[0]
    translator.set_language(language)
    return language

# Language dependency
LanguageDependency = get_language
