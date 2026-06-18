"""
URLs for tracker/analytics API endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('overview/', views.AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('clicks/', views.AnalyticsClicksView.as_view(), name='analytics-clicks'),
    path('earnings/', views.AnalyticsEarningsView.as_view(), name='analytics-earnings'),
    path('status/', views.PlatformStatusView.as_view(), name='platform-status'),
    path('caption-performance/', views.CaptionPerformanceView.as_view(), name='analytics-caption-performance'),
    path('test/', views.PlatformTestView.as_view(), name='platform-test'),
]
