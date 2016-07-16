import datetime

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import View, TemplateView
from django.utils import timezone

from .jobs import generate_dashboard
from .models import ProjectSummary


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
        try:
            updated = ProjectSummary.objects.latest().updated_at
        except ProjectSummary.DoesNotExist:
            updated = timezone.now()
        context = dict(data=data, updated=updated)
        generate_dashboard.delay()
        return context


class Refresh(View):
    def get(self, request, *args, **kwargs):
        cache.set('dashboard_data', [])
        generate_dashboard.delay()
        return redirect('dashboard')
