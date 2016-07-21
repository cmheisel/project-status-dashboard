"""Test our template tags."""

from collections import namedtuple

import pytest

from pretend import stub


@pytest.fixture()
def ReportStub():
    """Return a stub for ProjectReport"""
    ReportStub = namedtuple("ReportStub", ['incomplete', 'complete', 'total', 'pct_complete'])
    return ReportStub


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


def test_progress_report_no_previous(progress_report):
    """No previous displays defaults."""
    current_values = dict(
        incomplete=5,
        complete=10,
        total=15,
        pct_complete=10 / 15
    )
    current_report = stub(
        **current_values
    )
    previous_report = None
    expected = {
        'current': current_report,
        'previous': None,
        'scope_change': None,
        'complete_change': None,
    }

    actual = progress_report(current_report, previous_report)
    for key in expected:
        if key == 'current':
            for k, v in current_values.items():
                assert getattr(actual[key], k) == v, "Mismatch on actual[{}].{}".format(key, k)
        else:
            assert actual[key] == expected[key]


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
