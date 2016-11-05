import datetime
import logging

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import get_default_timezone

from django_rq import job

from .services import sheets, jira, summaries, predictions


@job
def generate_dashboard():
    logger = logging.getLogger("dashboard.jobs.generate_dashboard")
    logger.info("Start")
    sheet_id = settings.GOOGLE_SPREADSHEET_ID
    data = sheets.load_sheet(sheet_id)
    logger.debug("Sheet loaded")
    for row in data:
        if row.xtras.get('_jira_filter'):
            summary_data = jira.summarize_query(row.xtras['_jira_filter'])
            logger.debug("Filter {} summarized".format(row.xtras['_jira_filter']))
            if summary_data.get('errors', []):
                row.xtras['jira_summary_errors'] = summary_data['errors']
                logger.warn("Filter {} summary error".format(summary_data['errors']))
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
                logger.debug("Filter {} summary stored".format(p.filter_id))

                week_ago = p.created_on - relativedelta(days=7)
                two_weeks_ago = p.created_on - relativedelta(days=14)
                week_ago_summary = summaries.for_date(filter_id=p.filter_id, date=week_ago)
                row.xtras['week_ago_summary'] = week_ago_summary
                logger.debug("week_ago filter {} summary retrieved".format(p.filter_id))
                row.xtras['predictions'] = predictions.for_project(filter_id=p.filter_id, backlog_size=p.incomplete, start_date=two_weeks_ago)
                logger.debug("filter {} predictions created".format(p.filter_id))
    cache.set('dashboard_data', data, None)
    cache.set('dashboard_data_updated', datetime.datetime.now(get_default_timezone()), None)
    logger.info("End")
    return True
