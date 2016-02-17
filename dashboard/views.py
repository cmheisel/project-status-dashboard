import datetime

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.generic import View, TemplateView

from .services import sheets, jira


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

        for row in data:
            if row.xtras.get('_jira_filter'):
                row.xtras['jira_summary'] = jira.summarize_query(row.xtras['_jira_filter'])

        context = dict(data=data)
        return context
