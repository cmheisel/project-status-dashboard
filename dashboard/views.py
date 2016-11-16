import datetime

from dateutil.relativedelta import relativedelta

from django.core.cache import cache
from django.http import JsonResponse, Http404
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


class Forecast(TemplateView):
    template_name = "forecast.html"

    def get_context_data(self, filter_id, **kwargs):
        start_date = datetime.date.today() - relativedelta(days=90)
        filter_summaries = summaries.for_date_range(filter_id, start_date)
        if not filter_summaries:
            raise Http404("No filter with id: {}".format(filter_id))

        context = dict(
            filter_id=filter_id,
            filter_summaries=filter_summaries
        )
        return context


class Refresh(View):
    def get(self, request, *args, **kwargs):
        cache.set('dashboard_data', [])
        generate_dashboard.delay()
        return redirect('dashboard')
