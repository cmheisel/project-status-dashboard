"""Process the context."""

from django.conf import settings


def jira_url(request):
    """Return the JIRA_URL."""
    return {'JIRA_URL': settings.JIRA_URL}
