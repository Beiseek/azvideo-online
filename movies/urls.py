"""
URL configuration for movies app.
"""
from django.urls import path, include
from . import views
from . import admin_views
from . import video_views

urlpatterns = [
    # Главная страница
    path('', views.HomeView.as_view(), name='home'),
    
    # Фильмы
    path('movies/', views.MovieListView.as_view(), name='movie_list'),
    path('movie/<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail'),
    
    # Сериалы
    path('series/', views.SeriesListView.as_view(), name='series_list'),
    path('series/<slug:slug>/', views.SeriesDetailView.as_view(), name='series_detail'),
    
    # Поиск
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Жанры
    path('genre/<slug:slug>/', views.GenreView.as_view(), name='genre'),
    
    # Избранное и списки
    path('favorites/add/<str:content_type>/<int:content_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('watchlist/add/<str:content_type>/<int:content_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    
    # Статичные страницы
    path('page/<str:page_type>/', views.StaticPageView.as_view(), name='static_page'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),
    
    # URL для отдачи видео
    path('media/movie/<slug:slug>/', video_views.serve_movie_video, name='serve_movie_video'),
    path('media/series/<slug:series_slug>/<int:season_num>/<int:episode_num>/', video_views.serve_episode_video, name='serve_episode_video'),

    # Admin API endpoints
    path('admin/movies/episode/get-next-number/', admin_views.get_next_episode_number, name='get_next_episode_number'),
    path('admin/movies/season/get-next-number/', admin_views.get_next_season_number, name='get_next_season_number'),

    # API
    path('api/v1/', include('movies.api_urls')),
]

