"""
Custom admin panel for movies app.
"""
from django.contrib import admin
from django.utils.html import format_html
import nested_admin
from .models import (
    Genre, Country, Person, Movie, Series, Season, Episode,
    Rating, Comment, News, StaticPage
)
from .admin_forms import TMDBMovieForm, TMDBSeriesForm, EpisodeForm, SeasonForm
from django.contrib import messages
from django.utils.text import slugify
from django.core.files.base import ContentFile
from unidecode import unidecode
from .tmdb_service import TMDBService
import logging

logger = logging.getLogger(__name__)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_az', 'name_uz', 'slug']
    search_fields = ['name', 'name_az', 'name_uz']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name_az', 'name_uz', 'code']
    search_fields = ['name_az', 'name_uz', 'code']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'photo_preview', 'tmdb_id']
    list_filter = ['role']
    search_fields = ['name']
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="75" />', obj.photo.url)
        return '-'
    photo_preview.short_description = 'Фото'


class EpisodeInline(nested_admin.NestedTabularInline):
    model = Episode
    form = EpisodeForm
    extra = 1
    fields = ['episode_number', 'title_az', 'title_uz', 'duration', 'video_url', 'video_file', 'release_date']
    sortable_field_name = "episode_number"


class SeasonInline(nested_admin.NestedTabularInline):
    model = Season
    form = SeasonForm
    extra = 1
    fields = ['season_number', 'title_az', 'title_uz', 'release_date']
    inlines = [EpisodeInline]
    sortable_field_name = "season_number"


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    form = TMDBMovieForm
    list_display = ('title_az', 'title_uz', 'year', 'rating_avg', 'views', 'is_published')
    list_filter = ('genres', 'countries', 'year', 'is_published')
    search_fields = ('title_az', 'title_uz', 'original_title')
    filter_horizontal = ('genres', 'countries', 'directors', 'actors')
    actions = ['fill_from_tmdb_action']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title_az', 'title_uz', 'original_title', 'slug', 'tmdb_id')
        }),
        ('Описание', {
            'fields': ('description_az', 'description_uz')
        }),
        ('Медиа', {
            'fields': ('poster', 'backdrop', 'trailer_url', 'video_file')
        }),
        ('Данные', {
            'fields': ('year', 'duration', 'rating_avg')
        }),
        ('Связи', {
            'fields': ('genres', 'countries', 'directors', 'actors')
        }),
        ('Настройки публикации', {
            'fields': ('is_published',)
        }),
    )
    
    def poster_preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="50" height="75" />', obj.poster.url)
        return '-'
    poster_preview.short_description = 'Постер'
    
    def poster_preview_large(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="200" height="300" />', obj.poster.url)
        return '-'
    poster_preview_large.short_description = 'Предпросмотр постера'
    
    def rating_display(self, obj):
        return f"{obj.rating_avg} ({obj.rating_count})"
    rating_display.short_description = 'Рейтинг'

    @admin.action(description='Заполнить данные из TMDB')
    def fill_from_tmdb_action(self, request, queryset):
        """
        Admin action для заполнения выбранных фильмов данными из TMDB.
        """
        updated_count = 0
        error_count = 0
        service = TMDBService()

        for movie in queryset:
            tmdb_id = movie.tmdb_id
            # Если TMDB ID не указан, пытаемся найти по названию
            if not tmdb_id and movie.original_title:
                search_results = service.search_movie(movie.original_title, language='en-US')
                if search_results and search_results.get('results'):
                    tmdb_id = search_results['results'][0]['id']
                    movie.tmdb_id = tmdb_id  # Сохраняем найденный ID
                    self.message_user(request, f"Найден TMDB ID ({tmdb_id}) для '{movie.original_title}' по названию.", messages.INFO)
                else:
                    self.message_user(request, f"Не удалось найти фильм '{movie.original_title}' в TMDB по названию.", messages.WARNING)
                    error_count += 1
                    continue

            if not tmdb_id:
                self.message_user(request, f"У фильма '{movie.title_uz or movie.original_title}' не указан ни TMDB ID, ни оригинальное название для поиска.", messages.WARNING)
                error_count += 1
                continue

            try:
                movie_data = service.get_movie_data_multilang(tmdb_id)
                formatted = service.format_movie_data(movie_data)

                if not formatted:
                    self.message_user(request, f"Не удалось получить данные из TMDB для '{movie.title_uz}' (TMDB ID: {tmdb_id}).", messages.ERROR)
                    error_count += 1
                    continue

                # --- Заполняем поля ---
                movie.title_az = formatted.get('title_az', movie.title_az)
                # ... (заполняем остальные поля, как в management command)
                movie.original_title = formatted.get('original_title', '')
                movie.description_az = formatted.get('description_az', '')
                movie.year = formatted.get('year')
                movie.duration = formatted.get('duration', 0)
                movie.rating_avg = round(formatted.get('imdb_rating', 0) / 2, 1)
                movie.trailer_url = formatted.get('trailer_url', '')
                if not movie.slug:
                    movie.slug = slugify(unidecode(movie.title_az or movie.title_uz or movie.original_title))
                
                # --- Изображения ---
                if formatted.get('poster_path'):
                    poster_content = service.download_image(formatted['poster_path'])
                    if poster_content:
                        movie.poster.save(f"poster_{movie.tmdb_id}.jpg", ContentFile(poster_content), save=False)
                
                if formatted.get('backdrop_path'):
                    backdrop_content = service.download_image(formatted['backdrop_path'])
                    if backdrop_content:
                        movie.backdrop.save(f"backdrop_{movie.tmdb_id}.jpg", ContentFile(backdrop_content), save=False)
                
                movie.save() # Сохраняем основные поля

                # --- M2M Связи ---
                # Жанры
                genre_names = formatted.get('genres', [])
                genres_to_set = []
                for name in genre_names: # These are English names from TMDB
                    genre, created = Genre.objects.get_or_create(
                        name=name,
                        defaults={'name_az': service._translate_text(name, 'az')}
                    )
                    if created:
                        logger.info(f"Created new genre: '{name}' with Azerbaijani translation '{genre.name_az}'")
                    genres_to_set.append(genre)
                if genres_to_set: movie.genres.set(genres_to_set)

                # Страны
                country_names = formatted.get('countries', [])
                countries_to_set = []
                for name in country_names:
                    code = ''.join(filter(str.isalpha, unidecode(name)))[:3].upper()
                    country, _ = Country.objects.get_or_create(code=code, defaults={'name_az': name})
                    countries_to_set.append(country)
                if countries_to_set: movie.countries.set(countries_to_set)

                # Актеры
                actors_data = formatted.get('actors', [])
                actors_to_set = []
                for actor_data in actors_data:
                    name = actor_data.get('name')
                    if name:
                        person, _ = Person.objects.get_or_create(name=name, defaults={'role': 'actor'})
                        actors_to_set.append(person)
                if actors_to_set: movie.actors.set(actors_to_set)

                # Режиссеры
                director_names = formatted.get('directors', [])
                directors_to_set = []
                for name in director_names:
                    person, _ = Person.objects.get_or_create(name=name, defaults={'role': 'director'})
                    directors_to_set.append(person)
                if directors_to_set: movie.directors.set(directors_to_set)
                
                updated_count += 1

            except Exception as e:
                self.message_user(request, f"Ошибка при обновлении '{movie.title_uz}': {e}", messages.ERROR)
                error_count += 1

        if updated_count > 0:
            self.message_user(request, f"Успешно обновлено {updated_count} фильмов.", messages.SUCCESS)
        if error_count > 0:
            self.message_user(request, f"Не удалось обновить {error_count} фильмов.", messages.ERROR)


@admin.register(Series)
class SeriesAdmin(nested_admin.NestedModelAdmin):
    form = TMDBSeriesForm
    list_display = [
        'title_az', 'title_uz', 'year', 'seasons_count', 'status', 'poster_preview', 'rating_display', 'views', 'is_featured', 'is_published'
    ]
    list_filter = ['status', 'is_featured', 'is_published', 'year', 'genres']
    search_fields = ['title_az', 'title_uz', 'original_title']
    prepopulated_fields = {'slug': ('title_az', 'title_uz')}
    filter_horizontal = ['genres', 'countries', 'directors', 'actors']
    readonly_fields = ['rating_avg', 'rating_count', 'views', 'created_at', 'updated_at', 'poster_preview_large']
    inlines = [SeasonInline]
    actions = ['fill_from_tmdb_action']
    
    fieldsets = [
        ('Основная информация', {
            'fields': [
                'title_az', 'title_uz', 'original_title', 'slug', 'content_type', 'year', 'seasons_count', 'status',
            ]
        }),
        ('Описание', {
            'fields': ['description_az', 'description_uz']
        }),
        ('Медиа', {
            'fields': [
                'poster', 'poster_preview_large', 'backdrop', 'trailer_url',
            ]
        }),
        ('Связи', {
            'fields': ['genres', 'countries', 'directors', 'actors']
        }),
        ('Статистика', {
            'fields': ['rating_avg', 'rating_count', 'views']
        }),
        ('Настройки публикации', {
            'fields': ['is_featured', 'is_published']
        }),
        ('Даты', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def poster_preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="50" height="75" />', obj.poster.url)
        return '-'
    poster_preview.short_description = 'Постер'
    
    def poster_preview_large(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="200" height="300" />', obj.poster.url)
        return '-'
    poster_preview_large.short_description = 'Предпросмотр постера'
    
    def rating_display(self, obj):
        return f"{obj.rating_avg} ({obj.rating_count})"
    rating_display.short_description = 'Рейтинг'

    @admin.action(description='Заполнить данные из TMDB для сериалов')
    def fill_from_tmdb_action(self, request, queryset):
        updated_count = 0
        error_count = 0
        service = TMDBService()

        for series in queryset:
            tmdb_id = series.tmdb_id
            if not tmdb_id and series.original_title:
                search_results = service.search_series(series.original_title, language='en-US')
                if search_results and search_results.get('results'):
                    tmdb_id = search_results['results'][0]['id']
                    series.tmdb_id = tmdb_id
                    self.message_user(request, f"Найден TMDB ID ({tmdb_id}) для '{series.original_title}' по названию.", messages.INFO)
                else:
                    self.message_user(request, f"Не удалось найти сериал '{series.original_title}' в TMDB.", messages.WARNING)
                    error_count += 1
                    continue
            
            if not tmdb_id:
                self.message_user(request, f"У сериала '{series.title_uz or series.original_title}' не указан TMDB ID или оригинальное название.", messages.WARNING)
                error_count += 1
                continue

            try:
                series_data = service.get_series_data_multilang(tmdb_id)
                formatted = service.format_series_data(series_data)

                if not formatted:
                    self.message_user(request, f"Не удалось получить данные из TMDB для '{series.title_uz}' (ID: {tmdb_id}).", messages.ERROR)
                    error_count += 1
                    continue
                
                series.title_az = formatted.get('title_az', series.title_az)
                series.original_title = formatted.get('original_title', series.original_title)
                series.description_az = formatted.get('description_az', series.description_az)
                series.year = formatted.get('year', series.year)
                series.seasons_count = formatted.get('seasons_count', series.seasons_count)
                series.status = formatted.get('status', series.status)
                series.rating_avg = round(formatted.get('imdb_rating', 0) / 2, 1)
                series.trailer_url = formatted.get('trailer_url', series.trailer_url)
                if not series.slug:
                    series.slug = slugify(unidecode(series.title_az or series.title_uz or series.original_title))
                
                if formatted.get('poster_path'):
                    content = service.download_image(formatted['poster_path'])
                    if content: series.poster.save(f"poster_{tmdb_id}.jpg", ContentFile(content), save=False)
                
                if formatted.get('backdrop_path'):
                    content = service.download_image(formatted['backdrop_path'])
                    if content: series.backdrop.save(f"backdrop_{tmdb_id}.jpg", ContentFile(content), save=False)

                series.save()

                # Связи M2M
                genre_names = formatted.get('genres', [])
                genres_to_set = []
                for name in genre_names:
                    genre, _ = Genre.objects.get_or_create(name=name, defaults={'name_az': service._translate_text(name, 'az')})
                    genres_to_set.append(genre)
                if genres_to_set: series.genres.set(genres_to_set)
                
                country_names = formatted.get('countries', [])
                countries_to_set = []
                for name in country_names:
                    code = ''.join(filter(str.isalpha, unidecode(name)))[:3].upper()
                    country, _ = Country.objects.get_or_create(code=code, defaults={'name_az': name})
                    countries_to_set.append(country)
                if countries_to_set: series.countries.set(countries_to_set)

                actors_data = formatted.get('actors', [])
                actors_to_set = []
                for actor_data in actors_data:
                    if name := actor_data.get('name'):
                        person, _ = Person.objects.get_or_create(name=name, defaults={'role': 'actor'})
                        actors_to_set.append(person)
                if actors_to_set: series.actors.set(actors_to_set)

                director_names = formatted.get('directors', [])
                directors_to_set = []
                for name in director_names:
                    person, _ = Person.objects.get_or_create(name=name, defaults={'role': 'director'})
                    directors_to_set.append(person)
                if directors_to_set: series.directors.set(directors_to_set)

                # --- Создание сезонов и эпизодов ---
                seasons_data = formatted.get('seasons', [])
                for season_data in seasons_data:
                    # Пропускаем "спецвыпуски" с нулевым номером, если они есть
                    if season_data['season_number'] < 1:
                        continue
                    
                    season, created = Season.objects.update_or_create(
                        series=series,
                        season_number=season_data['season_number'] - 1,  # Сохраняем как 0-based
                        defaults={
                            'title_az': season_data.get('title_az', ''),
                            'description_az': season_data.get('description_az', ''),
                            'release_date': season_data.get('release_date') or None,
                        }
                    )
                    if created:
                        self.message_user(request, f"Создан Сезон {season.season_number} для '{series.title_uz}'", messages.SUCCESS)
                    
                    if season_data.get('poster_path'):
                        content = service.download_image(season_data['poster_path'])
                        if content: season.poster.save(f"s{season.season_number}_poster_{tmdb_id}.jpg", ContentFile(content), save=True)

                    for episode_data in season_data.get('episodes', []):
                        Episode.objects.update_or_create(
                            season=season,
                            episode_number=episode_data['episode_number'] - 1,  # Сохраняем как 0-based
                            defaults={
                                'title_az': episode_data.get('title_az', ''),
                                'description_az': episode_data.get('description_az', ''),
                                'duration': episode_data.get('duration'),
                                'release_date': episode_data.get('release_date') or None,
                            }
                        )

                updated_count += 1
            except Exception as e:
                self.message_user(request, f"Ошибка при обновлении '{series.title_uz}': {e}", messages.ERROR)
                error_count += 1
        
        if updated_count > 0:
            self.message_user(request, f"Успешно обновлено {updated_count} сериалов.", messages.SUCCESS)
        if error_count > 0:
            self.message_user(request, f"Не удалось обновить {error_count} сериалов.", messages.ERROR)


@admin.register(Season)
class SeasonAdmin(nested_admin.NestedModelAdmin):
    form = SeasonForm
    list_display = ['__str__', 'season_number', 'release_date']
    list_filter = ['series']
    search_fields = ['series__title_uz', 'title_uz']
    inlines = [EpisodeInline]


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    form = EpisodeForm
    list_display = ['__str__', 'episode_number', 'duration', 'release_date']
    list_filter = ['season__series']
    search_fields = ['title_uz']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_display', 'score', 'created_at']
    list_filter = ['content_type', 'score', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    
    def content_display(self, obj):
        return obj.movie if obj.movie else obj.series
    content_display.short_description = 'Контент'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_display', 'text_preview', 'is_approved', 'created_at']
    list_filter = ['content_type', 'is_approved', 'created_at']
    search_fields = ['user__username', 'text']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_comments', 'disapprove_comments']
    
    def content_display(self, obj):
        return obj.movie if obj.movie else obj.series
    content_display.short_description = 'Контент'
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = 'Одобрить выбранные комментарии'
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_comments.short_description = 'Отклонить выбранные комментарии'


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title_az', 'title_uz', 'image_preview', 'views', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title_az', 'title_uz']
    prepopulated_fields = {'slug': ('title_az', 'title_uz')}
    filter_horizontal = ['related_movies', 'related_series']
    readonly_fields = ['views', 'created_at', 'updated_at', 'image_preview_large']
    
    fieldsets = [
        ('Основная информация', {
            'fields': ['title_az', 'title_uz', 'slug']
        }),
        ('Содержание', {
            'fields': ['content_az', 'content_uz']
        }),
        ('Медиа', {
            'fields': ['image', 'image_preview_large']
        }),
        ('Связи', {
            'fields': ['related_movies', 'related_series']
        }),
        ('Статистика и настройки', {
            'fields': ['views', 'is_published', 'created_at', 'updated_at']
        }),
    ]
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="67" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Изображение'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="600" height="400" />', obj.image.url)
        return '-'
    image_preview_large.short_description = 'Предпросмотр изображения'


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ['page_type', 'title_uz', 'is_active', 'updated_at']
    list_filter = ['page_type', 'is_active']
    search_fields = ['title_uz', 'content_uz']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Основное', {
            'fields': ['page_type', 'is_active']
        }),
        ('Контент', {
            'fields': ['title_uz', 'content_uz']
        }),
        ('Информация', {
            'fields': ['created_at', 'updated_at']
        }),
    ]

