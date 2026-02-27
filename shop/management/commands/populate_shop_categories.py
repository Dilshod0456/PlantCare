from django.core.management.base import BaseCommand
from shop.models import ProductCategory
from diagnosis.models import PlantType, AIModel
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Shop kategoriyalarini yaratish'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Uy o\'simliklari',
                'slug': 'uy-osimliklari',
                'description': 'Uyingiz ichida o\'sadigan chiroyli o\'simliklar',
                'icon': 'fas fa-home',
                'order': 1
            },
            {
                'name': 'Mevali daraxtlar',
                'slug': 'mevali-daraxtlar',
                'description': 'Bog\'ingiz uchun mevali daraxtlar',
                'icon': 'fas fa-apple-alt',
                'order': 2
            },
            {
                'name': 'Sabzavotlar',
                'slug': 'sabzavotlar',
                'description': 'Uy bog\'i uchun sabzavot o\'simliklari',
                'icon': 'fas fa-carrot',
                'order': 3
            },
            {
                'name': 'Gullar',
                'slug': 'gullar',
                'description': 'Chiroyli va xushbo\'y gullar',
                'icon': 'fas fa-flower',
                'order': 4
            },
            {
                'name': 'Dorivor o\'simliklar',
                'slug': 'dorivor-osimliklar',
                'description': 'Shifobaxsh dorivor o\'simliklar',
                'icon': 'fas fa-mortar-pestle',
                'order': 5
            },
            {
                'name': 'Kaktuslар',
                'slug': 'kaktuslar',
                'description': 'Parvarishlash oson kaktus o\'simliklari',
                'icon': 'fas fa-spa',
                'order': 6
            },
        ]

        created_count = 0
        for cat_data in categories:
            category, created = ProductCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name_uz': cat_data['name'],
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'display_order': cat_data['order'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Kategoriya yaratildi: {category.name_uz}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Kategoriya mavjud: {category.name_uz}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n📊 Jami {created_count} ta yangi kategoriya yaratildi')
        )
