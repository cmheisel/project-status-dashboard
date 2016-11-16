"""Database models for dashboard app."""

from django.db import models


class ProjectSummary(models.Model):
    """Summary data about a JIRA filter for a particular date."""

    filter_id = models.IntegerField()
    incomplete = models.IntegerField()
    complete = models.IntegerField()
    total = models.IntegerField()
    created_on = models.DateField()
    updated_at = models.DateTimeField(null=False)

    class Meta:
        verbose_name = "project summary"
        verbose_name_plural = "project summaries"
        unique_together = (("filter_id", "created_on"))
        get_latest_by = "updated_at"

    def __repr__(self):
        return "<ProjectSummary {} filter: {} created_on: {}>".format(self.id, self.filter_id, self.created_on)

    @property
    def pct_complete(self):
        """How complete is the project.

        Returns:
            float: Percentage of the project that is complete.
        """
        if self.total == 0:
            return float(0)
        return self.complete / float(self.total)
