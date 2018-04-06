"""projects URL Configuration."""
from django.conf.urls import url, include
from django.conf import settings

urlpatterns = [
    url(r'^{}'.format(settings.BASE_URL), include('dashboard.urls')),
]
