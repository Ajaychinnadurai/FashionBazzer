"""
Views for the products app.
"""
import logging

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer
from apps.poster.models import PostQueue

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for products.
    Read-only by default. Use POST /api/products/create-sample/ to populate sample data.
    """
    queryset = Product.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'category', 'platform']
    ordering_fields = ['created_at', 'sale_price', 'rating', 'review_count']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    @action(detail=False, methods=['post'])
    def create_sample(self, request):
        """
        POST /api/products/create-sample/
        Creates sample fashion products and queues them for posting.
        Safe: only creates predefined products, no user-supplied data.
        """
        from apps.dashboard.views import _create_sample_products
        from apps.content.ai_generator import ContentGenerator

        try:
            created = _create_sample_products()
        except Exception as e:
            logger.error(f"Sample product creation failed: {e}")
            return Response({'error': str(e)}, status=500)

        content_gen = 0
        if created > 0:
            try:
                from apps.content.ai_generator import ContentGenerator
                generator = ContentGenerator()
                # Step 1: Set fallback taglines FIRST (fast, no HuggingFace API)
                FALLBACK_TAGLINES = [
                    "💖 This piece is giving main character energy! 🔥",
                    "✨ Your new closet obsession has arrived! 💫",
                    "💃 Slay every moment in this stunning piece! 🔥",
                    "🌸 Obsessed is an understatement! Get this look ✨",
                    "⭐ Pure perfection — and we totally get why! 💕",
                    "🎯 The fit everyone's been asking about! 💥",
                    "🌟 Affordable luxury at its finest! 💎",
                    "🔥 Manifesting good vibes in this gorgeous piece 💖",
                    "💸 Chic, classy, and totally unreal! 🎉",
                    "👗 Your wardrobe called — it needs this stunner! ✨",
                    "✨ The definition of style and comfort! 💫",
                    "🌸 Wear your confidence today! 💪",
                    "🎀 Twirl-worthy and totally YOU! 💕",
                    "🌟 Upgrade your style game instantly! 🔥",
                    "💖 Ready to turn heads wherever you go! 👀",
                ]
                import random
                for product in Product.objects.filter(ai_tagline=''):
                    product.ai_tagline = random.choice(FALLBACK_TAGLINES)
                    product.save(update_fields=['ai_tagline'])
                # Step 2: Queue posts via generate_for_product with force_regenerate=False
                # (skips HF API since ai_tagline is already set)
                for product in Product.objects.all():
                    post = generator.generate_for_product(product, force_regenerate=False)
                    if post:
                        content_gen += 1
            except Exception as e:
                logger.error(f"Content generation after sample creation failed: {e}")

        return Response({
            'products_created': created,
            'content_generated': content_gen,
            'total_products': Product.objects.count(),
            'total_queue': PostQueue.objects.count(),
        })

    @action(detail=False)
    def trending(self, request):
        """Return top 10 trending products."""
        trending = Product.objects.filter(is_trending=True)[:10]
        serializer = ProductListSerializer(trending, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def recent(self, request):
        """Return most recently scraped products."""
        recent = Product.objects.all()[:20]
        serializer = ProductListSerializer(recent, many=True)
        return Response(serializer.data)
