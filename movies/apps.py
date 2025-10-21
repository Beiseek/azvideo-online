from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'
    
    # def ready(self):
    #     import movies.signals  # Подключаем сигналы (ОТКЛЮЧЕНО)
    verbose_name = 'Фильмы и Сериалы'

