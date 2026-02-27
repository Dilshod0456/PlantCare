from django.db import models
from django.conf import settings


class PlantType(models.Model):
    """O'simlik turlari"""
    
    code = models.CharField(max_length=50, unique=True, verbose_name='Kod', help_text='Masalan: tomato, potato, corn')
    name_uz = models.CharField(max_length=100, verbose_name='Nomi (O\'zbek)', help_text='Masalan: Pomidor, Kartoshka')
    name_en = models.CharField(max_length=100, blank=True, verbose_name='Nomi (English)')
    name_ru = models.CharField(max_length=100, blank=True, verbose_name='Nomi (Русский)')
    
    description = models.TextField(blank=True, verbose_name='Tavsif')
    scientific_name = models.CharField(max_length=150, blank=True, verbose_name='Ilmiy nomi', help_text='Masalan: Solanum lycopersicum')
    
    # Kategoriya
    category = models.CharField(max_length=50, blank=True, verbose_name='Kategoriya', help_text='Masalan: Sabzavot, Meva, Don')
    
    # Rasm
    image = models.ImageField(upload_to='plant_types/', blank=True, null=True, verbose_name='Rasm')
    
    # Holat
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    
    # Sanalar
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqt')
    
    class Meta:
        ordering = ['name_uz']
        verbose_name = 'O\'simlik turi'
        verbose_name_plural = 'O\'simlik turlari'
    
    def __str__(self):
        return f"{self.name_uz} ({self.code})"


class Disease(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    symptoms = models.TextField(blank=True)
    causes = models.TextField(blank=True)
    prevention = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    region = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PlantImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='plant_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)  # History uchun qo'shildi
    disease = models.ForeignKey(Disease, on_delete=models.SET_NULL, null=True, blank=True)
    disease_name = models.CharField(max_length=255, blank=True)  # AI natijasi uchun
    confidence = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)  # History uchun qo'shildi
    ai_result = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='completed', choices=[
        ('processing', 'Tahlil qilinmoqda'),
        ('completed', 'Yakunlandi'),
        ('failed', 'Xato')
    ])

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.disease_name or 'Unknown'} - {self.created_at}"
    
    def save(self, *args, **kwargs):
        # Confidence ni accuracy ga ham saqlash
        if self.confidence and not self.accuracy:
            self.accuracy = self.confidence * 100  # 0.95 -> 95%
        super().save(*args, **kwargs)

class Recommendation(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    text = models.TextField()
    language = models.CharField(max_length=10, default='uz')
    ai_source = models.CharField(max_length=50, default='GEMINI')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.disease.name} - {self.language}"


class AIModel(models.Model):
    """AI modellarini saqlash uchun model"""
    
    DETECTION_TYPES = [
        ('disease', 'Kasallik aniqlash'),
        ('pest', 'Zararkunanda aniqlash'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Model nomi', help_text='Masalan: Pomidor kasalliklari modeli v2.0')
    detection_type = models.CharField(max_length=20, choices=DETECTION_TYPES, default='disease', verbose_name='Aniqlash turi')
    plant_type = models.ForeignKey(PlantType, on_delete=models.CASCADE, related_name='ai_models', verbose_name='O\'simlik turi', help_text='Qaysi o\'simlik uchun model')
    
    # Model fayllari
    model_file = models.FileField(upload_to='ai_models/', verbose_name='Model fayli (.h5)', help_text='TensorFlow/Keras .h5 model fayli')
    class_indices_file = models.FileField(upload_to='ai_models/', verbose_name='Class indices fayli (.json)', help_text='Sinflar indekslari JSON fayli')
    
    # Qo'shimcha ma'lumotlar
    description = models.TextField(blank=True, verbose_name='Tavsif', help_text='Model haqida qo\'shimcha ma\'lumot')
    is_active = models.BooleanField(default=True, verbose_name='Faol', help_text='Faqat faol modellar ishlatiladi')
    version = models.CharField(max_length=50, blank=True, verbose_name='Versiya', help_text='Model versiyasi')
    
    # Statistika
    accuracy = models.FloatField(null=True, blank=True, verbose_name='Aniqlik (%)', help_text='Model aniqligi (test ma\'lumotlarida)')
    total_classes = models.IntegerField(null=True, blank=True, verbose_name='Sinflar soni')
    
    # Sanalar
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Yuklangan vaqt')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqt')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Yuklagan foydalanuvchi')
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'AI Model'
        verbose_name_plural = 'AI Modellar'
        unique_together = ['detection_type', 'plant_type', 'version']
    
    def __str__(self):
        status = '✅' if self.is_active else '❌'
        plant_name = self.plant_type.name_uz if self.plant_type else 'Barcha'
        return f"{status} {self.name} ({self.get_detection_type_display()} - {plant_name})"
    
    def get_model_key(self):
        """Model kalitini qaytarish (model_manager uchun)"""
        plant_code = self.plant_type.code if self.plant_type else 'all'
        return f"{self.detection_type}_{plant_code}"

