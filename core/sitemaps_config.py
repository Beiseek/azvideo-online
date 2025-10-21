from django.contrib import sitemaps
from django.urls import reverse
from movies.models import Movie, Series, StaticPage

class MovieSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Movie.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

class SeriesSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Series.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        # List of static page names
        return ['home', 'movie_list', 'series_list']

    def location(self, item):
        return reverse(item)

sitemaps = {
    'movies': MovieSitemap,
    'series': SeriesSitemap,
    'static': StaticViewSitemap,
}
