"""
Тесты health-эндпоинта api-service.

"""
import httpx
import pytest
import respx


@pytest.fixture
def ml_url() -> str:
    from app.core.config import settings

    return settings.ml_service_url


@pytest.fixture
def recipe_url() -> str:
    from app.core.config import settings

    return settings.recipe_service_url


@respx.mock
def test_health_all_ok(client, ml_url, recipe_url):
    respx.get(f"{ml_url}/api/v1/health").mock(return_value=httpx.Response(200))
    respx.get(f"{recipe_url}/api/v1/health").mock(return_value=httpx.Response(200))

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert body["data"]["status"] == "ok"
    assert body["data"]["services"] == {"ml-service": "ok", "recipe-service": "ok"}


@respx.mock
def test_health_one_service_degraded(client, ml_url, recipe_url):
    respx.get(f"{ml_url}/api/v1/health").mock(return_value=httpx.Response(503))
    respx.get(f"{recipe_url}/api/v1/health").mock(return_value=httpx.Response(200))

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "degraded"
    assert body["data"]["services"]["ml-service"] == "degraded"
    assert body["data"]["services"]["recipe-service"] == "ok"


@respx.mock
def test_health_service_unavailable(client, ml_url, recipe_url):
    respx.get(f"{ml_url}/api/v1/health").mock(
        side_effect=httpx.ConnectError("connection refused")
    )
    respx.get(f"{recipe_url}/api/v1/health").mock(return_value=httpx.Response(200))

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "degraded"
    assert body["data"]["services"]["ml-service"] == "unavailable"


def test_health_404_for_old_path(client):
    response = client.get("/health")
    assert response.status_code == 404
    body = response.json()
    # формат ошибки по гайду
    assert body["data"] is None
    assert body["errors"][0]["code"] == "NotFoundHttpException"
