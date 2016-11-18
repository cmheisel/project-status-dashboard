from django.http import Http404

import pytest


@pytest.fixture
def views():
    from dashboard import views
    return views


@pytest.mark.system
def test_health(rf, views):
    request = rf.get('/health/')
    response = views.HealthCheck().get(request)
    assert response.status_code == 200


@pytest.mark.sytesm
def test_refresh(rf, views, monkeypatch, mocker):
    mock_cache = mocker.Mock()
    mock_generate_dashboard = mocker.Mock()
    monkeypatch.setattr(views, 'cache', mock_cache)
    monkeypatch.setattr(views, 'generate_dashboard', mock_generate_dashboard)

    request = rf.get('/refresh/')
    response = views.Refresh().get(request)

    assert mock_cache.set.called_with('dashboard_data', [])
    assert mock_generate_dashboard.delay.call_count == 1
    assert response.status_code == 302


@pytest.mark.django_db
@pytest.mark.system
def test_dashboard(rf, views):
    request = rf.get('/')
    response = views.Dashboard.as_view()(request)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.system
def test_history_bad_url(client):
    response = client.get('/forecast/123456/')
    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.system
def test_history_with_bad_filter_id(rf, views):
    request = rf.get('/forecast/123456/')
    with pytest.raises(Http404):
        views.Forecast.as_view()(request, filter_id=123456)


@pytest.mark.django_db
@pytest.fixture
def make_predictable_summaries(make_one_summary, summaries, relativedelta, datetime):
    def _make_predictable_summaries(scope, days, filter_id, decrement=1):
        incomplete = scope
        complete = 0
        total = incomplete + complete
        for i in reversed(range(0, days)):
            s = make_one_summary(filter_id=filter_id, created_on=datetime.date.today() - relativedelta(days=i), incomplete=incomplete, complete=complete, total=total)
            summaries.store(s)
            incomplete = incomplete - decrement
            complete = complete + decrement
            total = incomplete + complete
    return _make_predictable_summaries


@pytest.mark.django_db
@pytest.mark.system
def test_forecast_with_good_filter_id(rf, views, make_predictable_summaries, datetime, relativedelta):
    make_predictable_summaries(4, 4, 78910)

    request = rf.get('/forecast/78910/')
    response = views.Forecast.as_view()(request, filter_id=78910)
    assert response.status_code == 200

    recent_history = [
        [datetime.date.today() - relativedelta(days=3), 0, 0, 4, 0.0],
        [datetime.date.today() - relativedelta(days=2), 1, 1, 4, 0.25],
        [datetime.date.today() - relativedelta(days=1), 1, 2, 4, 0.5],
        [datetime.date.today() - relativedelta(days=0), 1, 3, 4, 0.75],
    ]

    expected_percentile_end_date = datetime.date.today() + relativedelta(days=1)

    expected_context = {
        "filter_id": 78910,
        "forecasts": {
            30: {'percentiles': [expected_percentile_end_date, expected_percentile_end_date, expected_percentile_end_date], 'scope': 1, 'actual_scope': 1},
        },
        "recent_history": recent_history,
        "start_date": datetime.date.today() - relativedelta(days=30),
        "end_date": datetime.date.today() - relativedelta(days=0),
    }

    actual_context = response.context_data
    assert actual_context.keys() == expected_context.keys()
    for key, value in expected_context.items():
        assert actual_context[key] == expected_context[key], "Key: {}".format(key)


@pytest.mark.django_db
@pytest.mark.system
def test_forecast_with_little_to_no_throughput(views, rf, make_predictable_summaries, datetime, relativedelta):
    make_predictable_summaries(4, 4, 888888, decrement=0)

    recent_history = [
        [datetime.date.today() - relativedelta(days=3), 0, 0, 4, 0.0],
        [datetime.date.today() - relativedelta(days=2), 0, 0, 4, 0.0],
        [datetime.date.today() - relativedelta(days=1), 0, 0, 4, 0.0],
        [datetime.date.today() - relativedelta(days=0), 0, 0, 4, 0.0],
    ]

    expected_context = {
        "filter_id": 888888,
        "forecasts": {},
        "recent_history": recent_history,
        "start_date": datetime.date.today() - relativedelta(days=30),
        "end_date": datetime.date.today(),
    }

    request = rf.get('/forecast/888888/')
    view = views.Forecast.as_view()
    response = view(request, filter_id=888888)
    actual_context = response.context_data

    assert actual_context.keys() == expected_context.keys()
    for key, value in expected_context.items():
        assert actual_context[key] == expected_context[key], "Key: {}".format(key)


