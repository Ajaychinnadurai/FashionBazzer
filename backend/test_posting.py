# -*- coding: utf-8 -*-
"""
Test script for FashionBazzer posting pipeline.
"""
import os
import sys
import django

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashionbazzer.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.poster.platforms.telegram_poster import TelegramPoster
from apps.content.ai_generator import ContentGenerator
from apps.products.models import Product


def run():
    print("=== FashionBazzer Posting Test ===\n")

    # 1. Test Telegram connection
    print("1. Testing Telegram bot connection...")
    poster = TelegramPoster()
    result = poster.test_connection()
    print(f"   Result: {result}")

    if not result.get('connected'):
        print("   ERROR: Telegram bot not connected!")
        return False

    # 2. Generate content for a product
    print("\n2. Generating AI content for products...")
    generator = ContentGenerator()
    product = Product.objects.filter(ai_tagline='').first()
    if not product:
        product = Product.objects.first()
        print(f"   Using product #{product.id}")

    post_queue = generator.generate_for_product(product)
    if post_queue:
        print(f"   Post created! ID: {post_queue.id}")
        print(f"   Status: {post_queue.status}")
        print(f"   Image path: {post_queue.image_path}")
        caption = post_queue.telegram_caption[:100].replace(chr(8206), '').replace(chr(8207), '')
        print(f"   Caption preview: {caption}...")
    else:
        print("   ERROR: Content generation failed!")
        return False

    # 3. Send to Telegram
    print("\n3. Sending to Telegram channel...")
    success = poster.send(post_queue)
    if success:
        print("   SUCCESS! Post sent to Telegram!")
    else:
        print("   ERROR: Failed to send to Telegram!")
        return False

    print("\n=== TEST COMPLETE ===")
    return True


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
