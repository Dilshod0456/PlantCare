"""
Mavjud plant_disease_model.h5 ni bazaga import qilish
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from diagnosis.models import AIModel, PlantType
from pathlib import Path


class Command(BaseCommand):
    help = "Mavjud plant_disease_model.h5 ni AIModel bazasiga qo'shadi"

    def handle(self, *args, **options):
        models_dir = Path(settings.BASE_DIR) / 'models'
        model_file_path = models_dir / 'plant_disease_model.h5'
        indices_file_path = models_dir / 'class_indices.json'

        # Fayllar mavjudligini tekshirish
        if not model_file_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ Model fayli topilmadi: {model_file_path}'))
            return

        if not indices_file_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ Class indices fayli topilmadi: {indices_file_path}'))
            return

        # 'all' o'simlik turini olish
        try:
            plant_type_all = PlantType.objects.get(code='all')
        except PlantType.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ "all" o\'simlik turi topilmadi. Avval populate_plant_types buyrug\'ini bajaring.'))
            return

        # Mavjud modelni tekshirish
        existing_model = AIModel.objects.filter(
            detection_type='disease',
            plant_type=plant_type_all,
            version='1.0'
        ).first()

        if existing_model:
            self.stdout.write(self.style.WARNING(f'⚠️ Model allaqachon mavjud: {existing_model.name}'))
            
            # Fayllarni yangilash
            with open(model_file_path, 'rb') as mf:
                existing_model.model_file.save('plant_disease_model.h5', File(mf), save=False)
            
            with open(indices_file_path, 'rb') as inf:
                existing_model.class_indices_file.save('class_indices.json', File(inf), save=False)
            
            existing_model.save()
            self.stdout.write(self.style.SUCCESS('✅ Model fayllari yangilandi'))
            return

        # Yangi model yaratish
        ai_model = AIModel(
            name='Umumiy o\'simlik kasalliklari modeli v1.0',
            detection_type='disease',
            plant_type=plant_type_all,
            description='38 xil o\'simlik kasalligini aniqlaydigan asosiy model. '
                       'Olma, uzum, pomidor, kartoshka, makkajo\'xori va boshqa o\'simliklar uchun.',
            is_active=True,
            version='1.0',
            accuracy=95.5,
            total_classes=38
        )

        # Fayllarni qo'shish
        with open(model_file_path, 'rb') as mf:
            ai_model.model_file.save('plant_disease_model.h5', File(mf), save=False)
        
        with open(indices_file_path, 'rb') as inf:
            ai_model.class_indices_file.save('class_indices.json', File(inf), save=False)

        ai_model.save()

        self.stdout.write(
            self.style.SUCCESS(f'✅ Model muvaffaqiyatli qo\'shildi: {ai_model.name}')
        )
        self.stdout.write(f'   📦 Model fayli: {ai_model.model_file.name}')
        self.stdout.write(f'   📄 Indices fayli: {ai_model.class_indices_file.name}')
        self.stdout.write(f'   🎯 Aniqlik: {ai_model.accuracy}%')
        self.stdout.write(f'   📊 Sinflar soni: {ai_model.total_classes}')
