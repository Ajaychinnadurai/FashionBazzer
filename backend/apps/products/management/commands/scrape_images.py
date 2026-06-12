"""
Management command to scrape real product images from e-commerce product pages.

Usage:
    python manage.py scrape_images                    # Batch update (20)
    python manage.py scrape_images --batch 50         # Custom batch size
    python manage.py scrape_images --product 5        # Single product
    python manage.py scrape_images --force-all        # Update ALL products
    python manage.py scrape_images --dry-run          # Preview without saving
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from apps.products.scrapers.image_scraper import (
    update_product_images,
    update_single_product_image,
    scrape_product_image,
    fetch_unsplash_fashion,
)
from apps.products.models import Product


class Command(BaseCommand):
    help = "Fetch real product images from Meesho/Amazon pages or Unsplash fallback"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch",
            type=int,
            default=20,
            help="Number of products to process (default: 20)",
        )
        parser.add_argument(
            "--product",
            type=int,
            help="Update image for a single product ID",
        )
        parser.add_argument(
            "--force-all",
            action="store_true",
            help="Update ALL products (not just picsum/empty ones)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without saving",
        )

    def handle(self, *args, **options):
        batch_size = options["batch"]
        product_id = options["product"]
        force_all = options["force_all"]
        dry_run = options["dry_run"]

        if product_id:
            self._handle_single(product_id, dry_run)
        elif dry_run:
            self._handle_dry_run(batch_size)
        elif force_all:
            self._handle_force_all(batch_size)
        else:
            self._handle_batch(batch_size)

    def _handle_single(self, product_id: int, dry_run: bool):
        self.stdout.write(f"\n🔍 Checking product #{product_id}...\n")
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            self.stderr.write(f"❌ Product #{product_id} not found")
            return

        self.stdout.write(f"   Name: {product.name[:60]}")
        self.stdout.write(f"   Platform: {product.platform}")
        self.stdout.write(f"   Current image: {product.image_url[:60] if product.image_url else '(empty)'}")
        self.stdout.write(f"   Product URL: {product.product_url[:80]}")

        if dry_run:
            self.stdout.write("\n   ✅ Dry-run — would scrape & update this product\n")
            return

        new_url = update_single_product_image(product_id)
        if new_url:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Updated! New image: {new_url[:80]}"))
        else:
            self.stderr.write("\n❌ Failed to update")

    def _handle_batch(self, batch_size: int):
        self.stdout.write(f"\n📸 Scraping images for up to {batch_size} products...\n")
        result = update_product_images(batch_size=batch_size)
        self._print_result(result)

    def _handle_force_all(self, batch_size: int):
        self.stdout.write(f"\n📸 Force-updating ALL products (batch: {batch_size})...\n")
        total = Product.objects.count()
        self.stdout.write(f"   Total products in DB: {total}\n")
        result = update_product_images(batch_size=total)
        self._print_result(result)

    def _handle_dry_run(self, batch_size: int):
        self.stdout.write(f"\n🔍 Dry-run: products needing updates...\n")
        picsum = Product.objects.filter(image_url__contains="picsum").count()
        empty = Product.objects.filter(image_url="").count()
        total = Product.objects.count()

        self.stdout.write(f"   Total products: {total}")
        self.stdout.write(f"   With picsum URLs: {picsum}")
        self.stdout.write(f"   With empty URLs: {empty}")
        self.stdout.write(f"   Up to date: {total - picsum - empty}")
        self.stdout.write(f"\n   Would process: {min(picsum + empty, batch_size)} products")
        self.stdout.write("   Run without --dry-run to apply\n")

    def _print_result(self, result: dict):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"✅ Processed: {result['processed']}"))
        if result["scraped_from_page"]:
            self.stdout.write(f"   Scraped from product page: {result['scraped_from_page']}")
        if result["unsplash_fallback"]:
            self.stdout.write(f"   Unsplash fallback: {result['unsplash_fallback']}")
        if result["errors"]:
            self.stderr.write(f"   Errors: {len(result['errors'])}")
            for err in result["errors"][:3]:
                self.stderr.write(f"     • {err}")
        self.stdout.write("")
