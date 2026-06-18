"""
Views for the products app.
"""
import logging

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for products.
    Read-only. Requires authentication.
    All products are from real e-commerce scrapes only — no sample/dummy data.
    """
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'category', 'platform']
    ordering_fields = ['created_at', 'sale_price', 'rating', 'review_count']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    @action(detail=False)
    def trending(self, request):
        """Return top 10 trending products."""
        trending = Product.objects.filter(is_trending=True)[:10]
        serializer = ProductListSerializer(trending, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def recent(self, request):
        """Return most recently scraped products."""
        recent = Product.objects.all().order_by('-created_at')[:20]
        serializer = ProductListSerializer(recent, many=True)
        return Response(serializer.data)
