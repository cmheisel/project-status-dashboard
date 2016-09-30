import datetime

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import View, TemplateView

from .jobs import generate_dashboard
from .services import summaries


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
        updated = summaries.latest_update()
        context = dict(data=data, updated=updated)
        return context


class Refresh(View):
    def get(self, request, *args, **kwargs):
        cache.set('dashboard_data', [])
        generate_dashboard.delay()
        return redirect('dashboard')
