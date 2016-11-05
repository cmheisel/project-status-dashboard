"""Test dashboard.services.summaries."""
import datetime

import pytest

from dateutil.relativedelta import relativedelta


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
    """Provide an function to make an instance of a summary."""
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
    """Verify our fixture maker works as expected."""
    expected_values = [
        (10, 0),  # 0
        (9, 1),   # 1 - 1
        (8, 2),   # 2 - 1
        (8, 2),   # 3 - 0
        (7, 3),   # 4 - 1
        (6, 4),   # 5 - 1
        (6, 4),   # 6 - 0
        (5, 5),   # 7 - 1
        (4, 6),   # 8 - 1
        (4, 6),   # 9 - 0
    ]

    backlog_start = 10
    zero_work_modulo = 3
    step = 1
    summaries = make_summaries(backlog_start, step, zero_work_modulo)
    actual = [(s.incomplete, s.complete) for s in summaries]
    assert expected_values == actual


def test_throughput_history(predictions, make_summaries):
    backlog_start = 10
    zero_work_modulo = 3
    step = 1
    summaries = make_summaries(backlog_start, step, zero_work_modulo)

    expected_throughput_history = [1, 1, 0, 1, 1, 0, 1, 1, 0]

    assert expected_throughput_history == predictions.throughput_history(summaries)


def test_throughput_history_negative(predictions, make_summary):
    s1 = make_summary(complete=0, incomplete=5, total=5)
    s2 = make_summary(complete=3, incomplete=2, total=5)
    s3 = make_summary(complete=2, incomplete=2, total=4)

    assert [3, 0] == predictions.throughput_history([s1, s2, s3])


def test_predict(predictions):
    throughput_history = [1, 1, 0, 1, 1, 0, 1, 1, 0]
    assert [15, 17, 19] == predictions.forecast(throughput_history, 10, seed=1)


def test_for_project(predictions, monkeypatch, make_summaries):
    backlog_start = 10

    def _mock_for_date_range(filter_id, start_date):
        zero_work_modulo = 3
        step = 1
        summaries = make_summaries(backlog_start, step, zero_work_modulo)
        return summaries
    monkeypatch.setattr(predictions, "for_date_range", _mock_for_date_range)

    start_date = datetime.date.today() - relativedelta(days=14)

    assert [15, 17, 19] == predictions.for_project(1111, 10, start_date)
