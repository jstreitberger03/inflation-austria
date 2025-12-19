import pytest
from fastapi.testclient import TestClient

from backend.app import DATA_CACHE, DataRequest, app, compute_data


@pytest.fixture(autouse=True)
def _clear_cache():
    DATA_CACHE.clear()
    yield
    DATA_CACHE.clear()


def test_health_endpoint():
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


def test_data_endpoint_returns_payload():
    with TestClient(app) as client:
        resp = client.get("/data")
        assert resp.status_code == 200
        payload = resp.json()
        for key in ["config", "inflation", "interest_rates", "comparison"]:
            assert key in payload


def test_compute_data_uses_cache_for_default_request():
    first = compute_data()
    second = compute_data()
    assert first is second  # cached instance reused


def test_compute_data_caches_by_payload():
    req = DataRequest(countries=["AT", "DE"])
    data_with_override = compute_data(override=req)
    cached_again = compute_data(override=req)
    assert data_with_override is cached_again
    # Default cache stays separate
    default_data = compute_data()
    assert default_data is not data_with_override
