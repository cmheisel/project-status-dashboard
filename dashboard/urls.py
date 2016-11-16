from django.conf.urls import url

from .views import HealthCheck, Dashboard, Refresh, Forecast

urlpatterns = [
    url(r'^$', Dashboard.as_view(), name="dashboard"),
    url(r'^forecast/(?P<filter_id>[0-9]+)/$', Forecast.as_view(), name="forecast"),
    url(r'^refresh/$', Refresh.as_view(), name="refresh"),
    url(r'^health/$', HealthCheck.as_view(), name="health"),
]
