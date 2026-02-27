"""
O'simlik turlarini bazaga qo'shuvchi management buyrug'i
"""

from django.core.management.base import BaseCommand
from diagnosis.models import PlantType


class Command(BaseCommand):
    help = "Class indices.json asosida o'simlik turlarini bazaga qo'shadi"

    def handle(self, *args, **options):
        plants_data = [
            {
                'code': 'apple',
                'name_uz': 'Olma',
                'name_en': 'Apple',
                'name_ru': 'Яблоко',
                'scientific_name': 'Malus domestica',
                'category': 'Meva'
            },
            {
                'code': 'blueberry',
                'name_uz': 'Ko\'k gilos',
                'name_en': 'Blueberry',
                'name_ru': 'Черника',
                'scientific_name': 'Vaccinium corymbosum',
                'category': 'Meva'
            },
            {
                'code': 'cherry',
                'name_uz': 'Olcha',
                'name_en': 'Cherry',
                'name_ru': 'Вишня',
                'scientific_name': 'Prunus avium',
                'category': 'Meva'
            },
            {
                'code': 'corn',
                'name_uz': 'Makkajo\'xori',
                'name_en': 'Corn (Maize)',
                'name_ru': 'Кукуруза',
                'scientific_name': 'Zea mays',
                'category': 'Don'
            },
            {
                'code': 'grape',
                'name_uz': 'Uzum',
                'name_en': 'Grape',
                'name_ru': 'Виноград',
                'scientific_name': 'Vitis vinifera',
                'category': 'Meva'
            },
            {
                'code': 'orange',
                'name_uz': 'Apelsin',
                'name_en': 'Orange',
                'name_ru': 'Апельсин',
                'scientific_name': 'Citrus sinensis',
                'category': 'Meva'
            },
            {
                'code': 'peach',
                'name_uz': 'Shaftoli',
                'name_en': 'Peach',
                'name_ru': 'Персик',
                'scientific_name': 'Prunus persica',
                'category': 'Meva'
            },
            {
                'code': 'pepper',
                'name_uz': 'Qalampir',
                'name_en': 'Bell Pepper',
                'name_ru': 'Перец',
                'scientific_name': 'Capsicum annuum',
                'category': 'Sabzavot'
            },
            {
                'code': 'potato',
                'name_uz': 'Kartoshka',
                'name_en': 'Potato',
                'name_ru': 'Картофель',
                'scientific_name': 'Solanum tuberosum',
                'category': 'Sabzavot'
            },
            {
                'code': 'raspberry',
                'name_uz': 'Malina',
                'name_en': 'Raspberry',
                'name_ru': 'Малина',
                'scientific_name': 'Rubus idaeus',
                'category': 'Meva'
            },
            {
                'code': 'soybean',
                'name_uz': 'Soya',
                'name_en': 'Soybean',
                'name_ru': 'Соя',
                'scientific_name': 'Glycine max',
                'category': 'Dukkakli'
            },
            {
                'code': 'squash',
                'name_uz': 'Qovoq',
                'name_en': 'Squash',
                'name_ru': 'Тыква',
                'scientific_name': 'Cucurbita pepo',
                'category': 'Sabzavot'
            },
            {
                'code': 'strawberry',
                'name_uz': 'Qulupnay',
                'name_en': 'Strawberry',
                'name_ru': 'Клубника',
                'scientific_name': 'Fragaria × ananassa',
                'category': 'Meva'
            },
            {
                'code': 'tomato',
                'name_uz': 'Pomidor',
                'name_en': 'Tomato',
                'name_ru': 'Помидор',
                'scientific_name': 'Solanum lycopersicum',
                'category': 'Sabzavot'
            },
            {
                'code': 'all',
                'name_uz': 'Barcha o\'simliklar',
                'name_en': 'All Plants',
                'name_ru': 'Все растения',
                'scientific_name': '',
                'category': 'Umumiy'
            }
        ]

        created_count = 0
        updated_count = 0

        for plant_data in plants_data:
            plant, created = PlantType.objects.update_or_create(
                code=plant_data['code'],
                defaults={
                    'name_uz': plant_data['name_uz'],
                    'name_en': plant_data['name_en'],
                    'name_ru': plant_data['name_ru'],
                    'scientific_name': plant_data['scientific_name'],
                    'category': plant_data['category'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Yaratildi: {plant.name_uz} ({plant.code})')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Yangilandi: {plant.name_uz} ({plant.code})')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Tayyor! {created_count} ta yangi, {updated_count} ta yangilandi.'
            )
        )
