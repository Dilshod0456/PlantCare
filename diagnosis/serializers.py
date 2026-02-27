from rest_framework import serializers
from .models import Disease, PlantImage, Recommendation

class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = '__all__'

class PlantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantImage
        fields = '__all__'

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'
