"""
Views for the content app.
"""
from rest_framework import generics
from .models import GenerationLog
from .serializers import GenerationLogSerializer


class GenerationLogListView(generics.ListAPIView):
    """List all AI generation logs."""
    queryset = GenerationLog.objects.all()
    serializer_class = GenerationLogSerializer
