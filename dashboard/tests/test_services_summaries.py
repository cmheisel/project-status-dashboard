"""Test dashboard.services.summaries."""

import pytest
from dateutil.relativedelta import relativedelta


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
def make_one(summaries):
    """Provide an function to make an instance of the CUT"""
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


def test_make_one(make_one):
    """Ensure our maker makes properly."""
    s = make_one(incomplete=3, complete=2, total=5)
    assert s.incomplete == 3
    assert s.complete == 2
    assert s.total == 5


def test_setup(summaries):
    """Ensure we wired the test up."""
    assert summaries


def test_make_summary(summaries):
    """Ensure we can create a summary."""
    data = dict(
        filter_id=6292809552232448,
        incomplete=5,
        complete=10,
        total=15,
    )

    s = summaries.create(**data)

    for key, value in data.items():
        assert getattr(s, key) == value


def test_make_summary_adds_the_date(summaries, datetime):
    """A date is added to the summary when created."""
    data = dict(
        filter_id=6292809552232448,
        incomplete=5,
        complete=10,
        total=15,
    )

    s = summaries.create(**data)
    assert s.created_on == datetime.date.today()


def test_make_summary_honors_date_arg(summaries, datetime):
    """A date arg is honored when passed."""
    yesterday = datetime.date.today() - relativedelta(days=1)
    data = dict(
        filter_id=6292809552232448,
        incomplete=5,
        complete=10,
        total=15,
        created_on=yesterday,
    )
    s = summaries.create(**data)
    assert s.created_on == yesterday


def test_summary_object_provides_pct_complete(make_one):
    """A summary object provides a percent complete."""
    kwargs = dict(
        incomplete=2,
        complete=4,
        total=6
    )
    s = make_one()
    assert s.pct_complete == kwargs['complete'] / float(kwargs['total'])


@pytest.mark.system
@pytest.mark.django_db
def test_store(summaries, make_one):
    """Ensure we can store summary objects."""
    s = make_one()
    s, result = summaries.store(s)
    assert result == summaries.SAVED
    assert s.id


@pytest.mark.system
@pytest.mark.django_db
def test_update(summaries, make_one):
    """Ensure multiple calls to create on the same date return the same obj."""
    s = make_one()
    s, result = summaries.store(s)
    assert result == summaries.SAVED
    assert s.id

    s2 = make_one(incomplete=1, complete=2, total=3)
    s2, result = summaries.store(s2)
    assert result == summaries.UPDATED
    assert s2.id == s.id
    assert (1, 2, 3) == (s2.incomplete, s2.complete, s2.total)
