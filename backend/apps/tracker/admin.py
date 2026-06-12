"""
Admin configuration for tracker app.
"""
from django.contrib import admin
from .models import TrackedLink, Click, Commission, PlatformConnection


@admin.register(TrackedLink)
class TrackedLinkAdmin(admin.ModelAdmin):
    list_display = ['short_code', 'product', 'platform', 'click_count', 'created_at']
    list_filter = ['platform']
    search_fields = ['short_code', 'product__name']
    ordering = ['-click_count']


@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ['link', 'clicked_at', 'ip_address']
    ordering = ['-clicked_at']
    list_per_page = 100


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['product', 'affiliate_platform', 'amount', 'status', 'recorded_at']
    list_filter = ['status', 'affiliate_platform']
    ordering = ['-recorded_at']


@admin.register(PlatformConnection)
class PlatformConnectionAdmin(admin.ModelAdmin):
    list_display = ['platform', 'is_connected', 'last_checked', 'posts_today']
    list_filter = ['is_connected']
