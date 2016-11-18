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

    def find_summaries_or_404(self, filter_id):
        self.filter_summaries = summaries.for_date_range(filter_id, self.start_date)
        if not self.filter_summaries:
            raise Http404("No filter with id: {}".format(filter_id))
        self.latest_summary = self.filter_summaries.last()

    @property
    def days_ago(self):
        try:
            days_ago = int(self.request.GET.get('days_ago', 30))
        except ValueError:
            days_ago = 30
        return days_ago

    @property
    def start_date(self):
        return datetime.date.today() - relativedelta(days=self.days_ago)

    @property
    def scope(self):
        try:
            scope = int(self.request.GET.get('scope', ''))
        except (TypeError, ValueError):
            scope = self.latest_summary.incomplete
        return scope

    def _generate_forecast(self):
        throughputs = predictions.throughput_history(self.filter_summaries)

        try:
            forecast = predictions.forecast(throughputs, self.scope)
            forecast = [self.latest_summary.created_on + relativedelta(days=int(f)) for f in forecast]
            forecasts = {self.days_ago: {'percentiles': forecast, 'scope': self.scope, 'actual_scope': self.latest_summary.incomplete}}
        except ValueError:
            forecasts = {}
        return ([0, ] + throughputs, forecasts)

    def _make_recent_history_table(self, throughputs):
        recent_history = []
        for i in range(0, len(self.filter_summaries)):
            summary = self.filter_summaries[i]
            recent_history.append(
                [summary.created_on, throughputs[i], summary.complete, summary.total, summary.pct_complete]
            )
        return recent_history

    def get_context_data(self, filter_id, **kwargs):
        self.find_summaries_or_404(filter_id)

        throughputs, forecasts = self._generate_forecast()
        recent_history = self._make_recent_history_table(throughputs)

        context = dict(
            filter_id=filter_id,
            recent_history=recent_history,
            forecasts=forecasts,
            start_date=self.start_date,
            end_date=self.latest_summary.created_on
        )
        return context


class Refresh(View):
    def get(self, request, *args, **kwargs):
        cache.set('dashboard_data', [])
        generate_dashboard.delay()
        return redirect('dashboard')
