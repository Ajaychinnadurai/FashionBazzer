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


class SeedDataView(APIView):
    """
    GET /api/dashboard/seed/
    Triggers real product scraping and content generation in the background.
    Does NOT create any dummy/sample products — only real scraped data.
    Returns immediately while scraping runs asynchronously.
    """

    def get(self, request):
        import logging
        import threading
        logger = logging.getLogger(__name__)
        results = {'products': 0, 'content': 0, 'errors': []}

        # ⚠️ No sample/dummy products are ever created.
        # Only real scraped products from e-commerce sites are stored.

        # Trigger scraping and content generation asynchronously in a background thread
        # to prevent blocking the web request and triggering 504/client timeouts.
        def run_pipeline_in_background():
            from django.db import close_old_connections
            try:
                # 1. Scrape products from real e-commerce sites
                from apps.poster.scheduler import scrape_trending_products
                logger.info("Background thread: starting real product scraping...")
                scrape_trending_products()
                
                # 2. Generate AI content for scraped products
                from apps.poster.scheduler import generate_content
                logger.info("Background thread: starting content generation...")
                generate_content()
                
                logger.info("Background thread: seeding pipeline complete.")
            except Exception as bg_e:
                logger.error(f"Background pipeline thread error: {bg_e}")
            finally:
                close_old_connections()

        try:
            threading.Thread(target=run_pipeline_in_background, daemon=True).start()
            logger.info("Real scraping & content generation pipeline started in background thread.")
        except Exception as e:
            results['errors'].append(f'Failed to start background pipeline: {str(e)}')
            logger.error(f"Failed to start background pipeline: {e}")

        # Get current counts
        results['products'] = Product.objects.count()
        results['total_products'] = results['products']
        results['total_queue'] = PostQueue.objects.count()

        return Response(results)


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
