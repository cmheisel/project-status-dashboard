import datetime
import time

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.generic import View, TemplateView

from .jobs import dashboard_data_fetch

class HealthCheck(View):
    def get(self, request, *args, **kwargs):
        last_access = cache.get('health_access', None)
        content = {
            'health': 'ok',
            'last_access': last_access,
        }
        cache.set('health_access', datetime.datetime.now(), 60)
        return JsonResponse(content)


class Dashboard(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        data = cache.get('dashboard_data', [])
        updated = cache.get('dashboard_data_updated', None)
        job = dashboard_data_fetch.delay()
        if not data:
            while job.result is not True:
                time.sleep(1)
        context = dict(data=data, updated=updated)
        return context
