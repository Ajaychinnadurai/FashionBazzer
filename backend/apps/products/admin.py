"""
Admin configuration for products app.
"""
from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'sale_price', 'rating', 'review_count', 'is_trending', 'created_at']
    list_filter = ['platform', 'category', 'is_trending']
    search_fields = ['name', 'platform']
    ordering = ['-created_at']
    list_per_page = 50
