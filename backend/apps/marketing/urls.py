"""
URLs for marketing app.
"""
from django.urls import path
from .views import NewsletterSubscribeView, ContactFormView

urlpatterns = [
    path('subscribe/', NewsletterSubscribeView.as_view(), name='marketing-subscribe'),
    path('contact/', ContactFormView.as_view(), name='marketing-contact'),
]
