from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiseaseViewSet, PlantImageViewSet, RecommendationViewSet
from . import views
from .chat import chat_ai
from .disease_views import disease_list, disease_detail, analytics_dashboard

# Set app name for namespace
app_name = 'diagnosis'

router = DefaultRouter()
router.register(r'diseases', DiseaseViewSet)
router.register(r'images', PlantImageViewSet)
router.register(r'recommendations', RecommendationViewSet)

def chat_view(request):
    from django.shortcuts import render
    return render(request, 'diagnosis/chat.html')

urlpatterns = [
    path('', views.test_image, name='test_image'),  # Default diagnosis page
    path('test/', views.test_image, name='test_image'),
    path('api/', include(router.urls)),
    path('chat-ai/', chat_ai, name='chat_ai'),
    path('chat/', chat_view, name='chat'),
    # Disease pages
    path('diseases/', disease_list, name='disease_list'),
    path('diseases/<int:pk>/', disease_detail, name='disease_detail'),
    # Analytics
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
]
