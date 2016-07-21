"""Test our template tags."""

import pytest


@pytest.fixture
def percentage_filter():
    """Return the percentage filter."""
    from ..templatetags.dashboard_tags import percentage
    return percentage


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
