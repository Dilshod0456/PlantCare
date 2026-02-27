from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.core.files.storage import default_storage
import tempfile
import os

from diagnosis.models import Disease, PlantImage, Recommendation
from diagnosis.serializers import DiseaseSerializer, PlantImageSerializer, RecommendationSerializer
from diagnosis.views import predict_image

# Try to import AI utils, fallback to simple version
try:
    from diagnosis.ai_utils import get_ai_recommendation, chat_with_ai
except ImportError:
    from diagnosis.ai_utils_simple import get_ai_recommendation, chat_with_ai

@api_view(['POST'])
@permission_classes([AllowAny])
def predict_disease_api(request):
    """
    API endpoint for disease prediction
    """
    try:
        if 'image' not in request.FILES:
            return Response({
                'error': True,
                'message': 'Rasm fayli majburiy'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        
        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
        
        try:
            # Predict disease
            disease_name, confidence = predict_image(temp_path)
            
            # Get or create disease
            disease, created = Disease.objects.get_or_create(
                name=disease_name,
                defaults={
                    'description': f'{disease_name} kasalligi aniqlandi',
                    'symptoms': 'Belgilar aniqlanmoqda...',
                    'treatment': 'Davolash usullari tayyorlanmoqda...'
                }
            )
            
            # Get AI recommendation
            lang = request.data.get('lang', 'uz')
            ai_recommendation = get_ai_recommendation(disease_name, lang=lang)
            
            # Save to database if user is authenticated
            plant_image = None
            if request.user.is_authenticated:
                plant_image = PlantImage.objects.create(
                    user=request.user,
                    image=image_file,
                    disease=disease,
                    disease_name=disease_name,
                    confidence=confidence,
                    accuracy=confidence * 100,
                    ai_result=ai_recommendation,
                    status='completed'
                )
            
            return Response({
                'error': False,
                'disease': disease_name,
                'confidence': round(confidence * 100, 2),
                'ai_recommendation': ai_recommendation,
                'disease_info': DiseaseSerializer(disease).data,
                'image_id': plant_image.id if plant_image else None
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        return Response({
            'error': True,
            'message': f'Server xatolik: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_api(request):
    """
    API endpoint for AI chat
    """
    try:
        question = request.data.get('question', '').strip()
        lang = request.data.get('lang', 'uz')
        
        if not question:
            return Response({
                'error': True,
                'message': 'Savol bo\'sh bo\'lmasligi kerak'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        answer = chat_with_ai(question, lang=lang)
        
        return Response({
            'error': False,
            'question': question,
            'answer': answer,
            'language': lang
        })
        
    except Exception as e:
        return Response({
            'error': True,
            'message': f'Server xatolik: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_history_api(request):
    """
    API endpoint for user's diagnosis history
    """
    try:
        images = PlantImage.objects.filter(user=request.user).order_by('-created_at')
        
        # Apply filters
        disease_filter = request.GET.get('disease')
        if disease_filter:
            images = images.filter(disease_name__icontains=disease_filter)
        
        # Pagination
        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = images.count()
        images_page = images[start:end]
        
        serializer = PlantImageSerializer(images_page, many=True)
        
        return Response({
            'error': False,
            'data': serializer.data,
            'pagination': {
                'total': total_count,
                'page': page,
                'page_size': page_size,
                'has_next': end < total_count,
                'has_previous': page > 1
            }
        })
        
    except Exception as e:
        return Response({
            'error': True,
            'message': f'Server xatolik: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def diseases_list_api(request):
    """
    API endpoint for diseases list
    """
    try:
        diseases = Disease.objects.all()
        search = request.GET.get('search')
        if search:
            diseases = diseases.filter(name__icontains=search)
        
        serializer = DiseaseSerializer(diseases, many=True)
        
        return Response({
            'error': False,
            'data': serializer.data
        })
        
    except Exception as e:
        return Response({
            'error': True,
            'message': f'Server xatolik: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
