"""Classes and functions for manipulating and storing summaries."""

import datetime

from ..models import ProjectSummary

SAVED = "saved"
UPDATED = "updated"


def create(filter_id, complete, incomplete, total, created_on=None):
    """Create ProjectSummary instances."""
    if created_on is None:
        created_on = datetime.date.today()

    p = ProjectSummary(
        filter_id=filter_id,
        complete=complete,
        incomplete=incomplete,
        total=total,
        created_on=created_on
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
