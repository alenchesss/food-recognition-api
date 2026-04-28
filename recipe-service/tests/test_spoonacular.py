"""
Тесты SpoonacularClient.

"""

import httpx
import pytest
import respx

from app.config import Settings
from app.services.spoonacular import SpoonacularClient, SpoonacularError

# ===== _parse_recipe =====


def test_parse_recipe_full_payload():
    raw = {
        "id": 42,
        "title": "Шакшука",
        "image": "http://x/y.jpg",
        "usedIngredientCount": 3,
        "missedIngredients": [
            {"name": "egg", "amount": 2.0, "unit": "pcs"},
            {"name": "salt", "amount": 0.5, "unit": "tsp"},
        ],
    }
    info = {
        "analyzedInstructions": [
            {
                "steps": [
                    {"number": 1, "step": "Heat the pan"},
                    {"number": 2, "step": "Crack eggs"},
                ]
            }
        ]
    }

    item = SpoonacularClient._parse_recipe(raw, info)

    assert item.id == 42
    assert item.title == "Шакшука"
    assert item.image == "http://x/y.jpg"
    assert item.used_ingredients_count == 3
    assert len(item.missing_ingredients) == 2
    assert item.missing_ingredients[0].name == "egg"
    assert item.missing_ingredients[0].amount == 2.0
    assert len(item.instructions) == 2
    assert item.instructions[0].description == "Heat the pan"


def test_parse_recipe_with_missing_optional_fields():
    raw = {"id": 1, "title": "Test"}
    info: dict = {}

    item = SpoonacularClient._parse_recipe(raw, info)

    assert item.id == 1
    assert item.title == "Test"
    assert item.image is None
    assert item.used_ingredients_count == 0
    assert item.missing_ingredients == []
    assert item.instructions == []


def test_parse_recipe_missing_ingredient_field_defaults():
    raw = {"id": 1, "title": "x", "missedIngredients": [{}]}
    info: dict = {}

    item = SpoonacularClient._parse_recipe(raw, info)

    assert item.missing_ingredients[0].name == ""
    assert item.missing_ingredients[0].amount == 0.0
    assert item.missing_ingredients[0].unit == ""


def test_parse_recipe_empty_analyzed_instructions():
    raw = {"id": 1, "title": "x"}
    info = {"analyzedInstructions": []}
    item = SpoonacularClient._parse_recipe(raw, info)
    assert item.instructions == []


# ===== find_by_ingredients =====


@pytest.fixture
def settings() -> Settings:
    return Settings(
        spoonacular_api_key="test-key",
        spoonacular_base_url="https://api.spoonacular.com",
        database_url="sqlite:///:memory:",
    )


@pytest.mark.asyncio
@respx.mock
async def test_find_by_ingredients_makes_two_requests_per_recipe(settings):
    respx.get("https://api.spoonacular.com/recipes/findByIngredients").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": 100,
                    "title": "Pasta",
                    "image": "http://img/100.jpg",
                    "usedIngredientCount": 2,
                    "missedIngredients": [{"name": "basil", "amount": 1, "unit": "leaf"}],
                }
            ],
        )
    )
    info_route = respx.get("https://api.spoonacular.com/recipes/100/information").mock(
        return_value=httpx.Response(
            200,
            json={"analyzedInstructions": [{"steps": [{"number": 1, "step": "Boil water"}]}]},
        )
    )

    client = SpoonacularClient(settings=settings)
    try:
        recipes = await client.find_by_ingredients(["tomato"], number=1)
    finally:
        await client.close()

    assert info_route.called
    assert len(recipes) == 1
    assert recipes[0].id == 100
    assert recipes[0].instructions[0].description == "Boil water"


@pytest.mark.asyncio
@respx.mock
async def test_find_by_ingredients_passes_apikey_in_query(settings):
    route = respx.get("https://api.spoonacular.com/recipes/findByIngredients").mock(
        return_value=httpx.Response(200, json=[])
    )

    client = SpoonacularClient(settings=settings)
    try:
        await client.find_by_ingredients(["tomato", "onion"], number=5)
    finally:
        await client.close()

    sent_params = dict(route.calls.last.request.url.params)
    assert sent_params["apiKey"] == "test-key"
    assert sent_params["ingredients"] == "tomato,onion"
    assert sent_params["number"] == "5"


@pytest.mark.asyncio
@respx.mock
async def test_find_by_ingredients_raises_on_http_error(settings):
    respx.get("https://api.spoonacular.com/recipes/findByIngredients").mock(
        return_value=httpx.Response(401)
    )

    client = SpoonacularClient(settings=settings)
    try:
        with pytest.raises(SpoonacularError, match="findByIngredients failed: 401"):
            await client.find_by_ingredients(["tomato"])
    finally:
        await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_find_by_ingredients_raises_on_network_error(settings):
    respx.get("https://api.spoonacular.com/recipes/findByIngredients").mock(
        side_effect=httpx.ConnectError("dns failed")
    )

    client = SpoonacularClient(settings=settings)
    try:
        with pytest.raises(SpoonacularError, match="request error"):
            await client.find_by_ingredients(["tomato"])
    finally:
        await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_find_by_ingredients_raises_when_info_fails(settings):
    """findByIngredients ок, а /information отдает 500 — должен подняться SpoonacularError."""
    respx.get("https://api.spoonacular.com/recipes/findByIngredients").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "title": "x", "missedIngredients": []}])
    )
    respx.get("https://api.spoonacular.com/recipes/1/information").mock(
        return_value=httpx.Response(500)
    )

    client = SpoonacularClient(settings=settings)
    try:
        with pytest.raises(SpoonacularError, match="recipe info failed: 500"):
            await client.find_by_ingredients(["tomato"])
    finally:
        await client.close()
