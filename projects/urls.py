"""projects URL Configuration."""
from django.conf.urls import url, include
from django.conf import settings

urlpatterns = [
    url(r'^', include('dashboard.urls')),
]
