"""
Base scraper class for affiliate product scraping.
All platform scrapers should inherit from this.
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict
from decimal import Decimal

logger = logging.getLogger(__name__)

# Trending keywords for Gen Z fashion (ages 15-30)
TRENDING_KEYWORDS = [
    "co-ord set under 500",
    "Y2K dress",
    "bodycon dress under 699",
    "aesthetic dress",
    "indo western dress girls",
    "mini dress trending",
    "cottagecore dress india",
    "party dress under 999",
    "college girl dress",
    "summer dress 2025",
    "denim dress",
    "puff sleeve dress",
    "corset dress",
    "slip dress",
    "shirt dress",
    "maxi dress",
    "midi dress",
    "tiered dress",
    "smocked dress",
]


class BaseScraper:
    """Base class for product scrapers."""

    platform_name: str = "base"

    def __init__(self):
        self.products_scraped = 0
        self.errors = []

    def run(self) -> Dict:
        """
        Main entry point - scrape products and save to DB.
        Returns a summary dict.
        """
        raise NotImplementedError("Subclasses must implement run()")

    def filter_trending(
        self,
        products: List[Dict],
        min_rating: float = 4.0,
        max_price: int = 1500,
        min_reviews: int = 50,
    ) -> List[Dict]:
        """
        Filter products by quality and price criteria.
        Targets the 15-30 age group with budget-friendly options.
        """
        filtered = []
        for product in products:
            try:
                rating = float(product.get('rating', 0))
                price = float(product.get('sale_price', 0))
                reviews = int(product.get('review_count', 0))

                if (
                    rating >= min_rating
                    and price <= max_price
                    and price > 0
                    and reviews >= min_reviews
                ):
                    product['is_trending'] = rating >= 4.5 and reviews >= 200
                    filtered.append(product)
            except (ValueError, TypeError):
                continue

        return filtered

    def save_products(self, products: List[Dict]) -> int:
        """
        Save scraped products to the database.
        Returns count of new products saved.
        """
        from apps.products.models import Product

        saved = 0
        for item in products:
            try:
                # Check if product already exists by product_url
                product, created = Product.objects.get_or_create(
                    product_url=item['product_url'],
                    defaults={
                        'name': item.get('name', '')[:300],
                        'platform': self.platform_name,
                        'original_price': Decimal(str(item.get('original_price', 0))),
                        'sale_price': Decimal(str(item.get('sale_price', 0))),
                        'rating': float(item.get('rating', 0)),
                        'review_count': int(item.get('review_count', 0)),
                        'category': item.get('category', 'other'),
                        'image_url': item.get('image_url', ''),
                        'affiliate_url': item.get('affiliate_url', ''),
                        'is_trending': item.get('is_trending', False),
                    }
                )
                if created:
                    saved += 1
                    self.products_scraped += 1
            except Exception as e:
                self.errors.append(str(e))
                logger.error(f"Error saving product: {e}")

        return saved

    def get_summary(self) -> Dict:
        return {
            'platform': self.platform_name,
            'products_scraped': self.products_scraped,
            'errors': self.errors[:5],
            'timestamp': datetime.now().isoformat(),
        }
