import datetime

from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import get_default_timezone

from django_rq import job

from .services import sheets, jira, summaries


@job
def generate_dashboard():
    sheet_id = settings.GOOGLE_SPREADSHEET_ID
    data = sheets.load_sheet(sheet_id)
    for row in data:
        if row.xtras.get('_jira_filter'):
            summary_data = jira.summarize_query(row.xtras['_jira_filter'])
            p = summaries.create(
                filter_id=int(row.xtras['_jira_filter']),
                incomplete=summary_data['incomplete'],
                complete=summary_data['complete'],
                total=summary_data['total'],
                fetched_on=datetime.datetime.today(),
            )
            summaries.store(p)
            row.xtras['jira_summary'] = p
    cache.set('dashboard_data', data, None)
    cache.set('dashboard_data_updated', datetime.datetime.now(get_default_timezone()), None)
    return True
generate_dashboard.delay()
