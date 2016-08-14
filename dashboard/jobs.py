import datetime

from dateutil.relativedelta import relativedelta

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
            if summary_data.get('errors', []):
                row.xtras['jira_summary_errors'] = summary_data['errors']
            elif summary_data:
                p = summaries.create(
                    filter_id=int(row.xtras['_jira_filter']),
                    incomplete=summary_data['incomplete'],
                    complete=summary_data['complete'],
                    total=summary_data['total'],
                    created_on=datetime.date.today(),
                )
                summaries.store(p)
                row.xtras['jira_summary'] = p

                week_ago = p.created_on - relativedelta(days=7)
                week_ago_summary = summaries.for_date(filter_id=p.filter_id, date=week_ago)
                row.xtras['week_ago_summary'] = week_ago_summary
    cache.set('dashboard_data', data, None)
    cache.set('dashboard_data_updated', datetime.datetime.now(get_default_timezone()), None)
    return True
