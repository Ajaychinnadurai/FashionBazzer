"""
Serializers for the products app.
"""
from rest_framework import serializers
from .models import Product


class ProductListSerializer(serializers.ModelSerializer):
    discount_display = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'platform', 'original_price', 'sale_price',
            'discount_percent', 'discount_display', 'rating', 'review_count',
            'category', 'product_url', 'affiliate_url', 'image_url',
            'is_trending', 'ai_tagline',
        ]

    def get_discount_display(self, obj):
        return f"{obj.discount_percent}% OFF"


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
