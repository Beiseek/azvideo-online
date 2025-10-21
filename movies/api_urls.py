"""
API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    MovieViewSet, SeriesViewSet, CommentViewSet,
    toggle_favorite, toggle_watchlist
)

router = DefaultRouter()
router.register('movies', MovieViewSet)
router.register('series', SeriesViewSet)
router.register('comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('favorites/toggle/', toggle_favorite, name='api_toggle_favorite'),
    path('watchlist/toggle/', toggle_watchlist, name='api_toggle_watchlist'),
]

