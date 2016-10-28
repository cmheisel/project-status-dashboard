"""Test dashboard.services.summaries."""

import pytest


def test_batman():
    assert True


@pytest.fixture
def predictions():
    from dashboard.services import predictions
    return predictions


@pytest.fixture
def summaries():
    from dashboard.services import summaries
    return summaries


@pytest.fixture
def make_summary(summaries):
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


@pytest.fixture
def make_summaries(make_summary):
    def _make_summaries(start, step, skip_modulo):
        daily_values = []
        summaries = []
        for day in range(0, start):
            try:
                yesterday = daily_values[-1]
            except IndexError:
                yesterday = (start, 0)

            if day % skip_modulo == 0:
                today = yesterday
            else:
                assert (yesterday[0]-step + yesterday[1]+step) == start
                today = (yesterday[0]-step, yesterday[1]+step)
            daily_values.append(today)
            summaries.append(make_summary(
                filter_id=123456789,
                incomplete=today[0],
                complete=today[1],
                total=today[0]+today[1]
            ))
        return summaries
    return _make_summaries


def test_make_summaries(make_summaries):
    expected_values = [
        (10, 0),  # 0
        (9, 1),   # 1
        (8, 2),   # 2
        (8, 2),   # 3
        (7, 3),   # 4
        (6, 4),   # 5
        (6, 4),   # 6
        (5, 5),   # 7
        (4, 6),   # 8
        (4, 6),   # 9
    ]

    backlog_start = 10
    zero_work_modulo = 3
    step = 1
    summaries = make_summaries(backlog_start, step, zero_work_modulo)
    actual = [(s.incomplete, s.complete) for s in summaries]
    assert expected_values == actual
