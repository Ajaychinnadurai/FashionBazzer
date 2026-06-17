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

# ── Sample products for fallback when scrapers return nothing ──
SAMPLE_PRODUCTS = [
    {
        "name": "Trendy Floral Print Co-ord Set",
        "platform": "amazon",
        "original_price": 1499,
        "sale_price": 399,
        "rating": 4.5,
        "review_count": 2800,
        "category": "co-ord",
        "product_url": "https://www.amazon.in/dp/B0D1EXAMPLE",
        "is_trending": True,
    },
    {
        "name": "Y2K Stylish Bodycon Mini Dress",
        "platform": "meesho",
        "original_price": 999,
        "sale_price": 299,
        "rating": 4.3,
        "review_count": 1500,
        "category": "bodycon",
        "product_url": "https://www.meesho.com/p/example-1",
        "is_trending": True,
    },
    {
        "name": "Elegant Maxi Dress for Women",
        "platform": "amazon",
        "original_price": 1899,
        "sale_price": 549,
        "rating": 4.6,
        "review_count": 3200,
        "category": "cottagecore",
        "product_url": "https://www.amazon.in/dp/B0D2EXAMPLE",
        "is_trending": True,
    },
    {
        "name": "Printed Wrap Dress - Summer Special",
        "platform": "meesho",
        "original_price": 799,
        "sale_price": 249,
        "rating": 4.2,
        "review_count": 980,
        "category": "wrap",
        "product_url": "https://www.meesho.com/p/example-2",
        "is_trending": True,
    },
    {
        "name": "Indo-Western Fusion Dress",
        "platform": "amazon",
        "original_price": 2499,
        "sale_price": 899,
        "rating": 4.7,
        "review_count": 5600,
        "category": "indo-western",
        "product_url": "https://www.amazon.in/dp/B0D3EXAMPLE",
        "is_trending": True,
    },
    {
        "name": "Cut-Out Party Dress",
        "platform": "meesho",
        "original_price": 1299,
        "sale_price": 449,
        "rating": 4.4,
        "review_count": 2100,
        "category": "cut-out",
        "product_url": "https://www.meesho.com/p/example-3",
        "is_trending": True,
    },
    {
        "name": "Casual Athleisure Dress",
        "platform": "amazon",
        "original_price": 1099,
        "sale_price": 349,
        "rating": 4.1,
        "review_count": 750,
        "category": "athleisure",
        "product_url": "https://www.amazon.in/dp/B0D4EXAMPLE",
        "is_trending": False,
    },
    {
        "name": "Trendy Party Wear Western Dress",
        "platform": "meesho",
        "original_price": 1599,
        "sale_price": 499,
        "rating": 4.5,
        "review_count": 4100,
        "category": "other",
        "product_url": "https://www.meesho.com/p/example-4",
        "is_trending": True,
    },
]


def _create_sample_products() -> int:
    """Create sample fashion products in the database.
    Returns the number of products created.
    """
    import logging
    from apps.products.scrapers.image_scraper import fetch_unsplash_fashion

    logger = logging.getLogger(__name__)
    created = 0

    for idx, data in enumerate(SAMPLE_PRODUCTS):
        name = data["name"]

        # Skip if product with same name already exists
        if Product.objects.filter(name=name).exists():
            logger.info(f"Sample product already exists: {name[:40]}")
            continue

        # Get an Unsplash image for this product
        image_url = fetch_unsplash_fashion(
            category=data["category"],
            seed=idx,  # consistent per product
        )

        Product.objects.create(
            name=name,
            platform=data["platform"],
            original_price=data["original_price"],
            sale_price=data["sale_price"],
            rating=data["rating"],
            review_count=data["review_count"],
            category=data["category"],
            product_url=data["product_url"],
            affiliate_url=data["product_url"],  # same as product URL; link builder adds tracking
            image_url=image_url,
            is_trending=data["is_trending"],
        )
        created += 1
        logger.info(f"Created sample product #{idx+1}: {name[:40]}")

    return created


class SeedDataView(APIView):
    """
    GET /api/dashboard/seed/
    Triggers the full data pipeline to populate the database with initial data.
    """

    def get(self, request):
        import logging
        import threading
        logger = logging.getLogger(__name__)
        results = {'products': 0, 'content': 0, 'errors': []}

        # Step 1: Ensure we have at least sample products in the database instantly
        # so the user has immediate visual feedback and we avoid Render request timeouts.
        created_samples = 0
        if Product.objects.count() == 0:
            logger.info("Database empty. Pre-seeding sample products...")
            try:
                created_samples = _create_sample_products()
                results['sample_fallback'] = created_samples
                logger.info(f"Created {created_samples} sample products")
            except Exception as e:
                results['errors'].append(f'Sample product creation failed: {str(e)}')
                logger.error(f"Sample product creation failed: {e}")

        # Step 2: Trigger scraping and content generation asynchronously in a background thread
        # to prevent blocking the web request and triggering 504/client timeouts.
        def run_pipeline_in_background():
            from django.db import close_old_connections
            try:
                # 1. Scrape products
                from apps.poster.scheduler import scrape_trending_products
                logger.info("Background thread: starting product scraping...")
                scrape_trending_products()
                
                # 2. Generate content
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
            logger.info("Scraping & content generation pipeline started in background thread.")
        except Exception as e:
            results['errors'].append(f'Failed to start background pipeline: {str(e)}')
            logger.error(f"Failed to start background pipeline: {e}")

        # Step 4: Get current counts
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
