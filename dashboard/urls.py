from django.conf.urls import url

from .views import HealthCheck

urlpatterns = [
    url(r'^health/$', HealthCheck.as_view(), name="health"),
]
