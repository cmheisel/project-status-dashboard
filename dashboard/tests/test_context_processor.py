"""Test context processors."""


def test_jira_url(settings):
    """Ensure the JIRA_URL is added to the context."""
    from dashboard.context_processors import jira_url

    expected = "http://foo.example.com"
    settings.JIRA_URL = expected

    assert jira_url(object()) == {'JIRA_URL': expected}
