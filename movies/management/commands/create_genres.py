from django.core.management.base import BaseCommand
from movies.models import Genre
from django.utils.text import slugify
from unidecode import unidecode

class Command(BaseCommand):
    help = 'Creates initial genres for movies and series'

    def handle(self, *args, **options):
        genres = [
            ('Action', 'Jangari'),
            ('Comedy', 'Komediya'),
            ('Drama', 'Drama'),
            ('Science Fiction', 'Fantastika'),
            ('Thriller', 'Triller'),
            ('Horror', 'Qoʻrqinchli'),
            ('Mystery', 'Detektiv'), # Mystery is often used on TMDB
            ('Detective', 'Detektiv'),
            ('Adventure', 'Sarguzasht'),
            ('Fantasy', 'Fantaziya'),
            ('Animation', 'Anime'), # TMDB uses Animation for Anime
            ('Family', 'Oilaviy'),
            ('History', 'Tarixiy'),
            ('War', 'Harbiy'),
            ('Crime', 'Jinoiy'),
            ('Romance', 'Melodrama'), # TMDB uses Romance for Melodrama
            ('Music', 'Musiqiy'),
            ('TV Movie', 'Telefilm'),
        ]

        for name_en, name_uz in genres:
            slug = slugify(unidecode(name_en))
            genre, created = Genre.objects.get_or_create(
                name=name_en,
                slug=slug,
                defaults={
                    'name_uz': name_uz,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created genre: {name_en} -> {unidecode(name_uz)}'))
            else:
                self.stdout.write(self.style.WARNING(f'Genre already exists: {name_en}'))

