"""
PlantCare AI - Model Manager
Bu modul turli xil o'simlik kasalliklari va zararkunandalarni aniqlash uchun
modellarni boshqaradi. Django AIModel dan ma'lumotlarni yuklaydi.
"""

import os
import json
import tensorflow as tf
from tensorflow.keras.models import load_model
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

class ModelManager:
    """Model va parametrlarni boshqaruvchi klass"""
    
    def __init__(self):
        self.models = {}
        self.class_indices = {}
        self.django_available = False
        self.load_model_configs()
    
    def load_model_configs(self):
        """Barcha mavjud model konfiguratsiyalarini yuklash"""
        # Django modellaridan yuklash
        if self._load_from_django():
            print("✅ Django modellaridan AI modellar yuklandi")
            return
        
        # Fallback: Statik konfiguratsiya
        print("⚠️ Django mavjud emas, statik konfiguratsiya ishlatilmoqda")
        self._load_static_configs()
    
    def _load_from_django(self):
        """Django AIModel dan modellarni yuklash"""
        try:
            # Django import qilish
            import django
            from django.conf import settings
            
            # Django sozlanganligini tekshirish
            if not settings.configured:
                return False
            
            # AIModel ni import qilish
            from diagnosis.models import AIModel
            
            # Faqat faol modellarni yuklash
            active_models = AIModel.objects.filter(is_active=True).select_related('plant_type')
            
            if not active_models.exists():
                print("⚠️ Faol modellar topilmadi")
                return False
            
            # Har bir modelni qo'shish
            for model_obj in active_models:
                plant_code = model_obj.plant_type.code if model_obj.plant_type else 'all'
                
                self.add_model_config(
                    model_type=model_obj.detection_type,
                    plant=plant_code,
                    model_path=model_obj.model_file.path,
                    indices_path=model_obj.class_indices_file.path,
                    description=model_obj.name
                )
                
                print(f"📦 Model qo'shildi: {model_obj.name} ({model_obj.detection_type}_{plant_code})")
            
            self.django_available = True
            return True
            
        except Exception as e:
            print(f"❌ Django modellaridan yuklashda xato: {e}")
            return False
    
    def _load_static_configs(self):
        """Statik model konfiguratsiyalarini yuklash (fallback)"""
        # Asosiy kasallik aniqlash modeli
        self.add_model_config(
            model_type='disease',
            plant='all',
            model_path='plant_disease_model.h5',
            indices_path='class_indices.json',
            description='Umumiy o\'simlik kasalliklari modeli'
        )
    
    def add_model_config(self, model_type, plant, model_path, indices_path, description=''):
        """Model konfiguratsiyasini qo'shish"""
        key = f"{model_type}_{plant}"
        self.models[key] = {
            'type': model_type,
            'plant': plant,
            'model_path': os.path.join(BASE_DIR, model_path),
            'indices_path': os.path.join(BASE_DIR, indices_path),
            'description': description,
            'loaded': False,
            'model': None,
            'indices': None
        }
    
    def get_model_key(self, detection_type, plant_type):
        """Parametrlarga ko'ra model kalitini olish"""
        # Agar maxsus o'simlik uchun model bo'lsa, uni qaytarish
        specific_key = f"{detection_type}_{plant_type}"
        if specific_key in self.models:
            return specific_key
        
        # Aks holda umumiy modelni qaytarish
        general_key = f"{detection_type}_all"
        if general_key in self.models:
            return general_key
        
        # Agar detection type uchun model yo'q bo'lsa, 'disease_all' dan foydalanish
        if 'disease_all' in self.models:
            print(f"⚠️ {detection_type} uchun maxsus model topilmadi, 'disease_all' ishlatilmoqda")
            return 'disease_all'
        
        return None
    
    def load_model(self, model_key):
        """Modelni yuklash"""
        if model_key not in self.models:
            raise ValueError(f"Model topilmadi: {model_key}")
        
        model_config = self.models[model_key]
        
        # Agar model allaqachon yuklangan bo'lsa
        if model_config['loaded']:
            return model_config['model'], model_config['indices']
        
        print(f"🔄 Model yuklanmoqda: {model_config['description']}")
        
        # Class indices ni yuklash
        with open(model_config['indices_path'], 'r', encoding='utf-8') as f:
            indices = json.load(f)
        
        # Modelni yuklash
        model = load_model(model_config['model_path'])
        
        # Konfiguratsiyani yangilash
        model_config['model'] = model
        model_config['indices'] = indices
        model_config['loaded'] = True
        
        print(f"✅ Model muvaffaqiyatli yuklandi: {model_config['description']}")
        print(f"📊 Sinflar soni: {len(indices)}")
        
        return model, indices
    
    def get_model(self, detection_type, plant_type):
        """Parametrlarga ko'ra modelni olish"""
        model_key = self.get_model_key(detection_type, plant_type)
        
        if not model_key:
            raise ValueError(
                f"Ushbu parametrlar uchun model topilmadi: "
                f"detection_type={detection_type}, plant_type={plant_type}"
            )
        
        return self.load_model(model_key)
    
    def get_available_plants(self, detection_type):
        """Muayyan aniqlash turi uchun mavjud o'simliklar ro'yxatini olish"""
        plants = set()
        
        for key, config in self.models.items():
            if config['type'] == detection_type:
                if config['plant'] != 'all':
                    plants.add(config['plant'])
        
        # Agar maxsus o'simlik modellari bo'lmasa, umumiy ro'yxatni qaytarish
        if not plants:
            return self.get_default_plants(detection_type)
        
        return sorted(list(plants))
    
    def get_default_plants(self, detection_type):
        """Default o'simliklar ro'yxati"""
        if detection_type == 'disease':
            return [
                'tomato', 'potato', 'pepper', 'grape', 
                'apple', 'corn', 'strawberry', 'peach'
            ]
        elif detection_type == 'pest':
            return ['tomato', 'potato', 'cotton', 'wheat', 'rice']
        else:
            return []
    
    def get_plant_name_uz(self, plant_code):
        """O'simlik kodini o'zbek tilidagi nomiga o'girish"""
        plant_names = {
            'tomato': 'Pomidor',
            'potato': 'Kartoshka',
            'pepper': 'Qalampir',
            'grape': 'Uzum',
            'apple': 'Olma',
            'corn': 'Makkajo\'xori',
            'strawberry': 'Qulupnay',
            'peach': 'Shaftoli',
            'cotton': 'Paxta',
            'wheat': 'Bug\'doy',
            'rice': 'Guruch'
        }
        return plant_names.get(plant_code, plant_code.title())
    
    def unload_all_models(self):
        """Barcha modellarni xotiradan tozalash"""
        for key, config in self.models.items():
            if config['loaded']:
                config['model'] = None
                config['indices'] = None
                config['loaded'] = False
        print("🗑️ Barcha modellar xotiradan tozalandi")
    
    def get_model_info(self):
        """Barcha modellar haqida ma'lumot olish"""
        info = []
        for key, config in self.models.items():
            info.append({
                'key': key,
                'type': config['type'],
                'plant': config['plant'],
                'description': config['description'],
                'loaded': config['loaded'],
                'model_exists': os.path.exists(config['model_path']),
                'indices_exists': os.path.exists(config['indices_path'])
            })
        return info


