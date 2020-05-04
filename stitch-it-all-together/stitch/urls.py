from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include
from django.conf import settings
from django.contrib.staticfiles.urls import static
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

# Server local media files when in debug mode
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
