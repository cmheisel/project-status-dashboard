from django.conf.urls import url

from .views import HealthCheck, Dashboard, Refresh

urlpatterns = [
    url(r'^$', Dashboard.as_view(), name="dashboard"),
    url(r'^refresh$', Refresh.as_view(), name="refresh"),
    url(r'^health/$', HealthCheck.as_view(), name="health"),
]
