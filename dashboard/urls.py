from django.conf.urls import url

from .views import HealthCheck, Dashboard, Refresh, History

urlpatterns = [
    url(r'^$', Dashboard.as_view(), name="dashboard"),
    url(r'^history/(?P<filter_id>[0-9]+)/$', History.as_view(), name="history"),
    url(r'^refresh/$', Refresh.as_view(), name="refresh"),
    url(r'^health/$', HealthCheck.as_view(), name="health"),
]
