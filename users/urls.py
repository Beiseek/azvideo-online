"""
URL configuration for users app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('favorites/', views.favorites, name='favorites'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('history/', views.history, name='history'),
]

