from django.core.management.base import BaseCommand
from movies.models import Movie, Series, Season, Episode, Rating, Comment, News

class Command(BaseCommand):
    help = 'Safely clears content data (movies, series, seasons, episodes, ratings, comments, news) without touching users, genres, or countries.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting content cleanup...'))

        # Delete child objects first to respect FK constraints
        deleted_counts = {}
        for model in [Rating, Comment, Episode, Season, News, Movie, Series]:
            count = model.objects.all().count()
            model.objects.all().delete()
            deleted_counts[model.__name__] = count

        for model_name, count in deleted_counts.items():
            self.stdout.write(self.style.SUCCESS(f'Deleted {count} {model_name} objects'))

        self.stdout.write(self.style.SUCCESS('Content cleanup finished successfully.'))
