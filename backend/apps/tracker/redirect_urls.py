"""
Redirect URL patterns for click tracking.
The /r/<short_code> pattern tracks clicks and redirects to affiliate URL.
"""
from django.urls import path, re_path
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.http import Http404
from django.db import transaction
from .models import TrackedLink, Click


class LinkRedirectView(View):
    """
    Handle /r/<short_code> redirects.
    Records the click before redirecting to the affiliate URL.
    """

    def get(self, request, short_code):
        link = get_object_or_404(TrackedLink, short_code=short_code)

        # Increment click count atomically
        with transaction.atomic():
            TrackedLink.objects.filter(id=link.id).update(
                click_count=link.click_count + 1
            )

        # Record click event
        Click.objects.create(
            link=link,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            referrer=request.META.get('HTTP_REFERER', '')[:500],
        )

        # Redirect to affiliate URL
        affiliate_url = link.affiliate_url
        return redirect(affiliate_url)

    def _get_client_ip(self, request):
        """Extract client IP from request headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


urlpatterns = [
    path('<slug:short_code>/', LinkRedirectView.as_view(), name='link-redirect'),
]