@pytest.mark.django_db
@pytest.mark.system
def test_forecast_with_no_scope(views, rf, make_predictable_summaries, datetime, relativedelta):
    make_predictable_summaries(0, 4, 999999, decrement=0)

    recent_history = [
        [datetime.date.today() - relativedelta(days=3), 0, 0, 0, 0.0],
        [datetime.date.today() - relativedelta(days=2), 0, 0, 0, 0.0],
        [datetime.date.today() - relativedelta(days=1), 0, 0, 0, 0.0],
        [datetime.date.today() - relativedelta(days=0), 0, 0, 0, 0.0],
    ]

    expected_context = {
        "filter_id": 999999,
        "forecasts": {},
        "recent_history": recent_history,
        "start_date": datetime.date.today() - relativedelta(days=30),
        "end_date": datetime.date.today(),
    }

    request = rf.get('/forecast/999999/')
    view = views.Forecast.as_view()
    response = view(request, filter_id=999999)
    actual_context = response.context_data

    assert actual_context.keys() == expected_context.keys()
    for key, value in expected_context.items():
        assert actual_context[key] == expected_context[key], "Key: {}".format(key)


@pytest.mark.django_db
@pytest.mark.system
def test_forecast_with_lotsa_history(views, rf, make_predictable_summaries, datetime, relativedelta):
    make_predictable_summaries(100, 10, 999999, decrement=1)

    recent_history = [
        [datetime.date.today() - relativedelta(days=9), 0, 0, 100, 0.0],
        [datetime.date.today() - relativedelta(days=8), 1, 1, 100, 0.01],
        [datetime.date.today() - relativedelta(days=7), 1, 2, 100, 0.02],
        [datetime.date.today() - relativedelta(days=6), 1, 3, 100, 0.03],
        [datetime.date.today() - relativedelta(days=5), 1, 4, 100, 0.04],
        [datetime.date.today() - relativedelta(days=4), 1, 5, 100, 0.05],
        [datetime.date.today() - relativedelta(days=3), 1, 6, 100, 0.06],
        [datetime.date.today() - relativedelta(days=2), 1, 7, 100, 0.07],
        [datetime.date.today() - relativedelta(days=1), 1, 8, 100, 0.08],
        [datetime.date.today() - relativedelta(days=0), 1, 9, 100, 0.09],
    ]

    expected_context = {
        "filter_id": 999999,
        "forecasts": {30: {
            'scope': 91,
            'actual_scope': 91,
            'percentiles': [
                datetime.date.today() + relativedelta(days=91),
                datetime.date.today() + relativedelta(days=91),
                datetime.date.today() + relativedelta(days=91),
            ]
        }},
        "recent_history": recent_history,
        "start_date": datetime.date.today() - relativedelta(days=30),
        "end_date": datetime.date.today(),
    }

    request = rf.get('/forecast/999999/')
    view = views.Forecast.as_view()
    response = view(request, filter_id=999999)
    actual_context = response.context_data

    assert actual_context.keys() == expected_context.keys()
    for key, value in expected_context.items():
        assert actual_context[key] == expected_context[key], "Key: {}".format(key)


@pytest.mark.django_db
@pytest.mark.system
def test_forecast_with_changing_scope(views, rf, make_predictable_summaries, datetime, relativedelta):
    make_predictable_summaries(100, 10, 999999, decrement=1)

    recent_history = [
        [datetime.date.today() - relativedelta(days=9), 0, 0, 100, 0.0],
        [datetime.date.today() - relativedelta(days=8), 1, 1, 100, 0.01],
        [datetime.date.today() - relativedelta(days=7), 1, 2, 100, 0.02],
        [datetime.date.today() - relativedelta(days=6), 1, 3, 100, 0.03],
        [datetime.date.today() - relativedelta(days=5), 1, 4, 100, 0.04],
        [datetime.date.today() - relativedelta(days=4), 1, 5, 100, 0.05],
        [datetime.date.today() - relativedelta(days=3), 1, 6, 100, 0.06],
        [datetime.date.today() - relativedelta(days=2), 1, 7, 100, 0.07],
        [datetime.date.today() - relativedelta(days=1), 1, 8, 100, 0.08],
        [datetime.date.today() - relativedelta(days=0), 1, 9, 100, 0.09],
    ]
    expected_context = {
        "filter_id": 999999,
        "forecasts": {30: {
            'scope': 5,
            'actual_scope': 91,
            'percentiles': [
                datetime.date.today() + relativedelta(days=5),
                datetime.date.today() + relativedelta(days=5),
                datetime.date.today() + relativedelta(days=5),
            ]
        }},
        "recent_history": recent_history,
        "start_date": datetime.date.today() - relativedelta(days=30),
        "end_date": datetime.date.today(),
    }

    request = rf.get('/forecast/999999/', {'scope': 5})
    view = views.Forecast.as_view()
    response = view(request, filter_id=999999)
    actual_context = response.context_data

    assert actual_context.keys() == expected_context.keys()
    for key, value in expected_context.items():
        assert actual_context[key] == expected_context[key], "Key: {}".format(key)


