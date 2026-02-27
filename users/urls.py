from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView

# Set app name for namespace
app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('history/', views.history, name='history'),
]
