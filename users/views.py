"""
Views for users app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, UserActivity
from movies.models import Movie, Series
from .forms import UserProfileForm


@login_required
def profile(request):
    """Страница профиля пользователя."""
    profile = request.user.profile
    activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')[:20]
    
    context = {
        'profile': profile,
        'activities': activities,
    }
    return render(request, 'users/profile.html', context)


@login_required
def favorites(request):
    """Избранное пользователя."""
    profile = request.user.profile
    favorite_movies = profile.favorite_movies.all()
    favorite_series = profile.favorite_series.all()
    
    context = {
        'favorite_movies': favorite_movies,
        'favorite_series': favorite_series,
    }
    return render(request, 'users/favorites.html', context)


@login_required
def watchlist(request):
    """Список к просмотру."""
    profile = request.user.profile
    watchlist_movies = profile.watchlist_movies.all()
    watchlist_series = profile.watchlist_series.all()
    
    context = {
        'watchlist_movies': watchlist_movies,
        'watchlist_series': watchlist_series,
    }
    return render(request, 'users/watchlist.html', context)


@login_required
def history(request):
    """История активности."""
    activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')
    
    for activity in activities:
        if activity.content_type == 'movie':
            try:
                movie = Movie.objects.get(id=activity.content_id)
                activity.content_slug = movie.slug
            except Movie.DoesNotExist:
                activity.content_slug = None
        elif activity.content_type == 'series':
            try:
                series = Series.objects.get(id=activity.content_id)
                activity.content_slug = series.slug
            except Series.DoesNotExist:
                activity.content_slug = None

    context = {
        'activities': activities,
    }
    return render(request, 'users/history.html', context)

