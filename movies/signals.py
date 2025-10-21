"""
Сигналы для автоматического заполнения данных фильмов из TMDB
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movie, Genre, Country, Person
from .tmdb_service import TMDBService
from django.core.files.base import ContentFile
from django.utils.text import slugify
from unidecode import unidecode
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Movie)
def auto_fill_movie_from_tmdb(sender, instance, created, **kwargs):
    if not created or not instance.tmdb_id or hasattr(instance, '_tmdb_fill_completed'):
        return

    logger.info(f"СИГНАЛ: Запуск автозаполнения для '{instance.title_uz}' (TMDB ID: {instance.tmdb_id})")

    service = TMDBService()
    try:
        movie_data = service.get_movie_data_multilang(instance.tmdb_id)
        formatted = service.format_movie_data(movie_data)

        if not formatted:
            logger.error(f"СИГНАЛ: Не удалось получить/отформатировать данные из TMDB для ID {instance.tmdb_id}.")
            return

        # 1. ЗАПОЛНЯЕМ И СОХРАНЯЕМ ОСНОВНЫЕ ПОЛЯ И КАРТИНКИ
        instance.title_uz = formatted.get('title_uz', '')
        instance.title_az = formatted.get('title_az', '')
        instance.original_title = formatted.get('original_title', '')
        instance.description_uz = formatted.get('description_uz', '')
        instance.description_az = formatted.get('description_az', '')
        instance.year = formatted.get('year')
        instance.duration = formatted.get('duration', 0)
        # В модели у нас rating_avg, а TMDB возвращает vote_average, который по 10-балльной шкале. Приведем к 5-балльной
        instance.rating_avg = round(formatted.get('imdb_rating', 0) / 2, 1)
        instance.trailer_url = formatted.get('trailer_url', '')
        if not instance.slug:
            instance.slug = slugify(unidecode(instance.title_uz or instance.original_title))
        
        if formatted.get('poster_path'):
            poster_content = service.download_image(formatted['poster_path'])
            if poster_content:
                instance.poster.save(f"poster_{instance.tmdb_id}.jpg", ContentFile(poster_content), save=False)
        
        if formatted.get('backdrop_path'):
            backdrop_content = service.download_image(formatted['backdrop_path'])
            if backdrop_content:
                instance.backdrop.save(f"backdrop_{instance.tmdb_id}.jpg", ContentFile(backdrop_content), save=False)
        
        # Отключаем сигнал, чтобы избежать рекурсии при сохранении
        post_save.disconnect(auto_fill_movie_from_tmdb, sender=Movie)
        instance.save()
        post_save.connect(auto_fill_movie_from_tmdb, sender=Movie)
        
        logger.info(f"СИГНАЛ: Основные поля и изображения для ID {instance.id} сохранены.")

        # 2. СОЗДАЕМ И ПРИВЯЗЫВАЕМ M2M СВЯЗИ (ПОСЛЕ ОСНОВНОГО СОХРАНЕНИЯ)
        # Жанры
        genre_names = formatted.get('genres', [])
        genres_to_set = []
        for name in genre_names:
            genre, _ = Genre.objects.get_or_create(name_uz=name, defaults={'name_az': name, 'slug': slugify(unidecode(name))})
            genres_to_set.append(genre)
        if genres_to_set:
            instance.genres.set(genres_to_set)
            logger.info(f"СИГНАЛ: Привязано {len(genres_to_set)} жанров.")

        # Страны
        country_names = formatted.get('countries', [])
        countries_to_set = []
        for name in country_names:
            code = ''.join(filter(str.isalpha, unidecode(name)))[:3].upper()
            country, _ = Country.objects.get_or_create(name_uz=name, defaults={'name_az': name, 'code': code})
            countries_to_set.append(country)
        if countries_to_set:
            instance.countries.set(countries_to_set)
            logger.info(f"СИГНАЛ: Привязано {len(countries_to_set)} стран.")

        # Актеры
        actors_data = formatted.get('actors', [])
        actors_to_set = []
        for actor in actors_data:
            name = actor.get('name')
            if name:
                person, _ = Person.objects.get_or_create(name=name, defaults={'role': Person.Role.ACTOR})
                actors_to_set.append(person)
        if actors_to_set:
            instance.actors.set(actors_to_set)
            logger.info(f"СИГНАЛ: Привязано {len(actors_to_set)} актеров.")
        
        # Режиссеры
        director_names = formatted.get('directors', [])
        directors_to_set = []
        for name in director_names:
            person, _ = Person.objects.get_or_create(name=name, defaults={'role': Person.Role.DIRECTOR})
            directors_to_set.append(person)
        if directors_to_set:
            instance.directors.set(directors_to_set)
            logger.info(f"СИГНАЛ: Привязано {len(directors_to_set)} режиссеров.")

        # Помечаем, что обработка завершена
        instance._tmdb_fill_completed = True
        logger.info(f"СИГНАЛ: Автозаполнение для фильма ID: {instance.id} полностью завершено.")

    except Exception as e:
        logger.error(f"СИГНАЛ: КРИТИЧЕСКАЯ ОШИБКА при автозаполнении фильма ID {instance.id}: {e}", exc_info=True)

