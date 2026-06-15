from django.test import TestCase
from apps.products.models import Product
from apps.products.scrapers.image_scraper import fetch_unsplash_fashion, scrape_product_image


class ImageScraperTestCase(TestCase):
    def test_fetch_unsplash_fashion(self):
        url_coord = fetch_unsplash_fashion("co-ord", 123)
        self.assertIn("images.unsplash.com", url_coord)
        self.assertIn("auto=format", url_coord)

        # Test fallback to other
        url_invalid = fetch_unsplash_fashion("invalid-category", 123)
        self.assertIn("images.unsplash.com", url_invalid)

    def test_scrape_product_image_invalid(self):
        url = "http://localhost:8000/some/path"
        result = scrape_product_image(url, "amazon")
        self.assertIsNone(result)
