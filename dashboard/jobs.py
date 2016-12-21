import datetime
import logging

from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import get_default_timezone

from django_rq import job

from .services import sheets, jira, summaries, predictions


def _add_current_jira_summary(xtras, jira_filter_id, logger):
    summary_data = jira.summarize_query(jira_filter_id)
    logger.debug("Filter {} summarized".format(jira_filter_id))
    if summary_data.get('errors', []):
        xtras['jira_summary_errors'] = summary_data['errors']
        logger.warn("Filter {} summary error".format(summary_data['errors']))
    elif summary_data:
        p = summaries.create(
            filter_id=int(xtras['_jira_filter']),
            incomplete=summary_data['incomplete'],
            complete=summary_data['complete'],
            total=summary_data['total'],
            created_on=datetime.date.today(),
        )
        summaries.store(p)
        xtras['jira_summary'] = p
        logger.debug("Filter {} summary stored".format(p.filter_id))
    return xtras


def _add_week_ago_summary(xtras, current_summary, logger):
    week_ago = current_summary.created_on - relativedelta(days=7)
    week_ago_summary = summaries.for_date(filter_id=current_summary.filter_id, date=week_ago)
    xtras['week_ago_summary'] = week_ago_summary
    logger.info("Filter {} week_ago summary retrieved".format(current_summary.filter_id))
    return xtras


def _add_forecasts(xtras, summary, logger):
    a_month_ago = summary.created_on - relativedelta(days=30)
    try:
        forecasts = predictions.for_project(filter_id=summary.filter_id, backlog_size=summary.incomplete, start_date=a_month_ago)
    except ValueError as e:
        forecasts = []
        logger.warn("Filter {} predictions error: {}".format(summary.filter_id, str(e)))

    xtras['predictions'] = [summary.created_on + relativedelta(days=int(f)) for f in forecasts]
    logger.debug("Filter {} predictions created".format(summary.filter_id))
    return xtras


def _add_target_date(xtras, target_date_string):
    xtras['target_date'] = ""
    try:
        xtras['target_date'] = parse(target_date_string)
    except (ValueError, AttributeError):
        pass
    return xtras


@job
def generate_dashboard():
    logger = logging.getLogger("dashboard.jobs.generate_dashboard")
    logger.info("Start")
    sheet_id = settings.GOOGLE_SPREADSHEET_ID
    data = sheets.load_sheet(sheet_id)
    logger.debug("Sheet loaded")
    for row in data:
        row.xtras = _add_target_date(row.xtras, row.xtras.get('_target_date'))
        if row.xtras.get('_jira_filter'):
            row.xtras = _add_current_jira_summary(row.xtras, row.xtras['_jira_filter'], logger)
        if row.xtras.get('jira_summary'):
            row.xtras = _add_week_ago_summary(row.xtras, row.xtras['jira_summary'], logger)
            row.xtras = _add_forecasts(row.xtras, row.xtras['jira_summary'], logger)
    cache.set('dashboard_data', data, None)
    cache.set('dashboard_data_updated', datetime.datetime.now(get_default_timezone()), None)
    logger.info("End")
    return True
