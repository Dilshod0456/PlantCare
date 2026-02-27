from django.contrib import admin
from .models import Disease, PlantImage, Recommendation, AIModel, PlantType


@admin.register(PlantType)
class PlantTypeAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'code', 'category', 'scientific_name', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name_uz', 'name_en', 'name_ru', 'code', 'scientific_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('code', 'name_uz', 'name_en', 'name_ru', 'scientific_name')
        }),
        ('Qo\'shimcha', {
            'fields': ('category', 'description', 'image', 'is_active')
        }),
        ('Sanalar', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'created_at')
    search_fields = ('name', 'region')

@admin.register(PlantImage)
class PlantImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at', 'disease', 'confidence')
    search_fields = ('user__username',)
    list_filter = ('disease',)

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('disease', 'language', 'ai_source', 'created_at')
    list_filter = ('language', 'ai_source')


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'detection_type', 'plant_type', 'version', 'is_active', 'accuracy', 'uploaded_at', 'uploaded_by')
    list_filter = ('detection_type', 'plant_type', 'is_active', 'uploaded_at')
    search_fields = ('name', 'description', 'version')
    readonly_fields = ('uploaded_at', 'updated_at', 'get_model_key')
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'detection_type', 'plant_type', 'version', 'description')
        }),
        ('Model fayllari', {
            'fields': ('model_file', 'class_indices_file')
        }),
        ('Holat va statistika', {
            'fields': ('is_active', 'accuracy', 'total_classes')
        }),
        ('Qo\'shimcha ma\'lumotlar', {
            'fields': ('uploaded_by', 'uploaded_at', 'updated_at', 'get_model_key'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Yangi obyekt yaratilayotganda
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_model_key(self, obj):
        """Model kalitini ko'rsatish"""
        return obj.get_model_key()
    get_model_key.short_description = 'Model kaliti'

