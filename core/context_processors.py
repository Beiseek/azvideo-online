"""
Context processors for global template variables.
"""
from django.conf import settings


def site_settings(request):
    """Добавляет общие настройки сайта в контекст."""
    return {
        'SITE_NAME': 'KinoSite',
        'LANGUAGES': settings.LANGUAGES,
        'CURRENT_LANGUAGE': request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else 'uz',
    }


def google_analytics(request):
    """Добавляет Google Analytics ID в контекст."""
    return {
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
    }

