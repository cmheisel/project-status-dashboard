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
    s = make_one(**kwargs)
    assert s.pct_complete == kwargs['complete'] / float(kwargs['total'])


def test_summary_object_provides_pct_complete_with_0_length(make_one):
    """A summary object provides a percent complete."""
    kwargs = dict(
        incomplete=0,
        complete=0,
        total=0
    )
    s = make_one(**kwargs)
    assert s.pct_complete == 0


@pytest.mark.system
@pytest.mark.django_db
def test_fill_updated_at(summaries, make_one):
    """fill_updated_at sets the summaries updated_at to 11:59 pm."""
    s = make_one()
    s.updated_at = None

    expected = (
        s.created_on.year,
        s.created_on.month,
        s.created_on.day,
        23,
        59,
        59,
    )

    s = summaries.fill_updated_at(s)
    actual = (
        s.updated_at.year,
        s.updated_at.month,
        s.updated_at.day,
        s.updated_at.hour,
        s.updated_at.minute,
        s.updated_at.second
    )
    assert expected == actual
    s.save()
    s = summaries.for_date(s.filter_id, s.created_on)
    print(s.updated_at.tzinfo)
    actual = (
        s.updated_at.year,
        s.updated_at.month,
        s.updated_at.day,
        s.updated_at.hour,
        s.updated_at.minute,
        s.updated_at.second
    )
    assert expected == actual


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


@pytest.mark.system
@pytest.mark.django_db
def test_updated_at(summaries, make_one):
    """Ensure updated_at is set."""
    from django.utils import timezone
    s = make_one()
    s, result = summaries.store(s)
    now = timezone.now()
    expected = (now.year, now.month, now.day, now.hour, now.minute, now.second)

    actual = (
        s.updated_at.year,
        s.updated_at.month,
        s.updated_at.day,
        s.updated_at.hour,
        s.updated_at.minute,
        s.updated_at.second
    )
    assert expected == actual


@pytest.mark.system
@pytest.mark.django_db
def test_update_different_filters(summaries, make_one):
    """Ensure multiple calls to create on the same date/diff filter return the same obj."""
    s = make_one(filter_id=1234)
    s, result = summaries.store(s)
    assert result == summaries.SAVED
    assert s.id

    s2 = make_one(filter_id=5678)
    s2, result = summaries.store(s2)
    assert result == summaries.SAVED
    assert s2.id != s.id


@pytest.mark.system
@pytest.mark.django_db
def test_for_date(summaries, make_one, datetime):
    """Ensure we can find summaries from the past."""
    week_ago = datetime.date.today() - relativedelta(days=7)

    s1 = make_one(created_on=week_ago)
    s2 = make_one()

    s1, result = summaries.store(s1)
    s2, result = summaries.store(s2)

    s3 = summaries.for_date(filter_id=s2.filter_id, date=week_ago)
    assert s3.id == s1.id


@pytest.mark.system
@pytest.mark.django_db
def test_for_date_sad(summaries, make_one, datetime):
    """Validate what happens when we can't find summaries from the past."""
    week_ago = datetime.date.today() - relativedelta(days=7)

    s1 = make_one()
    s2 = summaries.for_date(filter_id=s1.filter_id, date=week_ago)
    assert s2 is None


@pytest.mark.system
@pytest.mark.django_db
def test_latest_update(summaries, make_one, datetime):
    """Ensure that summaries.latest_update returns the most recent updated_at."""
    week_ago = datetime.date.today() - relativedelta(days=7)
    s1 = make_one(created_on=week_ago)
    s2 = make_one()

    summaries.store(s1)
    s2, result = summaries.store(s2)

    assert summaries.latest_update() == s2.updated_at


@pytest.mark.system
@pytest.mark.django_db
def test_latest_update_with_no_records(summaries, make_one):
    """Ensure that summaries.latest_update returns None if there are no summaries."""
    assert summaries.latest_update() is None


@pytest.mark.system
@pytest.mark.django_db
def test_for_date_range(summaries, make_one, datetime):
    """Ensure we can find many summaries from the past."""
    week_ago = datetime.date.today() - relativedelta(days=7)

    s1 = make_one(created_on=week_ago)
    s2 = make_one()

    s2, result = summaries.store(s2)
    s1, result = summaries.store(s1)

    past_summaries = summaries.for_date_range(filter_id=s2.filter_id, start_date=week_ago, end_date=s2.created_on)
    assert 2 == len(past_summaries)
    assert past_summaries[0] == s1
    assert past_summaries[1] == s2
