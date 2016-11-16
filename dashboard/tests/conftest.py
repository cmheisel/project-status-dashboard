import pytest


@pytest.fixture
def summaries():
    """Get the module under test."""
    from ..services import summaries
    return summaries


@pytest.fixture
def datetime():
    """Provide fixture for datetime."""
    import datetime
    return datetime


@pytest.fixture
def relativedelta():
    """Provide fixture for relativedelta."""
    from dateutil.relativedelta import relativedelta
    return relativedelta


@pytest.fixture
def make_one_summary(summaries):
    """Provide an function to make an instance of the CUT."""
    def _make_one(**kwargs):
        defaults = dict(
            filter_id=6292809552232448,
            incomplete=5,
            complete=10,
            total=15,
        )
        defaults.update(**kwargs)
        s = summaries.create(**defaults)
        return s
    return _make_one
