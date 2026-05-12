"""
Тесты HTTP-эндпоинтов ml-service.

"""
import base64

import pytest


def test_health_returns_data_envelope(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body == {"data": {"status": "ok"}}


def test_recognize_success(client, fake_recognizer):
    image_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    payload = {
        "image": base64.b64encode(image_bytes).decode(),
        "content_type": "image/jpeg",
    }

    response = client.post("/api/v1/ingredient-recognitions", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert body["data"] == {
        "ingredients": [{"name": "tomato"}, {"name": "cheese"}]
    }
    # recognizer был вызван с теми же байтами и content_type
    assert len(fake_recognizer.calls) == 1
    assert fake_recognizer.calls[0] == (image_bytes, "image/jpeg")


def test_recognize_invalid_content_type(client):
    payload = {
        "image": base64.b64encode(b"x").decode(),
        "content_type": "application/pdf",
    }
    response = client.post("/api/v1/ingredient-recognitions", json=payload)
    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["errors"][0]["code"] == "BadRequestHttpException"
    assert body["errors"][0]["message"] == "Unsupported content_type"


def test_recognize_invalid_base64(client):
    payload = {"image": "not-base64!!!@@@", "content_type": "image/jpeg"}
    response = client.post("/api/v1/ingredient-recognitions", json=payload)
    assert response.status_code == 400
    body = response.json()
    assert body["errors"][0]["code"] == "BadRequestHttpException"
    assert body["errors"][0]["message"] == "Invalid base64 image"


def test_recognize_image_too_large(client):
    big = b"\x00" * (11 * 1024 * 1024)
    payload = {
        "image": base64.b64encode(big).decode(),
        "content_type": "image/jpeg",
    }
    response = client.post("/api/v1/ingredient-recognitions", json=payload)
    assert response.status_code == 400
    body = response.json()
    assert body["errors"][0]["message"] == "Image is too large"


@pytest.mark.parametrize(
    "missing_field, body",
    [
        ("image", {"content_type": "image/jpeg"}),
        ("content_type", {"image": "Zm9v"}),
    ],
)
def test_recognize_missing_required_fields(client, missing_field, body):
    response = client.post("/api/v1/ingredient-recognitions", json=body)
    assert response.status_code == 400
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "ValidationException"


def test_recognize_empty_image_string_fails_validation(client):
    payload = {"image": "", "content_type": "image/jpeg"}
    response = client.post("/api/v1/ingredient-recognitions", json=payload)
    assert response.status_code == 400
    body = response.json()
    assert body["errors"][0]["code"] == "ValidationException"


def test_404_uses_guide_format(client):
    response = client.get("/api/v1/non-existent-endpoint")
    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["errors"][0]["code"] == "NotFoundHttpException"
