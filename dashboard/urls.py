from django.conf.urls import url

from .views import HealthCheck, Dashboard

urlpatterns = [
    url(r'^$', Dashboard.as_view(), name="dashboard"),
    url(r'^health/$', HealthCheck.as_view(), name="health"),
]
