from django.db import models


class ProjectSummary(models.Model):
    """Summary data about a JIRA filter for a particular date."""

    filter_id = models.IntegerField()
    incomplete = models.IntegerField()
    complete = models.IntegerField()
    total = models.IntegerField()
    fetched_on = models.DateField()

    @property
    def pct_complete(self):
        return self.complete / float(self.total)
