from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('predict/', views.predict_disease_api, name='api_predict'),
    path('chat/', views.chat_api, name='api_chat'),
    path('history/', views.user_history_api, name='api_history'),
    path('diseases/', views.diseases_list_api, name='api_diseases'),
]
