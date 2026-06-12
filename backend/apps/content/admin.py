"""
Admin configuration for content app.
"""
from django.contrib import admin
from .models import GenerationLog


@admin.register(GenerationLog)
class GenerationLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'model_used', 'success', 'duration_ms', 'created_at']
    list_filter = ['success', 'model_used']
    ordering = ['-created_at']
