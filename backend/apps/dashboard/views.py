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
    Calls product scraping + AI content generation.
    Falls back to sample products if scraping yields nothing.
    """

    def get(self, request):
        import logging
        logger = logging.getLogger(__name__)
        results = {'products': 0, 'content': 0, 'errors': []}

        # Step 1: Scrape products from affiliate platforms
        scraped_count = 0
        try:
            from apps.poster.scheduler import scrape_trending_products
            scrape_result = scrape_trending_products()
            scraped_count = scrape_result.get('new_products', 0) or scrape_result.get('products_scraped', 0)
            logger.info(f"Seed: scraped {scraped_count} products")
        except Exception as e:
            results['errors'].append(f'Scraping failed: {str(e)}')
            logger.error(f"Seed scraping failed: {e}")

        # Step 2: Fallback — create sample products if scraping returned nothing
        results['products'] = scraped_count
        if scraped_count == 0 and Product.objects.count() == 0:
            logger.info("No products scraped. Falling back to sample products...")
            try:
                sample_count = _create_sample_products()
                results['products'] = sample_count
                results['sample_fallback'] = sample_count
                logger.info(f"Created {sample_count} sample products")
            except Exception as e:
                results['errors'].append(f'Sample product creation failed: {str(e)}')
                logger.error(f"Sample product creation failed: {e}")

        # Step 3: Generate AI content for all unprocessed products
        try:
            from apps.poster.scheduler import generate_content
            content_result = generate_content()
            results['content'] = content_result.get('generated', 0) + content_result.get('recycled', 0)
            logger.info(f"Seed: generated {results['content']} content items")
        except Exception as e:
            results['errors'].append(f'Content generation failed: {str(e)}')
            logger.error(f"Seed content generation failed: {e}")

        # Step 4: Get current counts
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
