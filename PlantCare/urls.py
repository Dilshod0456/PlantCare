from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# Non-internationalized URLs (without language prefix)
urlpatterns = [
    # Language switcher AJAX URL
    path('i18n/', include('django.conf.urls.i18n')),
    # API endpoints (usually don't need translation)
    path('api/v1/', include('plantapi.urls')),
]

# Internationalized URLs (with language prefix)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('diagnosis/', include('diagnosis.urls')),
    path('users/', include('users.urls')),
    path('dokon/', include('shop.urls')),
    prefix_default_language=True  # Changed to True for proper URL handling
)

# Static and media files (only in DEBUG mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)