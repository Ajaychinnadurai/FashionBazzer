"""
Base scraper class for affiliate product scraping.
All platform scrapers should inherit from this.
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict
from decimal import Decimal

from django.utils import timezone

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
        Save or update scraped products in the database.
        - New products: created with all fields
        - Existing products: updated with fresher price/rating data
          (only if the new data has better price info — e.g. has MRP vs no MRP)

        Returns count of products created or updated.
        """
        from apps.products.models import Product

        processed = 0
        for item in products:
            try:
                new_price = Decimal(str(item.get('sale_price', 0)))
                new_original = Decimal(str(item.get('original_price', 0)))
                new_rating = float(item.get('rating', 0))
                new_reviews = int(item.get('review_count', 0))

                existing = Product.objects.filter(product_url=item['product_url']).first()

                if existing:
                    # ── Existing product: update if new data is more accurate ──
                    updated = False

                    # Update name if it was truncated or placeholder
                    new_name = item.get('name', '')[:300]
                    if new_name and len(new_name) > len(existing.name):
                        existing.name = new_name
                        updated = True

                    # Update prices if we now have a real MRP (was missing before)
                    if new_original > new_price and existing.has_fake_prices():
                        existing.original_price = new_original
                        existing.sale_price = new_price
                        existing.is_price_stale = False
                        existing.last_price_updated = timezone.now()
                        updated = True
                    elif new_price > 0 and existing.has_fake_prices() and new_original > 0:
                        existing.original_price = new_original
                        existing.sale_price = new_price
                        existing.last_price_updated = timezone.now()
                        updated = True

                    # Update rating/reviews if we found real data (default -> real)
                    if new_rating > 0 and (existing.rating == 0 or existing.review_count == 0):
                        existing.rating = new_rating
                        existing.review_count = new_reviews
                        updated = True

                    # Update image if missing or was a fallback (picsum/unsplash)
                    new_image = item.get('image_url', '')
                    if new_image and ('picsum' in existing.image_url or 'unsplash' in existing.image_url):
                        existing.image_url = new_image
                        updated = True

                    # Update affiliate URL if missing
                    new_aff = item.get('affiliate_url', '')
                    if new_aff and not existing.affiliate_url:
                        existing.affiliate_url = new_aff
                        updated = True

                    # Update category if it was 'other' and we have a better match
                    new_cat = item.get('category', 'other')
                    if existing.category == 'other' and new_cat != 'other':
                        existing.category = new_cat
                        updated = True

                    if updated:
                        existing.save()
                        processed += 1
                else:
                    # ── New product ──
                    # Flag products with fake prices (no real MRP found)
                    new_original = Decimal(str(item.get('original_price', 0)))
                    new_sale = Decimal(str(item.get('sale_price', 0)))
                    is_fake = (new_original > 0 and new_original == new_sale)

                    Product.objects.create(
                        name=item.get('name', '')[:300],
                        platform=self.platform_name,
                        original_price=new_original,
                        sale_price=new_sale,
                        rating=new_rating,
                        review_count=int(item.get('review_count', 0)),
                        category=item.get('category', 'other'),
                        product_url=item['product_url'],
                        affiliate_url=item.get('affiliate_url', ''),
                        image_url=item.get('image_url', ''),
                        is_trending=item.get('is_trending', False),
                        is_price_stale=is_fake,
                        last_price_updated=timezone.now() if not is_fake else None,
                    )
                    processed += 1
                    self.products_scraped += 1

            except Exception as e:
                self.errors.append(str(e))
                logger.error(f"Error saving product: {e}")

        return processed

    def get_summary(self) -> Dict:
        return {
            'platform': self.platform_name,
            'products_scraped': self.products_scraped,
            'errors': self.errors[:5],
            'timestamp': datetime.now().isoformat(),
        }
