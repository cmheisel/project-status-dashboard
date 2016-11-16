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
@pytest.mark.system
def test_forecast_with_good_filter_id(rf, views, summaries, make_one_summary, datetime, relativedelta):
    incomplete = 4
    complete = 0
    total = incomplete + complete
    for i in reversed(range(1, 4)):
        s = make_one_summary(filter_id=78910, created_on=datetime.date.today() - relativedelta(days=i), incomplete=incomplete, complete=complete, total=total)
        summaries.store(s)
        incomplete = incomplete - 1
        complete = complete + 1
        total = incomplete + complete

    request = rf.get('/forecast/78910/')
    response = views.Forecast.as_view()(request, filter_id=78910)
    assert response.status_code == 200

    actual_context = views.Forecast().get_context_data(filter_id=78910)
    expected_context = {
        "filter_id": 78910,
        "filter_summaries": summaries.for_date_range(78910, datetime.date.today() - relativedelta(days=4)),
        "forecasts": {
            14: [2, 2, 2],
        }
    }

    assert actual_context.keys() == expected_context.keys()
    assert actual_context['filter_id'] == expected_context['filter_id']
    assert list(actual_context['filter_summaries']) == list(expected_context['filter_summaries'])
    assert actual_context['forecasts'] == expected_context['forecasts']
