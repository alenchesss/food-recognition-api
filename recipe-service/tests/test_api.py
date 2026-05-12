"""
Тесты HTTP-эндпоинтов recipe-service.
.
"""

from app.schemas import MissingIngredientItem, RecipeItem, RecipeStep
from app.services.spoonacular import SpoonacularError


def test_health_returns_data_envelope(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"data": {"status": "ok"}}


def test_find_recipes_success(client, fake_service):
    fake_service.recipes_to_return = [
        RecipeItem(
            id=1,
            title="Pasta",
            image="http://x/y.jpg",
            used_ingredients_count=2,
            missing_ingredients=[MissingIngredientItem(name="basil", amount=1.0, unit="leaf")],
            instructions=[RecipeStep(number=1, description="boil water")],
        )
    ]

    response = client.post(
        "/api/v1/recipes:find",
        json={"ingredients": [{"name": "tomato"}, {"name": "garlic"}]},
    )

    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert len(body["data"]) == 1
    recipe = body["data"][0]
    assert recipe["id"] == 1
    assert recipe["title"] == "Pasta"
    assert recipe["used_ingredients_count"] == 2
    assert recipe["missing_ingredients"] == [{"name": "basil", "amount": 1.0, "unit": "leaf"}]
    assert recipe["instructions"] == [{"number": 1, "description": "boil water"}]

    # сервис был вызван с правильными ингредиентами
    assert fake_service.last_call == ["tomato", "garlic"]


def test_find_recipes_empty_result(client, fake_service):
    fake_service.recipes_to_return = []
    response = client.post("/api/v1/recipes:find", json={"ingredients": [{"name": "x"}]})
    assert response.status_code == 200
    assert response.json() == {"data": []}


def test_find_recipes_validation_no_ingredients(client):
    """Пустой список ингредиентов отвергается (min_length=1)."""
    response = client.post("/api/v1/recipes:find", json={"ingredients": []})
    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["errors"][0]["code"] == "ValidationException"


def test_find_recipes_validation_no_body(client):
    response = client.post("/api/v1/recipes:find")
    assert response.status_code == 400
    body = response.json()
    assert body["errors"][0]["code"] == "ValidationException"


def test_find_recipes_spoonacular_error_returns_502(client, fake_service):
    fake_service.exception_to_raise = SpoonacularError("upstream is down")
    response = client.post("/api/v1/recipes:find", json={"ingredients": [{"name": "tomato"}]})
    assert response.status_code == 502
    body = response.json()
    assert body["data"] is None
    assert body["errors"][0]["code"] == "ExternalServiceError"
    assert "upstream is down" in body["errors"][0]["message"]


def test_404_uses_guide_format(client):
    response = client.get("/api/v1/non-existent")
    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["errors"][0]["code"] == "NotFoundHttpException"
