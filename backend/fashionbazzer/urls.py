"""
FashionBazzer - Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.response import Response
from rest_framework.views import APIView


class RootStatusView(APIView):
    """Health endpoint for Render probes: GET / -> 200."""

    def get(self, request):
        return Response({"status": "ok"})


urlpatterns = [
    path('', RootStatusView.as_view(), name='root-status'),
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


# Serve media in both development and production
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
