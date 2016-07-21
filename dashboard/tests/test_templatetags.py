"""Test our template tags."""

import pytest

from pretend import stub


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


@pytest.fixture
def render_template():
    """Provide function for rendering a template string."""
    from django.template import Template, Context

    def _render_template(template_string, context={}):
        return Template(template_string).render(Context(context))

    return _render_template


def test_percentage(percentage_filter):
    """Floats come back with 1 place of precision."""

    expected = "22.2%"
    actual = percentage_filter(.2221)
    assert expected == actual


def test_render_template(render_template):
    """Ensure our fixture does what it says."""
    expected = "Name the ship: Rocinante"

    template = r"""Name the ship: {{ ship_name }}"""
    actual = render_template(template, dict(ship_name="Rocinante"))

    assert expected == actual


def test_progress_report_no_previous(render_template):
    """Check the output of progress_report."""
    current_report = stub(
        incomplete=5,
        complete=10,
        total=15,
        pct_complete=10 / 15
    )
    previous_report = None
    expected = "66.7% (10/15)"

    t = r"""{% load dashboard_tags %}{% progress_report current previous %}"""
    c = dict(current=current_report, previous=previous_report)
    assert render_template(t, c).strip() == expected


def test_progress_report_no_current(render_template):
    """Check the output of progress_report."""
    current_report = ""
    previous_report = ""
    expected = ""

    t = r"""{% load dashboard_tags %}{% progress_report current previous %}"""
    c = dict(current=current_report, previous=previous_report)
    assert render_template(t, c).strip() == expected
