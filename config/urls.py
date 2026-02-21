"""URL configuration for terminal teacher project."""
from django.urls import path, include

urlpatterns = [
    path('', include('commands.urls')),
]
