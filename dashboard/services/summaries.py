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
