from django.core.management.base import BaseCommand
from movies.models import Genre, Country, Person, Movie, Series, Season, Episode, StaticPage, News
from deep_translator import GoogleTranslator
import time

class Command(BaseCommand):
    help = 'Translate existing database fields from Uzbek to Azerbaijani'

    def _translate_text(self, text: str) -> str:
        """Translates text to Azerbaijani, returns original on error."""
        if not text:
            return ""
        try:
            # Adding a small delay to avoid hitting API rate limits
            time.sleep(0.1)
            return GoogleTranslator(source='uz', target='az').translate(text)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error translating '{text[:30]}...': {e}"))
            return text

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting translation of database content to Azerbaijani...'))

        models_and_fields = {
            Genre: {'name_uz': 'name_az'},
            Country: {'name_uz': 'name_az'},
            Person: {'bio_uz': 'bio_az'},
            Movie: {'title_uz': 'title_az', 'description_uz': 'description_az'},
            Series: {'title_uz': 'title_az', 'description_uz': 'description_az'},
            Season: {'title_uz': 'title_az', 'description_uz': 'description_az'},
            Episode: {'title_uz': 'title_az', 'description_uz': 'description_az'},
            StaticPage: {'title_uz': 'title_az', 'content_uz': 'content_az'},
            News: {'title_uz': 'title_az', 'content_uz': 'content_az'},
        }

        for model, fields in models_and_fields.items():
            self.stdout.write(f'Translating {model.__name__} objects...')
            updated_count = 0
            for item in model.objects.all():
                item_updated = False
                for source_field, target_field in fields.items():
                    source_text = getattr(item, source_field)
                    if source_text:
                        translated_text = self._translate_text(source_text)
                        setattr(item, target_field, translated_text)
                        item_updated = True
                
                if item_updated:
                    item.save()
                    updated_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Translated and updated {updated_count} {model.__name__} objects.'))

        self.stdout.write(self.style.SUCCESS('Database translation process finished.'))
