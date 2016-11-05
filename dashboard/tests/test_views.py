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
