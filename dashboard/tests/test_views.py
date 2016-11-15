from unittest.mock import Mock

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
def test_refresh(rf, views, monkeypatch):
    mock_cache = Mock()
    mock_generate_dashboard = Mock()
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
    response = client.get('/history/123456/')
    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.system
def test_history_with_bad_filter_id(rf, views):
    request = rf.get('/history/123456/')
    with pytest.raises(Http404):
        views.History.as_view()(request, filter_id=123456)
