"""
Serializers for content/poster app.
"""
from rest_framework import serializers
from apps.poster.models import PostQueue, PostLog


class PostQueueSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.CharField(source='product.image_url', read_only=True)

    class Meta:
        model = PostQueue
        fields = '__all__'


class PostQueueCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    platforms = serializers.ListField(
        child=serializers.CharField(), default=[
            'telegram', 'instagram', 'facebook', 'pinterest', 'twitter'
        ]
    )


class PostLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLog
        fields = '__all__'
