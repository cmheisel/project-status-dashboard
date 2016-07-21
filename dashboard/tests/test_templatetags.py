"""Test our template tags."""

import pytest


@pytest.fixture
def percentage_filter():
    """Return the percentage filter."""
    from ..templatetags.dashboard_tags import percentage
    return percentage


def test_percentage(percentage_filter):
    """Floats come back with 1 place of precision."""

    expected = "22.2%"
    actual = percentage_filter(.2221)
    assert expected == actual
