"""
Custom middleware for kinosite project.
"""
from django.utils import translation
from django.conf import settings
import geoip2.database
import geoip2.errors
from pathlib import Path


class AdminLanguageMiddleware:
    """Force Russian language in Django admin, keep site language unaffected."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin'):
            translation.activate('ru')
            request.LANGUAGE_CODE = 'ru'
        return self.get_response(request)


class LanguageDetectionMiddleware:
    """
    Автоматическое определение языка пользователя по IP-адресу.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.reader = None
        
        # Инициализация GeoIP2 reader
        geoip_path = Path(settings.GEOIP_PATH) / 'GeoLite2-Country.mmdb'
        if geoip_path.exists():
            try:
                self.reader = geoip2.database.Reader(str(geoip_path))
            except Exception as e:
                print(f"GeoIP2 initialization error: {e}")

    def __call__(self, request):
        # Если это админка, язык уже активирован в AdminLanguageMiddleware
        if request.path.startswith('/admin'):
            return self.get_response(request)
        # Всегда активируем азербайджанский для фронта
        language = 'az'
        translation.activate(language)
        request.session['django_language'] = language
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Получение реального IP-адреса клиента."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ViewCountMiddleware:
    """
    Подсчет просмотров фильмов/сериалов.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Увеличение счетчика просмотров для детальных страниц
        if hasattr(request, 'content_object'):
            content = request.content_object
            if hasattr(content, 'views'):
                content.views += 1
                content.save(update_fields=['views'])
        
        return response

