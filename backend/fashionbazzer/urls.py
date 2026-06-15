"""
FashionBazzer - Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/products/', include('apps.products.urls')),
    path('api/queue/', include('apps.poster.urls')),
    path('api/analytics/', include('apps.tracker.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/marketing/', include('apps.marketing.urls')),
    # Redirect + Track clicks (no /api/ prefix)
    path('r/', include('apps.tracker.redirect_urls')),
]

# Serve media in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
