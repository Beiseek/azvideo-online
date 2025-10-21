"""
Sitemaps for SEO.
"""
from django.contrib.sitemaps import Sitemap
from .models import Movie, Series, News


class MovieSitemap(Sitemap):
    """Sitemap для фильмов."""
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return Movie.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.updated_at


class SeriesSitemap(Sitemap):
    """Sitemap для сериалов."""
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return Series.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.updated_at


class NewsSitemap(Sitemap):
    """Sitemap для новостей."""
    changefreq = "daily"
    priority = 0.6
    
    def items(self):
        return News.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.updated_at

