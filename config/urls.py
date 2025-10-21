"""
URL configuration for kinosite project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps_config import sitemaps
from core.views import RobotsTxtView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movies.urls')),
    path('users/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/', include('movies.api_urls')),

    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # robots.txt
    path("robots.txt", RobotsTxtView.as_view()),
]

# Custom admin site titles
admin.site.site_header = "Киносайт - Панель Управления"
admin.site.site_title = "Администрирование"
admin.site.index_title = "Добро пожаловать в панель управления"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

