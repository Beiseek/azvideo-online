from django.core.management.base import BaseCommand
from movies.models import StaticPage


class Command(BaseCommand):
    help = 'Create default static pages'

    def handle(self, *args, **kwargs):
        # О нас
        StaticPage.objects.get_or_create(
            page_type='about',
            defaults={
                'title_uz': 'Biz haqimizda',
                'content_uz': '''KinoSite - eng yaxshi filmlar va seriallar onlayn platformasi.

Biz sizga eng so'nggi kinolar, mashhur seriallar va dunyo kinematografiyasining klassik asarlarini taqdim etamiz.

Bizning missiyamiz:
- Yuqori sifatli kontent taqdim etish
- Qulay va zamonaviy interfeys
- Tezkor yangilanishlar

Bizga qo'shiling va kinoning ajoyib dunyosiga sho'ng'ing!''',
                'is_active': True
            }
        )
        
        # Контакты
        StaticPage.objects.get_or_create(
            page_type='contacts',
            defaults={
                'title_uz': 'Aloqa',
                'content_uz': '''Biz bilan bog'laning:

Email: info@kinosite.com
Telegram: @kinosite
WhatsApp: +998 90 123 45 67

Manzil: Toshkent, O'zbekiston

Ish vaqti: Dushanba-Yakshanba, 9:00-18:00

Sizning fikr-mulohazalaringiz biz uchun muhim!''',
                'is_active': True
            }
        )
        
        # Правила
        StaticPage.objects.get_or_create(
            page_type='rules',
            defaults={
                'title_uz': 'Qoidalar',
                'content_uz': '''Sayt foydalanish qoidalari:

1. Foydalanuvchilar mas\'uliyati
- Shaxsiy ma\'lumotlaringizni himoya qiling
- Noto'g'ri ma\'lumot tarqatmang
- Boshqa foydalanuvchilarga hurmat bilan munosabatda bo'ling

2. Taqiqlangan harakatlar
- Spam yuborish
- Haqoratli izohlar qoldirish
- Mualliflik huquqini buzish

3. Izohlar moderatsiyasi
- Barcha izohlar tekshiriladi
- Qoidalarni buzgan foydalanuvchilar bloklash mumkin

Qoidalarni buzganlar uchun jazo choralari qo'llanilishi mumkin.''',
                'is_active': True
            }
        )
        
        # Конфиденциальность
        StaticPage.objects.get_or_create(
            page_type='privacy',
            defaults={
                'title_uz': 'Maxfiylik siyosati',
                'content_uz': '''Maxfiylik siyosati:

1. Ma\'lumotlar yig'ish
- Email manzil
- Foydalanuvchi faoliyati
- Cookie-fayllari

2. Ma\'lumotlardan foydalanish
- Xizmat sifatini yaxshilash
- Shaxsiylashtirilgan tavsiyalar
- Statistika

3. Ma\'lumotlar xavfsizligi
- Barcha ma\'lumotlar shifrlangan
- Uchinchi shaxslarga berilmaydi
- Siz istalgan vaqtda ma\'lumotlaringizni o\'chirishingiz mumkin

4. Cookie-fayllar
- Sayt funksiyalarini ta\'minlash uchun
- Statistika uchun
- Reklama uchun (uchinchi tomon)

GDPR talablariga muvofiq.''',
                'is_active': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Static pages created successfully!'))

