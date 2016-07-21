"""Test our template tags."""

from collections import namedtuple

import pytest


@pytest.fixture()
def ReportStub():
    """Return a stub for ProjectReport"""
    ReportStub = namedtuple("ReportStub", ['incomplete', 'complete', 'total', 'pct_complete'])
    return ReportStub


@pytest.fixture()
def google_sheet_url():
    """Return the google_sheet_url function."""
    from ..templatetags.dashboard_tags import google_sheet_url
    return google_sheet_url


@pytest.fixture
def percentage_filter():
    """Return the percentage filter."""
    from ..templatetags.dashboard_tags import percentage
    return percentage


@pytest.fixture
def progress_report():
    """Return the progress_report tag."""
    from ..templatetags.dashboard_tags import progress_report
    return progress_report


def test_percentage(percentage_filter):
    """Floats come back with 1 place of precision."""

    expected = "22.2%"
    actual = percentage_filter(.2221)
    assert expected == actual


def test_progress_report_no_current(progress_report):
    """No previous displays defaults."""
    current_report = None
    previous_report = None
    expected = {
        'current': None,
        'previous': None,
        'scope_change': None,
        'complete_change': None,
    }

    actual = progress_report(current_report, previous_report)
    assert actual == expected


def test_progress_report_no_previous(progress_report, ReportStub):
    """No previous displays defaults."""
    current_report = ReportStub(
        incomplete=5,
        complete=10,
        total=15,
        pct_complete=10 / 15
    )
    previous_report = None
    expected = {
        'current': current_report,
        'previous': None,
        'scope_change': None,
        'complete_change': None,
    }

    assert expected == progress_report(current_report, previous_report)


def test_progress_report_current_and_previous(progress_report, ReportStub):
    """Prevous and current return the enhanced display."""
    current_report = ReportStub(
        incomplete=5,
        complete=10,
        total=15,
        pct_complete=10 / 15
    )
    previous_report = ReportStub(
        incomplete=20,
        complete=10,
        total=30,
        pct_complete=10 / 30
    )

    expected = {
        'current': current_report,
        'previous': previous_report,
        'scope_change': 'down',
        'complete_change': 'up'
    }

    assert expected == progress_report(current_report, previous_report)


def test_google_sheet_url(settings, google_sheet_url):
    """Check the URL returned is proper."""
    settings.GOOGLE_SPREADSHEET_ID = "TESTMCTESTTEST"

    expected = """https://docs.google.com/spreadsheets/d/{}/edit#gid=0""".format(settings.GOOGLE_SPREADSHEET_ID)
    assert expected == google_sheet_url()
