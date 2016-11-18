import datetime

from dateutil.relativedelta import relativedelta

from django.core.cache import cache
from django.http import JsonResponse, Http404
from django.shortcuts import redirect
from django.views.generic import View, TemplateView

from .jobs import generate_dashboard
from .services import summaries, predictions


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
        days_ago = 29

        start_date = datetime.date.today() - relativedelta(days=days_ago)
        filter_summaries = summaries.for_date_range(filter_id, start_date)
        if not filter_summaries:
            raise Http404("No filter with id: {}".format(filter_id))

        latest_summary = filter_summaries.last()
        throughputs = predictions.throughput_history(filter_summaries)

        scope = self.request.GET.get('scope', latest_summary.incomplete)
        try:
            scope = int(scope)
        except (TypeError, ValueError):
            scope = latest_summary.incomplete

        try:
            two_week_forecast = predictions.forecast(throughputs, scope)
            two_week_forecast = [latest_summary.created_on + relativedelta(days=int(f)) for f in two_week_forecast]
            forecasts = {days_ago + 1: {'percentiles': two_week_forecast, 'scope': scope, 'actual_scope': latest_summary.incomplete}}
        except ValueError:
            forecasts = {}

        throughputs = [0, ] + throughputs
        recent_history = []
        for i in range(0, len(filter_summaries)):
            summary = filter_summaries[i]
            recent_history.append(
                [summary.created_on, throughputs[i], summary.complete, summary.total, summary.pct_complete]
            )

        context = dict(
            filter_id=filter_id,
            recent_history=recent_history,
            forecasts=forecasts,
            start_date=start_date,
            end_date=latest_summary.created_on
        )
        return context


class Refresh(View):
    def get(self, request, *args, **kwargs):
        cache.set('dashboard_data', [])
        generate_dashboard.delay()
        return redirect('dashboard')
