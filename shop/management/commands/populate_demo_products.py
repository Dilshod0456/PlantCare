from django.core.management.base import BaseCommand
from shop.models import ProductCategory, Product
from diagnosis.models import PlantType
from django.utils.text import slugify
import random


class Command(BaseCommand):
    help = 'Demo mahsulotlar yaratish'

    def handle(self, *args, **options):
        # Get categories
        try:
            uy_kategory = ProductCategory.objects.get(slug='uy-osimliklari')
            meva_kategory = ProductCategory.objects.get(slug='mevali-daraxtlar')
            sabza_kategory = ProductCategory.objects.get(slug='sabzavotlar')
        except ProductCategory.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Kategoriyalar topilmadi. Avval populate_shop_categories ni ishga tushiring')
            )
            return

        # Get plant types
        plant_types = list(PlantType.objects.all())
        if not plant_types:
            self.stdout.write(
                self.style.WARNING('O\'simlik turlari topilmadi')
            )
            plant_type = None
        else:
            plant_type = random.choice(plant_types)

        products = [
            {
                'name': 'Olma ko\'chati - Golden Delicious',
                'slug': 'olma-kochati-golden',
                'category': meva_kategory,
                'plant_type': plant_type,
                'short_description': 'Yuqori sifatli olma ko\'chati. Tez o\'sadi va ko\'p hosil beradi.',
                'description': '''Golden Delicious olma turi - eng mashhur va mazali olma turlaridan biri. Ko'chat 2-3 yildan keyin meva berishni boshlaydi. Yuqori sifatli, shirinroq va sog'lom mevalar beradi. Parvarishi oson, sovuqqa chidamli.

Parvarish qilish bo'yicha ko'rsatmalar:
1. Haftada 2-3 marta sug'oring
2. Bahorda o'g'it bering
3. Kasalliklardan himoya qiling
4. Muntazam qirqish kerak''',
                'price': 45000,
                'original_price': 60000,
                'stock_quantity': 25,
                'is_featured': True,
                'is_available': True,
                'light_requirement': 'To\'liq quyosh',
                'water_requirement': 'O\'rtacha',
                'temperature_range': '-5°C dan +30°C gacha',
                'care_level': 'easy',
                'condition': 'growing',
                'height': '50-70 sm',
                'age': '1 yil',
            },
            {
                'name': 'Pomidor ko\'chati - San Marzano',
                'slug': 'pomidor-kochati-san-marzano',
                'category': sabza_kategory,
                'plant_type': plant_type,
                'short_description': 'Italyan San Marzano pomidor ko\'chati. Pishloq tayyorlash uchun ideal.',
                'description': '''San Marzano - dunyodagi eng zo'r pomidor turlaridan biri. Uzun va go'zal shaklga ega. Pishloq tayyorlash, salat va boshqa taomlar uchun juda mos. Ko'chat bog'da yoki idishda o'stirish mumkin.

Parvarish qilish bo'yicha ko'rsatmalar:
1. Har kuni sug'oring
2. Quyosh nuri ko'p kerak
3. Tayoq yordamida bog'lang
4. Haftada bir marta o'g'it bering''',
                'price': 8000,
                'original_price': 12000,
                'stock_quantity': 50,
                'is_featured': True,
                'is_available': True,
                'light_requirement': 'To\'liq quyosh',
                'water_requirement': 'Ko\'p',
                'temperature_range': '+15°C dan +35°C gacha',
                'care_level': 'easy',
                'condition': 'new',
                'height': '15-20 sm',
                'age': '2 oy',
                'pot_size': '10 sm',
            },
            {
                'name': 'Zamiokulkas (ZZ o\'simlik)',
                'slug': 'zamiokulkas-zz',
                'category': uy_kategory,
                'plant_type': plant_type,
                'short_description': 'Uy uchun ideal. Yorug\'liksiz ham yashaydi, kam sug\'orish kerak.',
                'description': '''Zamiokulkas (ZZ Plant) - eng chidamli va parvarishi oson uy o'simliklaridan biri. Kam yorug'likda va kam sug'orishda ham yaxshi o'sadi. Havoni tozalaydi va uyingizga yashil rang qo'shadi. Yangi boshlanuvchilar uchun juda mos.

Parvarish qilish bo'yicha ko'rsatmalar:
1. Oyiga 1-2 marta sug'oring
2. Yorug'likni ko'p talab qilmaydi
3. 3 oyda bir marta o'g'it bering
4. Barglarni artib turing''',
                'price': 35000,
                'original_price': 50000,
                'stock_quantity': 15,
                'is_featured': True,
                'is_available': True,
                'light_requirement': 'Kam yorug\'lik yetarli',
                'water_requirement': 'Kam',
                'temperature_range': '+15°C dan +30°C gacha',
                'care_level': 'easy',
                'condition': 'mature',
                'height': '40-50 sm',
                'pot_size': '20 sm',
                'age': '1 yil',
            },
        ]

        created_count = 0
        for prod_data in products:
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Mahsulot yaratildi: {product.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Mahsulot mavjud: {product.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n📊 Jami {created_count} ta yangi mahsulot yaratildi')
        )
        self.stdout.write(
            self.style.SUCCESS('\n🌐 Do\'kon sahifasini ko\'ring: http://127.0.0.1:8000/uz/dokon/')
        )
