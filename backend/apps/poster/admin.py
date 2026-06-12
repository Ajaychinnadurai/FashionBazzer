"""
Admin configuration for poster app.
"""
from django.contrib import admin
from .models import PostQueue, PostLog


@admin.register(PostQueue)
class PostQueueAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'status', 'scheduled_time', 'published_at', 'created_at']
    list_filter = ['status', 'caption_style']
    search_fields = ['product__name']
    ordering = ['-created_at']


@admin.register(PostLog)
class PostLogAdmin(admin.ModelAdmin):
    list_display = ['post', 'platform', 'status', 'posted_at']
    list_filter = ['platform', 'status']
    ordering = ['-posted_at']
