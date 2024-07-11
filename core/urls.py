# core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500
from .views import custom_404, custom_500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('enroll.urls')),
]

handler404 = custom_404
handler500 = custom_500
