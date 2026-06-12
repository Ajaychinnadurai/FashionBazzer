"""
Dashboard views for the React frontend.
Aggregates data from all apps into a single dashboard API.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.tracker.analytics import AnalyticsEngine
from apps.tracker.models import TrackedLink, Click, Commission, PlatformConnection
from apps.products.models import Product
from apps.poster.models import PostQueue


class DashboardView(APIView):
    """
    GET /api/dashboard/
    Returns all dashboard data in a single request.
    """

    def get(self, request):
        # Get date filters
        days = int(request.query_params.get('days', 7))

        stats = AnalyticsEngine.get_dashboard_stats()
        clicks_by_platform = AnalyticsEngine.get_clicks_by_platform(days)
        earnings = AnalyticsEngine.get_earnings_breakdown(days)
        top_products = AnalyticsEngine.get_top_products(5)
        platform_status = AnalyticsEngine.get_platform_status()

        # Recent posts
        recent_posts = PostQueue.objects.select_related('product').order_by('-created_at')[:10]
        posts_data = []
        for post in recent_posts:
            posts_data.append({
                'id': post.id,
                'product_name': post.product.name[:50] if post.product else '',
                'status': post.status,
                'scheduled_time': post.scheduled_time,
                'published_at': post.published_at,
            })

        return Response({
            'stats': stats,
            'clicks_by_platform': clicks_by_platform,
            'earnings': earnings,
            'top_products': top_products,
            'platform_status': platform_status,
            'recent_posts': posts_data,
        })
