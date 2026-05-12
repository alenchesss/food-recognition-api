import respx
from fastapi.testclient import TestClient
from httpx import Response

from app.core.config import settings

BASE = settings.groq_api_url


def test_health_ok(client: TestClient):
    with respx.mock:
        respx.get(f"{BASE}/models").mock(return_value=Response(200, json={"data": []}))
        resp = client.get("/api/v1/health")

    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["status"] == "ok"
    assert body["data"]["services"]["groq"] == "ok"


def test_health_degraded_on_error(client: TestClient):
    with respx.mock:
        respx.get(f"{BASE}/models").mock(return_value=Response(401))
        resp = client.get("/api/v1/health")

    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "degraded"


def test_health_unavailable_on_network_error(client: TestClient):
    with respx.mock:
        respx.get(f"{BASE}/models").mock(side_effect=Exception("connection refused"))
        resp = client.get("/api/v1/health")

    assert resp.status_code == 200
    assert resp.json()["data"]["services"]["groq"] == "unavailable"
