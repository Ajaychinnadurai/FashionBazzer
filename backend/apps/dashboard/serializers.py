"""
Serializers for dashboard app.
"""
from rest_framework import serializers
from django.db.models import Sum, Count, Avg
from apps.tracker.models import Click, Commission, TrackedLink, PlatformConnection
from apps.products.models import Product
from apps.poster.models import PostQueue, PostLog


class DashboardStatsSerializer(serializers.Serializer):
    total_clicks = serializers.IntegerField()
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_posts = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_conversions = serializers.IntegerField()
    today_clicks = serializers.IntegerField()
    today_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    active_platforms = serializers.IntegerField()


class ClicksByPlatformSerializer(serializers.Serializer):
    platform = serializers.CharField()
    clicks = serializers.IntegerField()
    conversions = serializers.IntegerField()


class EarningsSummarySerializer(serializers.Serializer):
    platform = serializers.CharField()
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending = serializers.DecimalField(max_digits=10, decimal_places=2)
    approved = serializers.DecimalField(max_digits=10, decimal_places=2)
