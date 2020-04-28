from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include

from stitch.views import api_root

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root),
    path('api/', include('projects.urls')),
    path('api/', include('stitchers.urls')),
]

# Auth endpoint
urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]