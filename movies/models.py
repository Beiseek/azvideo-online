"""
Models for movies and series.
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from mptt.models import MPTTModel, TreeForeignKey
# from ckeditor.fields import RichTextField
from unidecode import unidecode


class Genre(models.Model):
    """Model for movie and series genres"""
    name = models.CharField(max_length=100, unique=True, verbose_name='Название (EN)', help_text='Original genre name from TMDB (e.g., Action)')
    name_uz = models.CharField(max_length=100, verbose_name='Название (UZ)', blank=True)
    name_az = models.CharField(max_length=100, verbose_name='Название (AZ)', blank=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name_az']

    def __str__(self):
        return self.name_az or self.name_uz or self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)


class Country(models.Model):
    """Страны производства."""
    name_uz = models.CharField('Название (UZ)', max_length=100)
    name_az = models.CharField('Название (AZ)', max_length=100, blank=True)
    code = models.CharField('Код', max_length=3, unique=True)

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'
        ordering = ['name_az']

    def __str__(self):
        return self.name_az or self.name_uz


class Person(models.Model):
    """Актеры, режиссеры и другие персоны."""
    ROLE_CHOICES = [
        ('actor', 'Актер'),
        ('director', 'Режиссер'),
        ('writer', 'Сценарист'),
        ('producer', 'Продюсер'),
    ]

    name = models.CharField('Имя', max_length=200)
    photo = models.ImageField('Фото', upload_to='persons/', blank=True, null=True)
    photo_thumbnail = ImageSpecField(
        source='photo',
        processors=[ResizeToFill(200, 300)],
        format='JPEG',
        options={'quality': 85}
    )
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='actor')
    bio_uz = models.TextField('Биография (UZ)', blank=True)
    bio_az = models.TextField('Биография (AZ)', blank=True)
    birth_date = models.DateField('Дата рождения', blank=True, null=True)
    tmdb_id = models.IntegerField('TMDB ID', blank=True, null=True, unique=True)

    class Meta:
        verbose_name = 'Персона'
        verbose_name_plural = 'Персоны'
        ordering = ['name']

    def __str__(self):
        return self.name


class BaseContent(models.Model):
    """Базовая модель для фильмов и сериалов."""
    CONTENT_TYPE_CHOICES = [
        ('movie', 'Фильм'),
        ('series', 'Сериал'),
        ('cartoon', 'Мультфильм'),
    ]

    title_uz = models.CharField('Название (UZ)', max_length=300)
    title_az = models.CharField('Название (AZ)', max_length=300, blank=True)
    original_title = models.CharField('Оригинальное название', max_length=300, blank=True)
    slug = models.SlugField('URL', max_length=300, unique=True)

    description_uz = models.TextField('Описание (UZ)', blank=True)
    description_az = models.TextField('Описание (AZ)', blank=True)

    poster = models.ImageField('Постер', upload_to='posters/', blank=True, null=True)
    poster_thumbnail = ImageSpecField(
        source='poster',
        processors=[ResizeToFill(300, 450)],
        format='JPEG',
        options={'quality': 90}
    )

    backdrop = models.ImageField('Фон', upload_to='backdrops/', blank=True, null=True)

    video_file = models.FileField('Файл фильма', upload_to='movies/', blank=True, null=True, help_text='Загрузите основной файл фильма')

    trailer_url = models.URLField('URL Трейлера', blank=True, help_text='YouTube или Vimeo URL')

    year = models.IntegerField('Год выпуска', validators=[MinValueValidator(1900), MaxValueValidator(2100)], blank=True, null=True)
    duration = models.IntegerField('Длительность (мин)', blank=True, null=True)

    content_type = models.CharField('Тип контента', max_length=20, choices=CONTENT_TYPE_CHOICES, default='movie')

    genres = models.ManyToManyField(Genre, verbose_name='Жанры', related_name='%(class)s_set', blank=True)
    countries = models.ManyToManyField(Country, verbose_name='Страны', related_name='%(class)s_set', blank=True)

    directors = models.ManyToManyField(
        Person,
        verbose_name='Режиссеры',
        related_name='%(class)s_directed',
        limit_choices_to={'role': 'director'},
        blank=True
    )
    actors = models.ManyToManyField(
        Person,
        verbose_name='Актеры',
        related_name='%(class)s_acted',
        limit_choices_to={'role': 'actor'},
        blank=True
    )

    rating_avg = models.DecimalField('Средний рейтинг', max_digits=3, decimal_places=2, default=0)
    rating_count = models.IntegerField('Количество оценок', default=0)

    views = models.IntegerField('Просмотры', default=0)

    is_featured = models.BooleanField('Рекомендуемое', default=False, help_text='Показывать в слайдере на главной')
    is_published = models.BooleanField('Опубликовано', default=True)

    tmdb_id = models.IntegerField('TMDB ID', blank=True, null=True)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode(self.title_az or self.title_uz or self.original_title or 'untitled'))
            self.slug = base_slug
            
            # Проверяем уникальность и добавляем суффикс при необходимости
            counter = 1
            while self.__class__.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def update_rating(self):
        """Обновление среднего рейтинга."""
        ratings = self.ratings.all()
        if ratings:
            self.rating_avg = sum(r.score for r in ratings) / len(ratings)
            self.rating_count = len(ratings)
        else:
            self.rating_avg = 0
            self.rating_count = 0
        self.save(update_fields=['rating_avg', 'rating_count'])


class Movie(BaseContent):
    """Модель фильма."""

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title_az or self.title_uz

    def get_absolute_url(self):
        return reverse('movie_detail', kwargs={'slug': self.slug})


class Series(BaseContent):
    """Модель сериала."""
    seasons_count = models.IntegerField('Количество сезонов', default=1)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=[
            ('ongoing', 'В производстве'),
            ('completed', 'Завершен'),
            ('cancelled', 'Отменен'),
        ],
        default='ongoing'
    )

    class Meta:
        verbose_name = 'Сериал'
        verbose_name_plural = 'Сериалы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title_az or self.title_uz

    def get_absolute_url(self):
        return reverse('series_detail', kwargs={'slug': self.slug})


class Season(models.Model):
    """Сезон сериала."""
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='seasons', verbose_name='Сериал')
    season_number = models.PositiveIntegerField('Номер сезона')
    title_uz = models.CharField('Название (UZ)', max_length=200, blank=True)
    title_az = models.CharField('Название (AZ)', max_length=200, blank=True)
    description_uz = models.TextField('Описание (UZ)', blank=True)
    description_az = models.TextField('Описание (AZ)', blank=True)
    poster = models.ImageField('Постер', upload_to='seasons/', blank=True, null=True)
    release_date = models.DateField('Дата выхода', blank=True, null=True)

    class Meta:
        verbose_name = 'Сезон'
        verbose_name_plural = 'Сезоны'
        ordering = ['series', 'season_number']
        unique_together = ['series', 'season_number']

    @property
    def display_number(self):
        return self.season_number + 1

    def __str__(self):
        return f"{(self.series.title_az or self.series.title_uz)} - Сезон {self.display_number}"


class Episode(models.Model):
    """Эпизод сериала."""
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes', verbose_name='Сезон')
    episode_number = models.PositiveIntegerField('Номер эпизода')
    title_uz = models.CharField('Название (UZ)', max_length=200)
    title_az = models.CharField('Название (AZ)', max_length=200, blank=True)
    description_uz = models.TextField('Описание (UZ)', blank=True)
    description_az = models.TextField('Описание (AZ)', blank=True)
    video_url = models.URLField('URL Видео', blank=True)
    video_file = models.FileField('Видеофайл', upload_to='episodes/videos/', blank=True, null=True)
    duration = models.IntegerField('Длительность (мин)', blank=True, null=True)
    release_date = models.DateField('Дата выхода', blank=True, null=True)
    still_image = models.ImageField('Кадр', upload_to='episodes/', blank=True, null=True)

    class Meta:
        verbose_name = 'Эпизод'
        verbose_name_plural = 'Эпизоды'
        ordering = ['season', 'episode_number']
        unique_together = ['season', 'episode_number']

    @property
    def display_number(self):
        return self.episode_number + 1

    def __str__(self):
        return f"{(self.season.series.title_az or self.season.series.title_uz)} S{self.season.display_number}E{self.display_number}"


class Rating(models.Model):
    """Рейтинг фильма/сериала от пользователя."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings', verbose_name='Пользователь')
    content_type = models.CharField(max_length=20, choices=[('movie', 'Фильм'), ('series', 'Сериал')])
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings', blank=True, null=True)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='ratings', blank=True, null=True)
    score = models.IntegerField(
        'Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='От 1 до 5 звезд'
    )
    created_at = models.DateTimeField('Дата оценки', auto_now_add=True)

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'
        unique_together = ['user', 'content_type', 'movie', 'series']

    def __str__(self):
        content = self.movie if self.movie else self.series
        return f"{self.user.username} - {content} - {self.score}/5"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Обновление среднего рейтинга
        if self.movie:
            self.movie.update_rating()
        elif self.series:
            self.series.update_rating()


