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
    Triggers the full data pipeline to populate the database with initial data.
    Calls product scraping + AI content generation.
    """

    def get(self, request):
        import logging
        logger = logging.getLogger(__name__)
        results = {'products': 0, 'content': 0, 'errors': []}

        # Step 1: Scrape products
        try:
            from apps.poster.scheduler import scrape_trending_products
            scrape_result = scrape_trending_products()
            results['products'] = scrape_result.get('new_products', 0) or scrape_result.get('products_scraped', 0)
            logger.info(f"Seed: scraped {results['products']} products")
        except Exception as e:
            results['errors'].append(f'Scraping failed: {str(e)}')
            logger.error(f"Seed scraping failed: {e}")

        # Step 2: Generate AI content
        try:
            from apps.poster.scheduler import generate_content
            content_result = generate_content()
            results['content'] = content_result.get('generated', 0) + content_result.get('recycled', 0)
            logger.info(f"Seed: generated {results['content']} content items")
        except Exception as e:
            results['errors'].append(f'Content generation failed: {str(e)}')
            logger.error(f"Seed content generation failed: {e}")

        # Step 3: Get current counts
        from apps.products.models import Product
        from apps.poster.models import PostQueue
        results['total_products'] = Product.objects.count()
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
