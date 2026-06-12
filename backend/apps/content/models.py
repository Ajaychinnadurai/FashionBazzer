"""
AI generated content models for FashionBazzer.
"""
from django.db import models

# Content generation is handled via PostQueue in the poster app.
# This file exists for future content-specific models like:
# - Caption templates
# - AI generation logs
# - Image composition templates


class GenerationLog(models.Model):
    """Tracks AI content generation for monitoring."""
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='generation_logs'
    )
    model_used = models.CharField(max_length=100, default='mistral-7b')
    prompt_tokens = models.IntegerField(default=0)
    generated_captions = models.JSONField(default=dict, blank=True)
    image_composed = models.BooleanField(default=False)
    duration_ms = models.IntegerField(default=0)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Gen #{self.id} - {self.product.name[:30]}"
