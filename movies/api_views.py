"""
API Views for movies app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Movie, Series, Rating, Comment
from .serializers import (
    MovieListSerializer, SeriesListSerializer,
    RatingSerializer, CommentSerializer
)
from users.models import UserActivity


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """API для фильмов."""
    queryset = Movie.objects.filter(is_published=True)
    serializer_class = MovieListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        """Оценка фильма."""
        movie = self.get_object()
        score = request.data.get('score')
        
        if not score or not (1 <= int(score) <= 5):
            return Response(
                {'error': 'Score must be between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            content_type='movie',
            movie=movie,
            defaults={'score': int(score)}
        )
        
        # Запись активности
        if created:
            UserActivity.objects.create(
                user=request.user,
                activity_type='rating',
                content_type='movie',
                content_id=movie.id,
                content_title=movie.title_uz
            )
        
        serializer = RatingSerializer(rating)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def user_rating(self, request, pk=None):
        """Получить рейтинг пользователя."""
        movie = self.get_object()
        
        if not request.user.is_authenticated:
            return Response({'rating': None})
        
        try:
            rating = Rating.objects.get(user=request.user, movie=movie)
            return Response({'rating': rating.score})
        except Rating.DoesNotExist:
            return Response({'rating': None})


class SeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """API для сериалов."""
    queryset = Series.objects.filter(is_published=True)
    serializer_class = SeriesListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        """Оценка сериала."""
        series = self.get_object()
        score = request.data.get('score')
        
        if not score or not (1 <= int(score) <= 5):
            return Response(
                {'error': 'Score must be between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            content_type='series',
            series=series,
            defaults={'score': int(score)}
        )
        
        # Запись активности
        if created:
            UserActivity.objects.create(
                user=request.user,
                activity_type='rating',
                content_type='series',
                content_id=series.id,
                content_title=series.title_uz
            )
        
        serializer = RatingSerializer(rating)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def user_rating(self, request, pk=None):
        """Получить рейтинг пользователя."""
        series = self.get_object()
        
        if not request.user.is_authenticated:
            return Response({'rating': None})
        
        try:
            rating = Rating.objects.get(user=request.user, series=series)
            return Response({'rating': rating.score})
        except Rating.DoesNotExist:
            return Response({'rating': None})


class CommentViewSet(viewsets.ModelViewSet):
    """API для комментариев."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Comment.objects.filter(is_approved=True)
        
        # Фильтрация по контенту
        content_type = self.request.query_params.get('content_type')
        content_id = self.request.query_params.get('content_id')
        
        if content_type == 'movie' and content_id:
            queryset = queryset.filter(movie_id=content_id, parent__isnull=True)
        elif content_type == 'series' and content_id:
            queryset = queryset.filter(series_id=content_id, parent__isnull=True)
        
        return queryset.select_related('user').prefetch_related('children')
    
    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        
        # Запись активности
        content = comment.movie if comment.movie else comment.series
        if content:
            UserActivity.objects.create(
                user=self.request.user,
                activity_type='comment',
                content_type=comment.content_type,
                content_id=content.id,
                content_title=content.title_uz
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request):
    """Переключение избранного."""
    content_type = request.data.get('content_type')
    content_id = request.data.get('content_id')
    
    if content_type == 'movie':
        movie = get_object_or_404(Movie, id=content_id)
        if request.user.profile.favorite_movies.filter(id=movie.id).exists():
            request.user.profile.favorite_movies.remove(movie)
            is_favorite = False
        else:
            request.user.profile.favorite_movies.add(movie)
            is_favorite = True
    elif content_type == 'series':
        series = get_object_or_404(Series, id=content_id)
        if request.user.profile.favorite_series.filter(id=series.id).exists():
            request.user.profile.favorite_series.remove(series)
            is_favorite = False
        else:
            request.user.profile.favorite_series.add(series)
            is_favorite = True
    else:
        return Response({'error': 'Invalid content type'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'is_favorite': is_favorite})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_watchlist(request):
    """Переключение списка к просмотру."""
    content_type = request.data.get('content_type')
    content_id = request.data.get('content_id')
    
    if content_type == 'movie':
        movie = get_object_or_404(Movie, id=content_id)
        if request.user.profile.watchlist_movies.filter(id=movie.id).exists():
            request.user.profile.watchlist_movies.remove(movie)
            in_watchlist = False
        else:
            request.user.profile.watchlist_movies.add(movie)
            in_watchlist = True
    elif content_type == 'series':
        series = get_object_or_404(Series, id=content_id)
        if request.user.profile.watchlist_series.filter(id=series.id).exists():
            request.user.profile.watchlist_series.remove(series)
            in_watchlist = False
        else:
            request.user.profile.watchlist_series.add(series)
            in_watchlist = True
    else:
        return Response({'error': 'Invalid content type'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'in_watchlist': in_watchlist})

