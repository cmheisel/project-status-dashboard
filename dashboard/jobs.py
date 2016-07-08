import datetime

from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import get_default_timezone

from django_rq import job

from .services import sheets, jira


@job
def dashboard_data_fetch():
    sheet_id = settings.GOOGLE_SPREADSHEET_ID
    data = sheets.load_sheet(sheet_id)

    for row in data:
        if row.xtras.get('_jira_filter'):
            row.xtras['jira_summary'] = jira.summarize_query(row.xtras['_jira_filter'])

    cache.set('dashboard_data', data, None)
    cache.set('dashboard_data_updated', datetime.datetime.now(get_default_timezone()), None)
    return True

dashboard_data_fetch.delay()
