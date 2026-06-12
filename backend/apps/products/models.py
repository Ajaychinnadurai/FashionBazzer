"""
Product and affiliate product models for FashionBazzer.
"""
from django.db import models


class Product(models.Model):
    """Represents a trending dress product from affiliate platforms."""
    CATEGORY_CHOICES = [
        ('co-ord', 'Co-ord Sets'),
        ('y2k', 'Y2K Dresses'),
        ('bodycon', 'Bodycon Mini Dresses'),
        ('cottagecore', 'Cottagecore Maxi Dresses'),
        ('indo-western', 'Indo-Western Fusion'),
        ('athleisure', 'Athleisure Dresses'),
        ('cut-out', 'Cut-out Dresses'),
        ('wrap', 'Printed Wrap Dresses'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=300)
    platform = models.CharField(max_length=50, help_text="meesho, amazon, flipkart, myntra, ajio")
    original_price = models.DecimalField(max_digits=8, decimal_places=2)
    sale_price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_percent = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    product_url = models.URLField(max_length=1000)
    affiliate_url = models.URLField(max_length=1000, blank=True, default='')
    image_url = models.URLField(max_length=1000, blank=True, default='')
    local_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_trending = models.BooleanField(default=False)
    ai_tagline = models.TextField(blank=True, default='')
    last_scraped = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['platform', 'is_trending']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.name[:50]}... (₹{self.sale_price})"

    def save(self, *args, **kwargs):
        if self.original_price and self.sale_price and self.original_price > 0:
            self.discount_percent = int(
                (1 - (float(self.sale_price) / float(self.original_price))) * 100
            )
        super().save(*args, **kwargs)
