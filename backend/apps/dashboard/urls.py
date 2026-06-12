"""
URLs for dashboard API.
"""
from django.urls import path
from .views import DashboardView, SeedDataView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('overview/', DashboardView.as_view(), name='dashboard-overview'),
    path('seed/', SeedDataView.as_view(), name='dashboard-seed'),
]
