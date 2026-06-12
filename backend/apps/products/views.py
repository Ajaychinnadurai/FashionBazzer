"""
Views for the products app.
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for products.
    """
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
        recent = Product.objects.all()[:20]
        serializer = ProductListSerializer(recent, many=True)
        return Response(serializer.data)
