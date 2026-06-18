"""
Tracker views for analytics API endpoints.
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .analytics import AnalyticsEngine
from .models import TrackedLink, Click, Commission, PlatformConnection
from apps.products.models import Product


class AnalyticsOverviewView(APIView):
    """GET /api/analytics/overview/ - Dashboard stats summary. Requires auth."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = AnalyticsEngine.get_dashboard_stats()
        return Response(stats)


class AnalyticsClicksView(APIView):
    """GET /api/analytics/clicks/ - Click data per platform. Requires auth."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        clicks = AnalyticsEngine.get_clicks_by_platform(days)
        top_products = AnalyticsEngine.get_top_products()
        return Response({
            'by_platform': clicks,
            'top_products': top_products,
        })


class AnalyticsEarningsView(APIView):
    """GET /api/analytics/earnings/ - Commission breakdown. Requires auth."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        earnings = AnalyticsEngine.get_earnings_breakdown(days)
        return Response(earnings)


class PlatformStatusView(APIView):
    """GET /api/analytics/status/ - All platform connection status. Requires auth."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_data = AnalyticsEngine.get_platform_status()
        return Response(status_data)


class CaptionPerformanceView(APIView):
    """GET /api/analytics/caption-performance/ - Caption style A/B performance. Requires auth."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        data = AnalyticsEngine.get_caption_performance(days)
        return Response(data)


class PlatformTestView(APIView):
    """POST /api/platforms/test/ - Test a platform connection. Requires auth."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        platform = request.data.get('platform', '').lower()

        poster_map = {
            'telegram': 'apps.poster.platforms.telegram_poster.TelegramPoster',
            'instagram': 'apps.poster.platforms.instagram_poster.InstagramPoster',
            'facebook': 'apps.poster.platforms.facebook_poster.FacebookPoster',
            'pinterest': 'apps.poster.platforms.pinterest_poster.PinterestPoster',
            'twitter': 'apps.poster.platforms.twitter_poster.TwitterPoster',
        }

        import importlib
        poster_path = poster_map.get(platform)
        if not poster_path:
            return Response({'error': f'Unknown platform: {platform}'}, status=400)

        try:
            module_path, class_name = poster_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            poster_class = getattr(module, class_name)
            result = poster_class().test_connection()
            return Response(result)
        except Exception as e:
            return Response({'connected': False, 'error': str(e)}, status=500)
