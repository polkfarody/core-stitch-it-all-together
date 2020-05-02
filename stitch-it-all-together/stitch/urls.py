from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include

from core.views import api_root

# Base URLS
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root),
]

# App urls
urlpatterns += [
    path('api/', include('projects.urls')),
    path('api/', include('stitchers.urls')),
]

# Auth endpoint
urlpatterns += [
    path('api/users/', include('rest_framework.urls')),
]
