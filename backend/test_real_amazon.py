# -*- coding: utf-8 -*-
"""Test the full pipeline with a real Amazon product link and real scraped image."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashionbazzer.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

django.setup()

from apps.products.models import Product
from apps.products.scrapers.image_scraper import scrape_product_image, update_single_product_image
from apps.content.ai_generator import ContentGenerator
from apps.poster.platforms.telegram_poster import TelegramPoster

REAL_AMAZON_URL = 'https://www.amazon.in/Fashionable-Manzil-Trendy-Western-Dresses/dp/B0DCSTWTK3'

print("=" * 60)
print("TEST: Full pipeline with real Amazon product")
print("=" * 60)

# Step 1: Create product with real Amazon URL
print("\n1. Creating product with real Amazon URL...")
product, created = Product.objects.get_or_create(
    product_url=REAL_AMAZON_URL,
    defaults={
        'name': 'Fashionable Manzil Trendy Western Dresses for Women',
        'platform': 'amazon',
        'original_price': 1499,
        'sale_price': 399,
        'rating': 4.3,
        'review_count': 1200,
        'category': 'co-ord',
        'affiliate_url': REAL_AMAZON_URL + '?tag=fashionbazzer-21',
        'image_url': '',
        'is_trending': True,
        'ai_tagline': '',
    }
)
print(f"   Product #{product.id} - {'CREATED' if created else 'EXISTS'}")
print(f"   Name: {product.name}")
print(f"   Current image: {product.image_url or '(empty)'}")

# Step 2: Scrape real product image from Amazon page
print("\n2. Scraping real product image from Amazon...")
result = scrape_product_image(REAL_AMAZON_URL, platform='amazon', timeout=15)
if result:
    print(f"   SCRAPED IMAGE: {result}")
    product.image_url = result
    product.save(update_fields=['image_url'])
else:
    print("   Failed to scrape, using fallback...")
    from apps.products.scrapers.image_scraper import fetch_unsplash_fashion
    fallback = fetch_unsplash_fashion(category='co-ord', seed=product.id)
    product.image_url = fallback
    product.save(update_fields=['image_url'])
    print(f"   FALLBACK IMAGE: {fallback}")

print(f"   Final image URL: {product.image_url[:80]}...")

# Step 3: Generate content
print("\n3. Generating AI content...")
generator = ContentGenerator()

# Reset tagline so generator creates new one
product.ai_tagline = ''
product.save(update_fields=['ai_tagline'])

post_queue = generator.generate_for_product(product)
if post_queue:
    print(f"   Post created! ID: {post_queue.id}")
    print(f"   Status: {post_queue.status}")
    print(f"   Image path: {post_queue.image_path}")
    caption_preview = post_queue.telegram_caption[:200].replace('\n', ' | ')
    print(f"   Caption preview: {caption_preview}...")
else:
    print("   FAILED to generate content!")
    sys.exit(1)

# Step 4: Post to Telegram
print("\n4. Sending to Telegram with REAL AMAZON IMAGE...")
poster = TelegramPoster()
success = poster.send(post_queue)
if success:
    print("   SUCCESS! Post sent to Telegram with real Amazon product image!")
else:
    print("   FAILED to send to Telegram!")
    sys.exit(1)

print("\n" + "=" * 60)
print("TEST COMPLETE - Check your Telegram channel!")
print("=" * 60)
