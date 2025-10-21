"""
Service for working with TMDB API
"""
import requests
from django.conf import settings
import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

class TMDBService:
    """Сервис для работы с The Movie Database API."""
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.BASE_URL = 'https://api.themoviedb.org/3'

    def _make_request(self, endpoint, params=None):
        """Отправка запроса к API."""
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        try:
            response = requests.get(f"{self.BASE_URL}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Ошибка сети при запросе к {endpoint}: {e}")
            return None

    def search_movie(self, query, language='ru-RU'):
        """Поиск фильма по названию."""
        return self._make_request('search/movie', {'query': query, 'language': language})

    def search_series(self, query, language='ru-RU'):
        """Поиск сериала по названию."""
        return self._make_request('search/tv', {'query': query, 'language': language})

    def get_movie_details(self, tmdb_id, language='en-US'):
        """Получить детальную информацию о фильме."""
        params = {
            'language': language,
            'append_to_response': 'credits,videos,images,translations,keywords,similar'
        }
        return self._make_request(f'movie/{tmdb_id}', params)

    def get_series_details(self, tmdb_id, language='en-US'):
        """Получить детальную информацию о сериале."""
        params = {
            'language': language,
            'append_to_response': 'credits,videos,images,translations,keywords,similar'
        }
        return self._make_request(f'tv/{tmdb_id}', params)
    
    def get_season_details(self, tv_id, season_number, language='en-US'):
        """Получить детальную информацию о сезоне сериала."""
        params = {'language': language}
        return self._make_request(f'tv/{tv_id}/season/{season_number}', params)

    def get_movie_data_multilang(self, tmdb_id):
        """Получить данные о фильме на нескольких языках для форматирования."""
        try:
            # Базовые данные всегда на английском, т.к. они самые полные
            en_data = self.get_movie_details(tmdb_id, language='en-US')
            if not en_data:
                logger.error(f"Не удалось получить базовые данные (en-US) для TMDB ID {tmdb_id}")
                return None
            
            # Пытаемся получить азербайджанские данные, если они есть
            az_data = self.get_movie_details(tmdb_id, language='az-AZ')

            return {
                'en': en_data,
                'az': az_data or {}, # Возвращаем пустой dict если нет данных
            }
        except Exception as e:
            logger.error(f'Критическая ошибка в get_movie_data_multilang для TMDB ID {tmdb_id}: {e}')
            return None

    def get_series_data_multilang(self, tmdb_id):
        """Получить данные о сериале на нескольких языках для форматирования."""
        try:
            # Базовые данные всегда на английском
            en_data = self.get_series_details(tmdb_id, language='en-US')
            if not en_data:
                logger.error(f"Не удалось получить базовые данные (en-US) для сериала с TMDB ID {tmdb_id}")
                return None
            
            # Пытаемся получить азербайджанские данные
            az_data = self.get_series_details(tmdb_id, language='az-AZ')

            return {
                'en': en_data,
                'az': az_data or {},
            }
        except Exception as e:
            logger.error(f'Критическая ошибка в get_series_data_multilang для TMDB ID {tmdb_id}: {e}')
            return None

    def download_image(self, file_path):
        """Скачивает изображение с TMDB."""
        if not file_path:
            return None
        url = f'https://image.tmdb.org/t/p/original{file_path}'
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Ошибка скачивания изображения {url}: {e}")
            return None

    def _translate_text(self, text: str, target_language: str) -> str:
        """Переводит текст на указанный язык, используя Google Translate."""
        if not text or not target_language:
            return text
        try:
            # Инициализируем переводчик
            translator = GoogleTranslator(source='auto', target=target_language)
            # Переводим
            translated_text = translator.translate(text)
            logger.info(f"Перевод с 'en' на '{target_language}' успешeн.")
            return translated_text
        except Exception as e:
            logger.error(f"Ошибка перевода текста на язык '{target_language}': {e}")
            return text  # Возвращаем оригинал в случае ошибки

    def format_series_data(self, data: dict) -> dict | None:
        """Форматирует данные о сериале из TMDB."""
        if not data or not data.get('en'):
            return None

        base_data = data['en']
        
        # Названия
        title_en = base_data.get('name', '')
        title_az = self._translate_text(title_en, 'az')

        # Описания
        overview_en = base_data.get('overview', '')
        overview_az = self._translate_text(overview_en, 'az')

        # Трейлер
        trailer_url = ''
        if base_data.get('videos', {}).get('results'):
            for video in base_data['videos']['results']:
                if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                    trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
                    break

        # Актеры и режиссеры
        actors, directors = [], []
        if base_data.get('credits', {}).get('cast'):
            actors = [{'name': self._translate_text(p['name'], 'az')} for p in base_data['credits']['cast'][:15]]
        if base_data.get('credits', {}).get('crew'):
            directors = [self._translate_text(p['name'], 'az') for p in base_data['credits']['crew'] if p.get('job') == 'Director']

        release_date = base_data.get('first_air_date', '')
        
        genres_en = [g['name'] for g in base_data.get('genres', [])]
        countries_en = [c['name'] for c in base_data.get('production_countries', [])]
        countries_az = [self._translate_text(name, 'az') for name in countries_en]

        # --- Сезоны и эпизоды ---
        seasons_data = []
        if base_data.get('id') and 'seasons' in base_data:
            for season_summary in base_data['seasons']:
                season_number = season_summary.get('season_number')
                # Пропускаем "спецвыпуски" с нулевым номером
                if season_number is None or season_number == 0:
                    continue

                # Получаем детали сезона, включая эпизоды
                season_details_en = self.get_season_details(base_data['id'], season_number, language='en-US')
                if not season_details_en:
                    continue
                
                episodes = []
                for ep_data in season_details_en.get('episodes', []):
                    ep_name_en = ep_data.get('name', f'Episode {ep_data.get("episode_number")}')
                    ep_overview_en = ep_data.get('overview', '')
                    episodes.append({
                        'episode_number': ep_data.get('episode_number'),
                        'title_az': self._translate_text(ep_name_en, 'az'),
                        'description_az': self._translate_text(ep_overview_en, 'az'),
                        'duration': ep_data.get('runtime'),
                        'release_date': ep_data.get('air_date'),
                    })
                
                season_name_en = season_details_en.get('name', f'Season {season_number}')
                season_overview_en = season_details_en.get('overview', '')

                seasons_data.append({
                    'season_number': season_number,
                    'title_az': self._translate_text(season_name_en, 'az'),
                    'description_az': self._translate_text(season_overview_en, 'az'),
                    'poster_path': season_details_en.get('poster_path'),
                    'release_date': season_details_en.get('air_date'),
                    'episodes': episodes,
                })


        return {
            'title_az': title_az,
            'original_title': base_data.get('original_name', ''),
            'description_az': overview_az,
            'year': int(release_date.split('-')[0]) if release_date else None,
            'seasons_count': base_data.get('number_of_seasons', 0),
            'status': base_data.get('status', ''),
            'genres': genres_en,
            'countries': countries_az,
            'actors': actors,
            'directors': directors,
            'poster_path': base_data.get('poster_path', ''),
            'backdrop_path': base_data.get('backdrop_path', ''),
            'imdb_rating': base_data.get('vote_average', 0),
            'trailer_url': trailer_url,
            'seasons': seasons_data,
        }

    def format_movie_data(self, data: dict) -> dict | None:
        """
        Форматирует мульти-языковые данные о фильме, полученные из TMDB.
        Принимает на вход словарь вида {'en': {...}, 'az': {...}}.
        """
        if not data or not isinstance(data, dict) or not data.get('en'):
            logger.error("format_movie_data: получены некорректные данные. Ожидался словарь с ключом 'en'.")
            return None
        
        base_data = data['en']
        
        # --- Названия ---
        title_en = base_data.get('title', '')
        title_az = ''
        if base_data.get('translations', {}).get('translations'):
            for trans in base_data['translations']['translations']:
                if trans.get('iso_639_1') == 'az':
                    title_az = trans.get('data', {}).get('title', '')
                    break
        if not title_az and title_en:
            title_az = self._translate_text(title_en, 'az')

        # --- Описания ---
        overview_en = base_data.get('overview', '')
        overview_az = ''
        if base_data.get('translations', {}).get('translations'):
            for trans in base_data['translations']['translations']:
                if trans.get('iso_639_1') == 'az':
                    overview_az = trans.get('data', {}).get('overview', '')
                    break
        if not overview_az and overview_en:
            overview_az = self._translate_text(overview_en, 'az')
        
        # --- Трейлер ---
        trailer_url = ''
        if base_data.get('videos', {}).get('results'):
            for video in base_data['videos']['results']:
                if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                    trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
                    break
        
        # --- Режиссеры и Актеры (с переводом) ---
        actors, directors = [], []
        if base_data.get('credits', {}).get('cast'):
            actors = [{'name': self._translate_text(person['name'], 'az')} for person in base_data['credits']['cast'][:15]]
        if base_data.get('credits', {}).get('crew'):
            for person in base_data['credits']['crew']:
                if person.get('job') == 'Director':
                    directors.append(self._translate_text(person['name'], 'az'))

        release_date = base_data.get('release_date', '')

        # --- Жанры и Страны (с переводом) ---
        genres_en = [genre['name'] for genre in base_data.get('genres', [])]
        
        countries_en = [country['name'] for country in base_data.get('production_countries', [])]
        countries_az = [self._translate_text(name, 'az') for name in countries_en]

        return {
            'title_az': title_az or title_en,
            'original_title': base_data.get('original_title', ''),
            'description_az': overview_az or overview_en,
            'year': int(release_date.split('-')[0]) if release_date else None,
            'duration': base_data.get('runtime', 0),
            'genres': genres_en, # Pass English names
            'countries': countries_az,
            'actors': actors,
            'directors': directors,
            'poster_path': base_data.get('poster_path', ''),
            'backdrop_path': base_data.get('backdrop_path', ''),
            'imdb_rating': base_data.get('vote_average', 0),
            'trailer_url': trailer_url,
        }

