import datetime

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.generic import View, TemplateView

from .services import sheets


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
        sheet_id = settings.GOOGLE_SPREADSHEET_ID
        data = sheets.load_sheet(sheet_id)

        # HACK: Make real
        hack_percents = [5, 33, 25, 90, 87, 30, 0,]
        hack_deltas = [5, -3, 10, -20, -1, -.5, 0, 0, 0]

        context = dict(data=data, percents=hack_percents, deltas=hack_deltas)
        return context