@pytest.mark.django_db
@pytest.mark.system
def test_forecast_with_no_scope_as_arg(views, rf, make_predictable_summaries, datetime, relativedelta):
    make_predictable_summaries(4, 4, 888888, decrement=1)

    recent_history = [
        [datetime.date.today() - relativedelta(days=3), 0, 0, 4, 0.0],
        [datetime.date.today() - relativedelta(days=2), 1, 1, 4, 0.25],
        [datetime.date.today() - relativedelta(days=1), 1, 2, 4, 0.5],
        [datetime.date.today() - relativedelta(days=0), 1, 3, 4, 0.75],
    ]

    expected_percentile_end_date = datetime.date.today() + relativedelta(days=1)
    expected_context = {
        "filter_id": 888888,
        "forecasts": {
            30: {'percentiles': [expected_percentile_end_date, expected_percentile_end_date, expected_percentile_end_date], 'scope': 1, 'actual_scope': 1},
        },
        "recent_history": recent_history,
        "start_date": datetime.date.today() - relativedelta(days=30),
        "end_date": datetime.date.today(),
    }

    request = rf.get('/forecast/888888/', {'scope': ''})
    view = views.Forecast.as_view()
    response = view(request, filter_id=888888)
    actual_context = response.context_data

    assert actual_context.keys() == expected_context.keys()
    for key, value in expected_context.items():
        assert actual_context[key] == expected_context[key], "Key: {}".format(key)


@pytest.mark.django_db
@pytest.mark.system
def test_forecast_with_variable_time(views, rf, make_predictable_summaries, datetime, relativedelta):
    make_predictable_summaries(100, 10, 888888, decrement=1)

    recent_history = [
        [datetime.date.today() - relativedelta(days=5), 0, 4, 100, 0.04],
        [datetime.date.today() - relativedelta(days=4), 1, 5, 100, 0.05],
        [datetime.date.today() - relativedelta(days=3), 1, 6, 100, 0.06],
        [datetime.date.today() - relativedelta(days=2), 1, 7, 100, 0.07],
        [datetime.date.today() - relativedelta(days=1), 1, 8, 100, 0.08],
        [datetime.date.today() - relativedelta(days=0), 1, 9, 100, 0.09],
    ]

    expected_percentile_end_date = datetime.date.today() + relativedelta(days=91)
    expected_context = {
        "filter_id": 888888,
        "forecasts": {
            5: {'percentiles': [expected_percentile_end_date, expected_percentile_end_date, expected_percentile_end_date], 'scope': 91, 'actual_scope': 91},
        },
        "recent_history": recent_history,
        "start_date": datetime.date.today() - relativedelta(days=5),
        "end_date": datetime.date.today(),
    }

    request = rf.get('/forecast/888888/', {'days_ago': '5'})
    view = views.Forecast.as_view()
    response = view(request, filter_id=888888)
    actual_context = response.context_data

    assert actual_context.keys() == expected_context.keys()
    for key, value in expected_context.items():
        assert actual_context[key] == expected_context[key], "Key: {}".format(key)


@pytest.mark.django_db
@pytest.mark.system
def test_forecast_with_variable_time_arg_empty(views, rf, make_predictable_summaries, datetime, relativedelta):
    make_predictable_summaries(4, 4, 888888, decrement=1)

    recent_history = [
        [datetime.date.today() - relativedelta(days=3), 0, 0, 4, 0.0],
        [datetime.date.today() - relativedelta(days=2), 1, 1, 4, 0.25],
        [datetime.date.today() - relativedelta(days=1), 1, 2, 4, 0.5],
        [datetime.date.today() - relativedelta(days=0), 1, 3, 4, 0.75],
    ]

    expected_percentile_end_date = datetime.date.today() + relativedelta(days=1)
    expected_context = {
        "filter_id": 888888,
        "forecasts": {
            30: {'percentiles': [expected_percentile_end_date, expected_percentile_end_date, expected_percentile_end_date], 'scope': 1, 'actual_scope': 1},
        },
        "recent_history": recent_history,
        "start_date": datetime.date.today() - relativedelta(days=30),
        "end_date": datetime.date.today(),
    }

    request = rf.get('/forecast/888888/', {'days_ago': ''})
    view = views.Forecast.as_view()
    response = view(request, filter_id=888888)
    actual_context = response.context_data

    assert actual_context.keys() == expected_context.keys()
    for key, value in expected_context.items():
        assert actual_context[key] == expected_context[key], "Key: {}".format(key)