# Global model manager instance
model_manager = ModelManager()


def predict_with_manager(image, detection_type, plant_type):
    """Model manager yordamida bashorat qilish"""
    import numpy as np
    from PIL import Image
    
    # Modelni olish
    model, class_indices = model_manager.get_model(detection_type, plant_type)
    
    # Rasmni qayta ishlash
    img = Image.open(image)
    img = img.convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Bashorat
    predictions = model.predict(img_array, verbose=0)
    predicted_class_index = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_class_index])
    
    # Class nomini topish
    class_name = None
    for name, idx in class_indices.items():
        if idx == predicted_class_index:
            class_name = name
            break
    
    # Return as tuple (class_name, confidence) for compatibility
    return class_name, confidence


if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("PlantCare AI - Model Manager Test")
    print("=" * 60)
    
    manager = ModelManager()
    
    print("\n📋 Mavjud modellar:")
    for info in manager.get_model_info():
        print(f"\n  🔹 {info['key']}")
        print(f"     Tur: {info['type']}")
        print(f"     O'simlik: {info['plant']}")
        print(f"     Tavsif: {info['description']}")
        print(f"     Model mavjud: {'✅' if info['model_exists'] else '❌'}")
        print(f"     Indices mavjud: {'✅' if info['indices_exists'] else '❌'}")
    
    print("\n🌱 Kasallik aniqlash uchun o'simliklar:")
    disease_plants = manager.get_available_plants('disease')
    for plant in disease_plants:
        print(f"  - {plant}: {manager.get_plant_name_uz(plant)}")
    
    print("\n🐛 Zararkunanda aniqlash uchun o'simliklar:")
    pest_plants = manager.get_available_plants('pest')
    for plant in pest_plants:
        print(f"  - {plant}: {manager.get_plant_name_uz(plant)}")
    
    print("\n" + "=" * 60)
