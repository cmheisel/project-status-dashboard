"""Test dashboard.services.jira."""

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pytest
import requests_mock
import json


@pytest.fixture
def jira():
    """Fixture for JIRA."""
    from ..services import jira
    return jira


def test_setup(jira):
    """Verify our fixture."""
    assert jira


def test_query_url(jira):
    """Verify explicit arg is used for URL."""
    filter_id = "12345"
    jira_url = "https://jira.purnkleen.com"
    expected = "https://jira.purnkleen.com/rest/api/2/search?jql=filter=12345&maxResults=999"
    assert expected == jira.query_url(filter_id, jira_url)


def test_query_url_w_settings(jira, settings):
    """Verify settings used for URL implicitly."""
    filter_id = "12345"
    expected = "https://jira.purnkleen.com/rest/api/2/search?jql=filter=12345&maxResults=999"
    settings.JIRA_URL = "https://jira.purnkleen.com"
    assert expected == jira.query_url(filter_id)


def test_summarize_results(jira, settings):
    """Verify happy path results."""
    settings.JIRA_DONE = ['Donnager']
    issue_list = {
        'total': 3,
        'issues': [
            {'key': 'JIRA-1', 'fields': {'status': {'name': 'In Progress'}}},
            {'key': 'JIRA-2', 'fields': {'status': {'name': 'In Progress'}}},
            {'key': 'JIRA-3', 'fields': {'status': {'name': 'Donnager'}}},
        ]
    }
    expected = {
        'incomplete': 2,
        'complete': 1,
        'pct_complete': 1 / 3.0,
        'total': 3,
        'errors': [],
    }
    assert jira.summarize_results(issue_list) == expected


def test_summarize_results_with_multiple_done_labels_and_whitespace(jira, settings):
    """Verify happy path results when there's multiple JIRA_DONE labels and there's whitespace"""
    settings.JIRA_DONE = ["Abandoned", "Done", "Deployed", "Closed", "Accepted", "Invalid Ticket", "Merged", "Release"]
    issue_list = {
        'total': 7,
        'issues': [
            {'key': "JIRA-1", 'fields': {'status': {'name': 'In Progress'}}},
            {'key': "JIRA-2", 'fields': {'status': {'name': 'In Progress'}}},
            {'key': "JIRA-3", 'fields': {'status': {'name': 'Abandoned'}}},
            {'key': "JIRA-4", 'fields': {'status': {'name': 'Deployed'}}},
            {'key': "JIRA-5", 'fields': {'status': {'name': 'Accepted'}}},
            {'key': "JIRA-6", 'fields': {'status': {'name': 'Invalid Ticket    '}}},
            {'key': "JIRA-7", 'fields': {'status': {'name': 'Foo bar baz'}}},

        ]
    }
    expected = {
        'incomplete': 3,
        'complete': 4,
        'pct_complete': 4 / 7.0,
        'total': 7,
        'errors': [],
    }
    assert jira.summarize_results(issue_list) == expected


def test_summarize_results_with_errors(jira):
    """Pass errors upstream with 0s for values."""
    issue_list = {
        'errorMessages': ["A value with ID '12245' does not exist for the field 'filter'."],
        'errors': {}
    }
    expected = {
        'incomplete': 0,
        'complete': 0,
        'pct_complete': 0,
        'total': 0,
        'errors': [
            "A value with ID '12245' does not exist for the field 'filter'.",
        ]
    }
    assert jira.summarize_results(issue_list) == expected


def test_summarize_results_with_zero_results(jira):
    """Pass 0s upstream for filters with no results."""
    issue_list = {
        'total': 0,
        'issues': []
    }
    expected = {
        'incomplete': 0,
        'complete': 0,
        'pct_complete': 0,
        'total': 0,
        'errors': [],
    }
    assert jira.summarize_results(issue_list) == expected


def test_summarize_query_weird_input(jira):
    """Return None if passed a non-int filter_id."""
    result = jira.summarize_query("FOOBAR")
    assert result == {}


def test_fetch_query_results(settings, jira):
    """Return the results."""
    settings.JIRA_AUTH = ("user", "password")
    expected = dict(foo="bar", baz="bat")
    expected_json = json.dumps(expected)
    with requests_mock.mock() as m:
        m.register_uri(requests_mock.ANY, requests_mock.ANY, text=expected_json)
        result = jira.fetch_query_results(43035)
        assert result == expected


def test_fetch_query_results_with_errors(settings, jira):
    """JIRA responses with error messages should be logged and returned."""
    settings.JIRA_AUTH = ("user", "password")
    expected = dict(
        errors=[],
        errorMessages=["Was a boring conversation anyway... Luke we're gonna have company!", ],
    )
    expected_json = json.dumps(expected)
    with requests_mock.mock() as m:
        with patch("dashboard.services.jira.LOGGER") as mocked_logger:
            m.register_uri(requests_mock.ANY, requests_mock.ANY, text=expected_json)
            result = jira.fetch_query_results(43035, logger=mocked_logger)
            assert mocked_logger.warning.called
            assert result == expected
