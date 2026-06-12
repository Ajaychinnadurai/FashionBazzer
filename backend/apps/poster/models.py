"""
Post queue and content models for FashionBazzer.
"""
from django.db import models


class PostQueue(models.Model):
    """Queued post ready for publishing across platforms."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ]

    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='posts'
    )
    telegram_caption = models.TextField(blank=True, default='')
    instagram_caption = models.TextField(blank=True, default='')
    facebook_caption = models.TextField(blank=True, default='')
    pinterest_caption = models.TextField(blank=True, default='')
    twitter_caption = models.TextField(blank=True, default='')
    threads_caption = models.TextField(blank=True, default='')
    image_path = models.CharField(max_length=500, blank=True, default='')
    public_image_url = models.URLField(max_length=1000, blank=True, default='')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    caption_style = models.CharField(max_length=50, blank=True, default='')
    scheduled_time = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Post queue"

    def __str__(self):
        return f"Post #{self.id} - {self.product.name[:40]} ({self.status})"


class PostLog(models.Model):
    """Log of published posts per platform."""
    PLATFORM_CHOICES = [
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('pinterest', 'Pinterest'),
        ('twitter', 'Twitter/X'),
        ('threads', 'Threads'),
    ]

    post = models.ForeignKey(
        PostQueue, on_delete=models.CASCADE, related_name='logs'
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    platform_post_id = models.CharField(max_length=200, blank=True, default='')
    status = models.CharField(max_length=20, default='success')
    error_message = models.TextField(blank=True, default='')
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.platform} - {self.status}"
