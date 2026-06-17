"""
Views for managing post queue and content generation.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import PostQueue
from apps.content.serializers import PostQueueSerializer, PostQueueCreateSerializer
from apps.content.ai_generator import ContentGenerator


class PostQueueListView(generics.ListAPIView):
    """List all queued posts."""
    queryset = PostQueue.objects.all()
    serializer_class = PostQueueSerializer


class GenerateContentAPIView(APIView):
    """Manually trigger content generation for pending products."""

    def post(self, request):
        serializer = PostQueueCreateSerializer(data=request.data)
        if serializer.is_valid():
            generator = ContentGenerator()
            product_id = serializer.validated_data['product_id']
            result = generator.generate_for_product(product_id)
            if result:
                response_serializer = PostQueueSerializer(result)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return Response({'error': 'Failed to generate content'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublishNowAPIView(APIView):
    """Force publish a queued post immediately."""

    def post(self, request):
        post_id = request.data.get('post_id')
        if not post_id:
            return Response(
                {'error': 'post_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            post = PostQueue.objects.get(id=post_id, status='pending')
        except PostQueue.DoesNotExist:
            return Response(
                {'error': 'Post not found or already published'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Publish to all platforms
        from .scheduler import publish_post_to_all
        success = publish_post_to_all(post)
        if success:
            return Response({'status': 'published'})
        return Response({'error': 'Publishing failed'}, status=500)
