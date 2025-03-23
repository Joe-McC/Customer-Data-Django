from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # We will create an api app with its own urls.py
    path('api/', include('api.urls')),
]