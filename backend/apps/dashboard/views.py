"""
Dashboard views for the React frontend.
Aggregates data from all apps into a single dashboard API.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, Q, Max, F
from django.utils import timezone
from datetime import timedelta

from apps.tracker.analytics import AnalyticsEngine
from apps.tracker.models import TrackedLink, Click, Commission, PlatformConnection
from apps.products.models import Product
from apps.poster.models import PostQueue


class SeedDataView(APIView):
    """
    GET /api/dashboard/seed/
    Admin-only. Triggers real product scraping and content generation in the background.
    Does NOT create any dummy/sample products — only real scraped data.
    Returns immediately while scraping runs asynchronously.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

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


class DataQualityView(APIView):
    """
    GET /api/dashboard/data-quality/
    Admin-only. Returns product data quality metrics for monitoring stale prices,
    missing ratings, and overall data health.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        total = Product.objects.count()
        stale_count = Product.objects.filter(is_price_stale=True).count()
        missing_rating_count = Product.objects.filter(Q(rating=0) | (Q(review_count=0) & Q(rating__lte=4.0))).count()
        has_content = Product.objects.filter(ai_tagline__gt='').count()

        # Average discount (only among products with real MRP)
        with_discount = Product.objects.filter(
            sale_price__gt=0,
            original_price__gt=0,
        ).filter(original_price__gt=F('sale_price'))
        avg_discount = with_discount.aggregate(
            avg=Avg(
                (F('original_price') - F('sale_price'))
                / F('original_price') * 100
            )
        )['avg'] or 0

        # Platform distribution
        platform_dist = list(
            Product.objects.values('platform')
            .annotate(count=Count('id'), stale=Count('id', filter=Q(is_price_stale=True)))
            .order_by('-count')
        )

        # Category distribution
        cat_dist = list(
            Product.objects.values('category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Worst offenders: top 10 products with stale prices
        worst_stale = list(
            Product.objects.filter(is_price_stale=True)
            .values('id', 'name', 'platform', 'sale_price', 'original_price', 'rating', 'review_count', 'last_scraped')
            .order_by('?')[:10]
        )

        # Products with missing ratings
        worst_ratings = list(
            Product.objects.filter(Q(rating=0) | (Q(review_count=0) & Q(rating__lte=4.0)))
            .values('id', 'name', 'platform', 'sale_price', 'rating', 'review_count', 'last_scraped')
            .order_by('?')[:10]
        )

        # Fresh products (updated within last 24h)
        fresh_cutoff = timezone.now() - timedelta(hours=24)
        fresh_count = Product.objects.filter(last_price_updated__gte=fresh_cutoff).count()

        # Last refresh time from any product
        last_refresh = Product.objects.aggregate(last=Max('last_price_updated'))['last']

        # Products with content vs without
        content_ratio = round((has_content / total * 100), 1) if total > 0 else 0

        return Response({
            'total_products': total,
            'stale_count': stale_count,
            'stale_percent': round((stale_count / total * 100), 1) if total > 0 else 0,
            'missing_rating_count': missing_rating_count,
            'missing_rating_percent': round((missing_rating_count / total * 100), 1) if total > 0 else 0,
            'has_content': has_content,
            'content_ratio': content_ratio,
            'fresh_count': fresh_count,
            'avg_discount': round(avg_discount, 1),
            'last_refresh': last_refresh,
            'platform_distribution': platform_dist,
            'category_distribution': cat_dist,
            'worst_stale_products': worst_stale,
            'worst_rating_products': worst_ratings,
        })


class DashboardView(APIView):
    """
    GET /api/dashboard/
    Returns all dashboard data in a single request.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

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
