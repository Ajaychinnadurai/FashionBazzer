"""
URLs for the poster app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostQueueListView.as_view(), name='post-queue-list'),
    path('generate/', views.GenerateContentAPIView.as_view(), name='generate-content'),
    path('publish-now/', views.PublishNowAPIView.as_view(), name='publish-now'),
]
