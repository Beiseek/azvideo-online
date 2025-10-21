"""
User profile and related models.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Расширенный профиль пользователя."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('О себе', blank=True)
    birth_date = models.DateField('Дата рождения', blank=True, null=True)
    
    favorite_movies = models.ManyToManyField(
        'movies.Movie',
        verbose_name='Избранные фильмы',
        blank=True,
        related_name='favorited_by'
    )
    favorite_series = models.ManyToManyField(
        'movies.Series',
        verbose_name='Избранные сериалы',
        blank=True,
        related_name='favorited_by'
    )
    
    watchlist_movies = models.ManyToManyField(
        'movies.Movie',
        verbose_name='Список к просмотру (фильмы)',
        blank=True,
        related_name='in_watchlist'
    )
    watchlist_series = models.ManyToManyField(
        'movies.Series',
        verbose_name='Список к просмотру (сериалы)',
        blank=True,
        related_name='in_watchlist'
    )
    
    is_blocked = models.BooleanField('Заблокирован', default=False)
    
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f"Профиль {self.user.username}"


class UserActivity(models.Model):
    """История активности пользователя."""
    ACTIVITY_TYPES = [
        ('view', 'Просмотр'),
        ('rating', 'Оценка'),
        ('comment', 'Комментарий'),
        ('favorite', 'Добавление в избранное'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities', verbose_name='Пользователь')
    activity_type = models.CharField('Тип активности', max_length=20, choices=ACTIVITY_TYPES)
    
    content_type = models.CharField(
        'Тип контента',
        max_length=20,
        choices=[('movie', 'Фильм'), ('series', 'Сериал'), ('news', 'Новость')]
    )
    content_id = models.IntegerField('ID контента')
    content_title = models.CharField('Название контента', max_length=300)
    
    created_at = models.DateTimeField('Дата', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Активность пользователя'
        verbose_name_plural = 'Активности пользователей'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.content_title}"

