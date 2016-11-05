"""Classes and functions for manipulating and storing summaries."""

import datetime

from django.utils import timezone

from ..models import ProjectSummary

SAVED = "saved"
UPDATED = "updated"


def fill_updated_at(summary):
    """Set updated_at to created_on at 11:59 pm UTC"""
    summary.updated_at = timezone.now().replace(
        year=summary.created_on.year,
        month=summary.created_on.month,
        day=summary.created_on.day,
        hour=23,
        minute=59,
        second=59,
    )
    return summary


def create(filter_id, complete, incomplete, total, created_on=None):
    """Create ProjectSummary instances."""
    if created_on is None:
        created_on = datetime.date.today()

    p = ProjectSummary(
        filter_id=filter_id,
        complete=complete,
        incomplete=incomplete,
        total=total,
        created_on=created_on,
        updated_at=timezone.now()
    )
    return p


def store(summary_obj):
    """Store the summary_obj in the database.

    Args:
        summary_obj (ProjectSummary): The ProjectSummary instance to store
    Returns:
        str: One of summaries.SAVED or summaries.UPDATED
    """
    updated_values = dict(
        complete=summary_obj.complete,
        incomplete=summary_obj.incomplete,
        total=summary_obj.total,
        updated_at=timezone.now()
    )

    obj, created = ProjectSummary.objects.update_or_create(
        filter_id=summary_obj.filter_id,
        created_on=summary_obj.created_on,
        defaults=updated_values
    )

    result = UPDATED
    if created:
        result = SAVED

    return obj, result


def for_date(filter_id, date):
    """Find a summary with a given filter_id and date.

    Args:
        filter_id (int): The filter_id for the project in question.
        date (Date): The date you want a summary for

    Returns:
        None: If no summary is found
        ProjectSummary: instance that matches the date/filter combo
    """
    try:
        return ProjectSummary.objects.get(filter_id=filter_id, created_on=date)
    except ProjectSummary.DoesNotExist:
        return None


def for_date_range(filter_id, start_date, end_date=None):
    """Find all the summaries for a given filter_id and a date range.
    Args:
        filter_id (int): The filter_id for the project in question.
        start_date (Date): The start of the range you want summaries for
        end_date (Date[today]): The end of the range you want summaries for, default: today
    Returns:
        List[ProjectSummary]: 0 or more project summaries for that filter in the range
    """
    if end_date is None:
        end_date = datetime.date.today()
    return ProjectSummary.objects.filter(
        created_on__gte=start_date,
        created_on__lte=end_date,
    ).order_by('created_on')


def latest_update():
    """Retun the most recent datetime of summary updates.

    Returns:
        datetime: When the most recent ProjectSummary was updated.
    """
    try:
        return ProjectSummary.objects.latest().updated_at
    except ProjectSummary.DoesNotExist:
        return None
