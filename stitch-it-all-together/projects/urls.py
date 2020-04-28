from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ProjectViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'projects', ProjectViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]