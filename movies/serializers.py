"""
Serializers for REST API.
"""
from rest_framework import serializers
from .models import Movie, Series, Rating, Comment, Genre
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра."""
    class Meta:
        model = Genre
        fields = ['id', 'name_uz', 'name_az', 'slug']


class RatingSerializer(serializers.ModelSerializer):
    """Сериализатор рейтинга."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'user', 'content_type', 'movie', 'series', 'score', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def create(self, validated_data):
        # Получаем или обновляем рейтинг пользователя
        user = self.context['request'].user
        content_type = validated_data['content_type']
        
        if content_type == 'movie':
            rating, created = Rating.objects.update_or_create(
                user=user,
                content_type=content_type,
                movie=validated_data['movie'],
                defaults={'score': validated_data['score']}
            )
        else:
            rating, created = Rating.objects.update_or_create(
                user=user,
                content_type=content_type,
                series=validated_data['series'],
                defaults={'score': validated_data['score']}
            )
        
        return rating


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'content_type', 'movie', 'series',
            'parent', 'text', 'is_approved', 'created_at', 'replies'
        ]
        read_only_fields = ['user', 'is_approved', 'created_at']
    
    def get_replies(self, obj):
        if obj.children.exists():
            return CommentSerializer(obj.children.filter(is_approved=True), many=True).data
        return []
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # По умолчанию комментарии требуют модерации
        validated_data['is_approved'] = False
        return super().create(validated_data)


class MovieListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка фильмов."""
    genres = GenreSerializer(many=True, read_only=True)
    
    class Meta:
        model = Movie
        fields = [
            'id', 'title_uz', 'title_az', 'slug', 'poster',
            'year', 'genres', 'rating_avg', 'rating_count', 'views'
        ]


class SeriesListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка сериалов."""
    genres = GenreSerializer(many=True, read_only=True)
    
    class Meta:
        model = Series
        fields = [
            'id', 'title_uz', 'title_az', 'slug', 'poster',
            'year', 'genres', 'rating_avg', 'rating_count', 'views', 'status'
        ]

