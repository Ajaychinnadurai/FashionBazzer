from django.test import TestCase
from apps.products.models import Product
from apps.content.ai_generator import ContentGenerator
from apps.poster.platforms.telegram_poster import TelegramPoster


class ContentGeneratorTestCase(TestCase):
    def setUp(self):
        # Create a test product
        self.product = Product.objects.create(
            name="Test Western Wear Bodycon Dress",
            platform="amazon",
            original_price=1200,
            sale_price=400,
            rating=4.5,
            review_count=150,
            category="bodycon",
            product_url="https://amazon.in/dp/AMZTEST",
            affiliate_url="https://amazon.in/dp/AMZTEST?tag=test-21",
            image_url="https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600",
            is_trending=True,
        )

    def test_content_generator(self):
        generator = ContentGenerator()
        post_queue = generator.generate_for_product(self.product)
        self.assertIsNotNone(post_queue)
        self.assertEqual(post_queue.status, 'pending')
        self.assertTrue(post_queue.image_path.endswith('.jpg'))
        self.assertGreater(len(post_queue.telegram_caption), 0)
        self.assertIn("Test Western Wear Bodycon Dress", post_queue.telegram_caption)


class TelegramPosterTestCase(TestCase):
    def test_connection(self):
        # Even if token is invalid or missing, test_connection should run and return a dict
        poster = TelegramPoster()
        result = poster.test_connection()
        self.assertIn('connected', result)
