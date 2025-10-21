"""
Views for movies app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.utils.translation import get_language
from django.views.decorators.cache import cache_page
from .models import Movie, Series, Genre, Country, News, Comment, Rating, StaticPage
from .filters import MovieFilter, SeriesFilter
from users.models import UserActivity


class HomeView(ListView):
    """Главная страница с каталогом."""
    model = Movie
    template_name = 'movies/index.html'
    context_object_name = 'movies'
    paginate_by = 20
    
    def get_queryset(self):
        return Movie.objects.filter(is_published=True).select_related().prefetch_related(
            'genres', 'countries', 'directors', 'actors'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Рекомендуемые фильмы для слайдера
        context['featured_movies'] = Movie.objects.filter(
            is_published=True,
            is_featured=True
        ).order_by('-rating_avg')[:5]
        
        # Популярные фильмы
        context['popular_movies'] = Movie.objects.filter(
            is_published=True
        ).order_by('-views')[:12]
        
        # Новые сериалы
        context['new_series'] = Series.objects.filter(
            is_published=True
        ).order_by('-created_at')[:8]
        
        # Жанры для фильтра
        context['genres'] = Genre.objects.all()
        context['countries'] = Country.objects.all()
        
        # Новости
        context['latest_news'] = News.objects.filter(is_published=True).order_by('-created_at')[:4]
        
        return context


class MovieListView(ListView):
    """Список фильмов с фильтрацией."""
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Movie.objects.filter(is_published=True).select_related().prefetch_related(
            'genres', 'countries'
        )
        self.filterset = MovieFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['genres'] = Genre.objects.all()
        context['countries'] = Country.objects.all()
        return context


class SeriesListView(ListView):
    """Список сериалов с фильтрацией."""
    model = Series
    template_name = 'movies/series_list.html'
    context_object_name = 'series'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Series.objects.filter(is_published=True).select_related().prefetch_related(
            'genres', 'countries'
        )
        self.filterset = SeriesFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['genres'] = Genre.objects.all()
        context['countries'] = Country.objects.all()
        return context


class MovieDetailView(DetailView):
    """Детальная страница фильма."""
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'
    
    def get_queryset(self):
        return Movie.objects.filter(is_published=True).prefetch_related(
            'genres', 'countries', 'directors', 'actors', 'comments'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.object
        
        # Увеличение счетчика просмотров
        self.request.content_object = movie
        
        # Комментарии (только одобренные)
        context['comments'] = movie.comments.filter(is_approved=True).select_related('user')
        
        # Рейтинг пользователя
        if self.request.user.is_authenticated:
            try:
                context['user_rating'] = Rating.objects.get(
                    user=self.request.user,
                    movie=movie
                ).score
            except Rating.DoesNotExist:
                context['user_rating'] = None
            
            # Проверка избранного
            context['is_favorite'] = self.request.user.profile.favorite_movies.filter(id=movie.id).exists()
            context['in_watchlist'] = self.request.user.profile.watchlist_movies.filter(id=movie.id).exists()
        
        # Похожие фильмы (по жанрам)
        movie_genres = movie.genres.all()
        context['similar_movies'] = Movie.objects.filter(
            is_published=True,
            genres__in=movie_genres
        ).exclude(id=movie.id).distinct().order_by('-rating_avg')[:6]
        
        # Запись активности
        if self.request.user.is_authenticated:
            UserActivity.objects.create(
                user=self.request.user,
                activity_type='view',
                content_type='movie',
                content_id=movie.id,
                content_title=movie.title_uz
            )
        
        return context


class SeriesDetailView(DetailView):
    """Детальная страница сериала."""
    model = Series
    template_name = 'movies/series_detail.html'
    context_object_name = 'series'
    
    def get_queryset(self):
        return Series.objects.filter(is_published=True).prefetch_related(
            'genres', 'countries', 'directors', 'actors', 'seasons__episodes', 'comments'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series = self.object
        
        # Увеличение счетчика просмотров
        self.request.content_object = series
        
        # Сезоны и эпизоды
        context['seasons'] = series.seasons.all().prefetch_related('episodes')
        
        # Комментарии (только одобренные)
        context['comments'] = series.comments.filter(is_approved=True).select_related('user')
        
        # Рейтинг пользователя
        if self.request.user.is_authenticated:
            try:
                context['user_rating'] = Rating.objects.get(
                    user=self.request.user,
                    series=series
                ).score
            except Rating.DoesNotExist:
                context['user_rating'] = None
            
            # Проверка избранного
            context['is_favorite'] = self.request.user.profile.favorite_series.filter(id=series.id).exists()
            context['in_watchlist'] = self.request.user.profile.watchlist_series.filter(id=series.id).exists()
        
        # Похожие сериалы
        series_genres = series.genres.all()
        context['similar_series'] = Series.objects.filter(
            is_published=True,
            genres__in=series_genres
        ).exclude(id=series.id).distinct().order_by('-rating_avg')[:6]
        
        # Запись активности
        if self.request.user.is_authenticated:
            UserActivity.objects.create(
                user=self.request.user,
                activity_type='view',
                content_type='series',
                content_id=series.id,
                content_title=series.title_uz
            )
        
        return context


class SearchView(ListView):
    """Поиск по фильмам и сериалам."""
    template_name = 'movies/search.html'
    context_object_name = 'results'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        content_type = self.request.GET.get('type', 'all')
        
        if not query:
            return []
        
        # Поиск по фильмам
        movies_q = Q(title_az__icontains=query) | Q(title_uz__icontains=query) | Q(original_title__icontains=query)
        movies_q |= Q(description_az__icontains=query) | Q(description_uz__icontains=query)
        movies_q |= Q(actors__name__icontains=query) | Q(directors__name__icontains=query)
        
        results = []
        
        if content_type in ['all', 'movie']:
            movies = Movie.objects.filter(movies_q, is_published=True).distinct()
            results.extend([{'type': 'movie', 'object': m} for m in movies])
        
        if content_type in ['all', 'series']:
            series = Series.objects.filter(movies_q, is_published=True).distinct()
            results.extend([{'type': 'series', 'object': s} for s in series])
        
        return results
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['content_type'] = self.request.GET.get('type', 'all')
        return context


class GenreView(ListView):
    """Вывод фильмов и сериалов по жанру."""
    template_name = 'movies/genre.html'
    context_object_name = 'content_list'
    paginate_by = 24

    def get_queryset(self):
        self.genre = get_object_or_404(Genre, slug=self.kwargs['slug'])
        
        # Получаем фильмы и сериалы как объекты
        movies = Movie.objects.filter(genres=self.genre, is_published=True).select_related().prefetch_related('genres')
        series = Series.objects.filter(genres=self.genre, is_published=True).select_related().prefetch_related('genres')
        
        # Объединяем и сортируем
        content_list = []
        
        # Добавляем фильмы
        for movie in movies:
            content_list.append({
                'object': movie,
                'content_type': 'movie',
                'year': movie.year,
                'rating_avg': movie.rating_avg
            })
        
        # Добавляем сериалы
        for series in series:
            content_list.append({
                'object': series,
                'content_type': 'series', 
                'year': series.year,
                'rating_avg': series.rating_avg
            })
        
        # Сортируем по году
        content_list.sort(key=lambda x: x['year'] if x['year'] else 0, reverse=True)
        
        return content_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre'] = self.genre
        return context


def add_to_favorites(request, content_type, content_id):
    # Логика добавления в избранное
    pass

def add_to_watchlist(request, content_type, content_id):
    # Логика добавления в список "посмотреть позже"
    pass


class StaticPageView(DetailView):
    """Отображение статических страниц."""
    model = StaticPage
    template_name = 'movies/static_page.html'
    context_object_name = 'page'
    
    def get_object(self):
        page_type = self.kwargs.get('page_type')
        return get_object_or_404(StaticPage, page_type=page_type, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.object
        
        context['title'] = page.title_uz
        context['content'] = page.content_uz
        
        return context


class NewsListView(ListView):
    model = News
    template_name = 'movies/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 12

    def get_queryset(self):
        return News.objects.filter(is_published=True).order_by('-created_at')


class NewsDetailView(DetailView):
    model = News
    template_name = 'movies/news_detail.html'
    context_object_name = 'news'

    def get_queryset(self):
        return News.objects.filter(is_published=True)

