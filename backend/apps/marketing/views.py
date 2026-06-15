"""
Marketing views for FashionBazzer.
Handles newsletter subscriptions, contact form, and marketing page data.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class NewsletterSubscribeView(APIView):
    """
    POST /api/marketing/subscribe/
    Subscribe an email to the FashionBazzer newsletter.
    """

    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log the subscription (extend with Mailchimp/SendGrid/DB in production)
        logger.info(f"Newsletter subscription: {email}")

        return Response({
            'success': True,
            'message': 'Successfully subscribed!',
            'email': email,
        })


class ContactFormView(APIView):
    """
    POST /api/marketing/contact/
    Submit a contact form message.
    """

    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        message = request.data.get('message', '').strip()

        if not all([name, email, message]):
            return Response(
                {'error': 'Name, email, and message are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log the contact (extend with email notification in production)
        logger.info(f"Contact form: {name} <{email}>: {message[:100]}...")

        return Response({
            'success': True,
            'message': 'Message received! We\'ll get back to you soon.',
        })
