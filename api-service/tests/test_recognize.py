"""
Тесты основного эндпоинта POST /api/v1/recognitions.

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
def test_recognize_success(client, fake_jpeg_bytes, ml_url, recipe_url):
    """Успешный сценарий: ml вернул ингредиенты, recipe вернул рецепты."""
    respx.post(f"{ml_url}/api/v1/ingredient-recognitions").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "ingredients": [
                        {"name": "tomato"},
                        {"name": "onion"},
                    ]
                }
            },
        )
    )
    respx.post(f"{recipe_url}/api/v1/recipes:find").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": 42,
                        "title": "Томатный суп",
                        "image": None,
                        "used_ingredients_count": 2,
                        "missing_ingredients": [
                            {"name": "garlic", "amount": 1.0, "unit": "clove"}
                        ],
                        "instructions": [
                            {"number": 1, "description": "Нарезать"},
                            {"number": 2, "description": "Варить"},
                        ],
                    }
                ]
            },
        )
    )

    response = client.post(
        "/api/v1/recognitions",
        files={"image": ("food.jpg", fake_jpeg_bytes, "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    data = body["data"]
    assert len(data["detected_ingredients"]) == 2
    assert data["detected_ingredients"][0]["name"] == "tomato"
    assert len(data["recipes"]) == 1
    recipe = data["recipes"][0]
    assert recipe["id"] == 42
    assert recipe["name"] == "Томатный суп"
    assert recipe["missing_ingredients"] == [{"name": "garlic"}]
    assert "1. Нарезать" in recipe["instructions"]
    assert "2. Варить" in recipe["instructions"]


def test_recognize_invalid_content_type(client):
    response = client.post(
        "/api/v1/recognitions",
        files={"image": ("doc.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert response.status_code == 400
    body = response.json()
    # формат ошибки по гайду
    assert body["data"] is None
    assert body["errors"][0]["code"] == "BadRequestHttpException"
    assert "Неверный тип файла" in body["errors"][0]["message"]


def test_recognize_file_too_large(client):
    big = b"\xff\xd8\xff\xe0" + b"\x00" * (11 * 1024 * 1024)
    response = client.post(
        "/api/v1/recognitions",
        files={"image": ("big.jpg", big, "image/jpeg")},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["errors"][0]["code"] == "BadRequestHttpException"
    assert "слишком большой" in body["errors"][0]["message"]


@respx.mock
def test_recognize_empty_ingredients_returns_empty_recipes(
    client, fake_jpeg_bytes, ml_url
):
    respx.post(f"{ml_url}/api/v1/ingredient-recognitions").mock(
        return_value=httpx.Response(200, json={"data": {"ingredients": []}})
    )

    response = client.post(
        "/api/v1/recognitions",
        files={"image": ("food.jpg", fake_jpeg_bytes, "image/jpeg")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["detected_ingredients"] == []
    assert body["data"]["recipes"] == []


@respx.mock
def test_recognize_ml_service_error(client, fake_jpeg_bytes, ml_url):
    respx.post(f"{ml_url}/api/v1/ingredient-recognitions").mock(
        return_value=httpx.Response(500)
    )

    response = client.post(
        "/api/v1/recognitions",
        files={"image": ("food.jpg", fake_jpeg_bytes, "image/jpeg")},
    )
    assert response.status_code == 502
    body = response.json()
    assert body["errors"][0]["code"] == "BadGatewayHttpException"
    assert "ml-service" in body["errors"][0]["message"]


@respx.mock
def test_recognize_recipe_service_error(client, fake_jpeg_bytes, ml_url, recipe_url):
    respx.post(f"{ml_url}/api/v1/ingredient-recognitions").mock(
        return_value=httpx.Response(
            200, json={"data": {"ingredients": [{"name": "tomato"}]}}
        )
    )
    respx.post(f"{recipe_url}/api/v1/recipes:find").mock(
        return_value=httpx.Response(500)
    )

    response = client.post(
        "/api/v1/recognitions",
        files={"image": ("food.jpg", fake_jpeg_bytes, "image/jpeg")},
    )
    assert response.status_code == 502
    body = response.json()
    assert body["errors"][0]["code"] == "BadGatewayHttpException"
    assert "recipe-service" in body["errors"][0]["message"]


def test_recognize_no_image(client):
    response = client.post("/api/v1/recognitions")
    assert response.status_code == 400  # ValidationException
    body = response.json()
    assert body["data"] is None
    assert body["errors"][0]["code"] == "ValidationException"
