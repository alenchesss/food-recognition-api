"""
Тесты HTTP-клиентов api-service: ml_client и recipe_client.

"""
import httpx
import pytest
import respx

from app.core.config import settings
from app.services.ml_client import recognize_ingredients
from app.services.recipe_client import get_recipes_by_ingredients


@pytest.mark.asyncio
@respx.mock
async def test_ml_client_sends_base64_and_parses_response():
    route = respx.post(
        f"{settings.ml_service_url}/api/v1/ingredient-recognitions"
    ).mock(
        return_value=httpx.Response(
            200, json={"data": {"ingredients": [{"name": "egg"}]}}
        )
    )

    async with httpx.AsyncClient() as client:
        result = await recognize_ingredients(client, b"binary_image", "image/jpeg")

    assert route.called
    sent_body = route.calls.last.request.read()
    import json

    parsed = json.loads(sent_body)
    assert parsed["content_type"] == "image/jpeg"
    # base64 от "binary_image"
    assert parsed["image"] == "YmluYXJ5X2ltYWdl"

    assert len(result) == 1
    assert result[0].name == "egg"
    assert result[0].confidence == 1.0


@pytest.mark.asyncio
@respx.mock
async def test_ml_client_raises_on_http_error():
    respx.post(
        f"{settings.ml_service_url}/api/v1/ingredient-recognitions"
    ).mock(return_value=httpx.Response(500))

    async with httpx.AsyncClient() as client:
        with pytest.raises(httpx.HTTPStatusError):
            await recognize_ingredients(client, b"x", "image/jpeg")


@pytest.mark.asyncio
@respx.mock
async def test_recipe_client_sends_ingredients_and_parses_response():
    route = respx.post(f"{settings.recipe_service_url}/api/v1/recipes:find").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": 7,
                        "title": "Шакшука",
                        "image": None,
                        "used_ingredients_count": 1,
                        "missing_ingredients": [
                            {"name": "egg", "amount": 2, "unit": "pcs"}
                        ],
                        "instructions": [{"number": 1, "description": "разбить"}],
                    }
                ]
            },
        )
    )

    async with httpx.AsyncClient() as client:
        recipes = await get_recipes_by_ingredients(client, ["tomato", "onion"])

    assert route.called
    import json

    sent = json.loads(route.calls.last.request.read())
    assert sent == {"ingredients": [{"name": "tomato"}, {"name": "onion"}]}

    assert len(recipes) == 1
    r = recipes[0]
    assert r.id == 7
    assert r.name == "Шакшука"
    assert r.missing_ingredients[0].name == "egg"
    assert "1. разбить" in r.instructions


@pytest.mark.asyncio
@respx.mock
async def test_recipe_client_handles_empty_data():
    respx.post(f"{settings.recipe_service_url}/api/v1/recipes:find").mock(
        return_value=httpx.Response(200, json={"data": []})
    )

    async with httpx.AsyncClient() as client:
        recipes = await get_recipes_by_ingredients(client, ["x"])

    assert recipes == []
