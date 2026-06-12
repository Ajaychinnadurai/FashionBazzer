"""
Click tracking and commission models for FashionBazzer.
"""
from django.db import models


class TrackedLink(models.Model):
    """Shortened affiliate link with click tracking."""
    short_code = models.CharField(max_length=20, unique=True)
    affiliate_url = models.URLField(max_length=1000)
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='tracked_links'
    )
    platform = models.CharField(max_length=50)
    click_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-click_count']
        indexes = [
            models.Index(fields=['short_code']),
            models.Index(fields=['platform']),
        ]

    def __str__(self):
        return f"{self.short_code} -> {self.affiliate_url[:50]}"


class Click(models.Model):
    """Individual click event on a tracked link."""
    link = models.ForeignKey(
        TrackedLink, on_delete=models.CASCADE, related_name='clicks'
    )
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    referrer = models.URLField(max_length=1000, blank=True, default='')

    class Meta:
        ordering = ['-clicked_at']

    def __str__(self):
        return f"Click on {self.link.short_code} at {self.clicked_at}"


class Commission(models.Model):
    """Affiliate commission record."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='commissions'
    )
    affiliate_platform = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    order_id = models.CharField(max_length=200, blank=True, default='')
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"₹{self.amount} from {self.affiliate_platform} ({self.status})"


class PlatformConnection(models.Model):
    """Tracks connection status and health of each platform."""
    PLATFORM_CHOICES = [
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('pinterest', 'Pinterest'),
        ('twitter', 'Twitter/X'),
        ('threads', 'Threads'),
    ]

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, unique=True)
    is_connected = models.BooleanField(default=False)
    last_checked = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, default='')
    posts_today = models.IntegerField(default=0)
    posts_total = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.get_platform_display()}: {'✅' if self.is_connected else '❌'}"