class Comment(MPTTModel):
    """Комментарии к фильмам/сериалам с поддержкой вложенности."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Пользователь')
    content_type = models.CharField(max_length=20, choices=[('movie', 'Фильм'), ('series', 'Сериал')])
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='comments', blank=True, null=True)

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительский комментарий'
    )

    text = models.TextField('Текст комментария')
    is_approved = models.BooleanField('Одобрен', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['-created_at']

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        content = self.movie if self.movie else self.series
        return f"{self.user.username} - {content}"


class StaticPage(models.Model):
    """Статические страницы сайта (О нас, Контакты и т.д.)"""
    ABOUT = 'about'
    CONTACTS = 'contacts'
    RULES = 'rules'
    PRIVACY = 'privacy'

    PAGE_TYPES = [
        (ABOUT, 'О нас'),
        (CONTACTS, 'Контакты'),
        (RULES, 'Правила'),
        (PRIVACY, 'Конфиденциальность'),
    ]

    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, unique=True, verbose_name='Тип страницы')
    title_uz = models.CharField(max_length=200, verbose_name='Заголовок (UZ)')
    title_az = models.CharField(max_length=200, verbose_name='Заголовок (AZ)', blank=True)
    content_uz = models.TextField(verbose_name='Содержание (UZ)')
    content_az = models.TextField(verbose_name='Содержание (AZ)', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Статическая страница'
        verbose_name_plural = 'Статические страницы'

    def __str__(self):
        return self.get_page_type_display()


class News(models.Model):
    """Новости кино."""
    title_uz = models.CharField('Заголовок (UZ)', max_length=300)
    title_az = models.CharField('Заголовок (AZ)', max_length=300, blank=True)
    slug = models.SlugField('URL', max_length=300, unique=True)

    content_uz = models.TextField('Содержание (UZ)')
    content_az = models.TextField('Содержание (AZ)', blank=True)

    image = models.ImageField('Изображение', upload_to='news/')
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(600, 400)],
        format='JPEG',
        options={'quality': 85}
    )

    related_movies = models.ManyToManyField(Movie, verbose_name='Связанные фильмы', blank=True)
    related_series = models.ManyToManyField(Series, verbose_name='Связанные сериалы', blank=True)

    is_published = models.BooleanField('Опубликовано', default=True)
    views = models.IntegerField('Просмотры', default=0)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self):
        return self.title_az or self.title_uz

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title_az or self.title_uz))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'slug': self.slug})

