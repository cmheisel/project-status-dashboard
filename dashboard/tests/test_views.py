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
        for i in reversed(range(1, days)):
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
    ]

    expected_percentile_end_date = datetime.date.today() + relativedelta(days=1)

    actual_context = views.Forecast().get_context_data(filter_id=78910)
    expected_context = {
        "filter_id": 78910,
        "forecasts": {
            30: {'percentiles': [expected_percentile_end_date, expected_percentile_end_date, expected_percentile_end_date], 'scope': 2},
        },
        "recent_history": recent_history,
        "start_date": datetime.date.today() - relativedelta(days=29),
        "end_date": datetime.date.today() - relativedelta(days=1),
    }

    assert actual_context.keys() == expected_context.keys()
    for key, value in expected_context.items():
        assert actual_context[key] == expected_context[key], "Key: {}".format(key)


@pytest.mark.django_db
@pytest.mark.system
def test_forecast_with_little_to_no_throughput(rf, views, make_predictable_summaries, datetime, relativedelta):
    make_predictable_summaries(4, 4, 888888, decrement=0)

    request = rf.get('/forecast/888888/')
    response = views.Forecast.as_view()(request, filter_id=888888)
    assert response.status_code == 200

    recent_history = [
        [datetime.date.today() - relativedelta(days=3), 0, 0, 4, 0.0],
        [datetime.date.today() - relativedelta(days=2), 0, 0, 4, 0.0],
        [datetime.date.today() - relativedelta(days=1), 0, 0, 4, 0.0],
    ]

    actual_context = views.Forecast().get_context_data(filter_id=888888)
    expected_context = {
        "filter_id": 888888,
        "forecasts": {},
        "recent_history": recent_history,
        "start_date": datetime.date.today() - relativedelta(days=29),
        "end_date": datetime.date.today() - relativedelta(days=1),
    }

    assert actual_context.keys() == expected_context.keys()
    for key, value in expected_context.items():
        assert actual_context[key] == expected_context[key], "Key: {}".format(key)


@pytest.mark.django_db
@pytest.mark.system
def test_forecast_with_no_scope(rf, views, make_predictable_summaries, datetime, relativedelta):
    make_predictable_summaries(0, 4, 999999, decrement=0)

    request = rf.get('/forecast/999999/')
    response = views.Forecast.as_view()(request, filter_id=999999)
    assert response.status_code == 200

    recent_history = [
        [datetime.date.today() - relativedelta(days=3), 0, 0, 0, 0.0],
        [datetime.date.today() - relativedelta(days=2), 0, 0, 0, 0.0],
        [datetime.date.today() - relativedelta(days=1), 0, 0, 0, 0.0],
    ]

    actual_context = views.Forecast().get_context_data(filter_id=999999)
    expected_context = {
        "filter_id": 999999,
        "forecasts": {},
        "recent_history": recent_history,
        "start_date": datetime.date.today() - relativedelta(days=29),
        "end_date": datetime.date.today() - relativedelta(days=1),
    }

    assert actual_context.keys() == expected_context.keys()
    for key, value in expected_context.items():
        assert actual_context[key] == expected_context[key], "Key: {}".format(key)
