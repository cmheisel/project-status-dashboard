import pytest


@pytest.fixture
def jira():
    from ..services import jira
    return jira


def test_setup(jira):
    assert jira


def test_query_url(jira):
    filter_id = "12345"
    jira_url = "https://jira.purnkleen.com"
    expected = "https://jira.purnkleen.com/rest/api/2/search?jql=filter=12345&maxResults=999"
    assert expected == jira.query_url(filter_id, jira_url)


def test_query_url_w_settings(jira, settings):
    filter_id = "12345"
    expected = "https://jira.purnkleen.com/rest/api/2/search?jql=filter=12345&maxResults=999"
    settings.JIRA_URL = "https://jira.purnkleen.com"
    assert expected == jira.query_url(filter_id)


def test_summarize_results(jira, settings):
    settings.JIRA_DONE = ['Donnager']
    issue_list = {
        'total': 3,
        'issues': [
            {'fields': {'status': {'name': 'In Progress'}}},
            {'fields': {'status': {'name': 'In Progress'}}},
            {'fields': {'status': {'name': 'Donnager'}}},
        ]
    }
    expected = {
        'incomplete': 2,
        'complete': 1,
        'pct_complete': 1 / 3.0,
        'total': 3,
    }
    assert jira.summarize_results(issue_list) == expected
