import json

import respx
from fastapi.testclient import TestClient
from httpx import Response

from app.core.config import settings

BASE = settings.groq_api_url


def _groq_response(recipes: list[dict]) -> dict:
    return {
        "choices": [{"message": {"content": json.dumps({"recipes": recipes}, ensure_ascii=False)}}]
    }


def test_translate_single_recipe(client: TestClient, sample_recipe: dict):
    translated = {
        **sample_recipe,
        "title": "Запечённые ригатони с колбасой",
        "missing_ingredients": [{"name": "зубчики чеснока", "amount": 3, "unit": ""}],
        "instructions": [
            {
                "number": 1,
                "description": "Доведите большую кастрюлю с подсоленной водой до кипения.",
            },
            {"number": 2, "description": "Добавьте колбасу и обжаривайте 3–4 минуты."},
        ],
    }

    with respx.mock:
        respx.post(f"{BASE}/chat/completions").mock(
            return_value=Response(200, json=_groq_response([translated]))
        )
        resp = client.post("/api/v1/recipes:translate", json={"recipes": [sample_recipe]})

    assert resp.status_code == 200
    recipe = resp.json()["data"]["recipes"][0]

    assert recipe["id"] == 633765  # id не меняется
    assert recipe["image"] == sample_recipe["image"]  # image не меняется
    assert recipe["used_ingredients_count"] == 7  # не меняется
    assert recipe["title"] == "Запечённые ригатони с колбасой"
    assert recipe["missing_ingredients"][0]["name"] == "зубчики чеснока"
    assert recipe["missing_ingredients"][0]["amount"] == 3  # amount не меняется
    assert recipe["instructions"][0]["number"] == 1  # number не меняется
    assert "кипения" in recipe["instructions"][0]["description"]


def test_translate_empty_list(client: TestClient):
    resp = client.post("/api/v1/recipes:translate", json={"recipes": []})
    assert resp.status_code == 200
    assert resp.json()["data"]["recipes"] == []


def test_translate_multiple_recipes(client: TestClient, sample_recipe: dict):
    recipe2 = {
        "id": 660215,
        "title": "Skillet Lasagna",
        "image": "https://img.spoonacular.com/recipes/660215-312x231.jpg",
        "used_ingredients_count": 5,
        "missing_ingredients": [{"name": "tomato sauce", "amount": 8, "unit": "oz"}],
        "instructions": [{"number": 1, "description": "Heat oil in a skillet."}],
    }
    translated = [
        {
            **sample_recipe,
            "title": "Запечённые ригатони с колбасой",
            "missing_ingredients": [{"name": "зубчики чеснока", "amount": 3, "unit": ""}],
            "instructions": [
                {"number": 1, "description": "Доведите воду до кипения."},
                {"number": 2, "description": "Обжарьте колбасу."},
            ],
        },
        {
            **recipe2,
            "title": "Лазанья на сковороде",
            "missing_ingredients": [{"name": "томатный соус", "amount": 8, "unit": "oz"}],
            "instructions": [{"number": 1, "description": "Разогрейте масло на сковороде."}],
        },
    ]

    with respx.mock:
        respx.post(f"{BASE}/chat/completions").mock(
            return_value=Response(200, json=_groq_response(translated))
        )
        resp = client.post(
            "/api/v1/recipes:translate",
            json={"recipes": [sample_recipe, recipe2]},
        )

    assert resp.status_code == 200
    recipes = resp.json()["data"]["recipes"]
    assert len(recipes) == 2
    assert recipes[0]["title"] == "Запечённые ригатони с колбасой"
    assert recipes[1]["title"] == "Лазанья на сковороде"
    assert recipes[1]["missing_ingredients"][0]["name"] == "томатный соус"


def test_translate_groq_error_returns_500(client: TestClient, sample_recipe: dict):
    with respx.mock:
        respx.post(f"{BASE}/chat/completions").mock(return_value=Response(500, text="server error"))
        resp = client.post("/api/v1/recipes:translate", json={"recipes": [sample_recipe]})

    assert resp.status_code == 500
    assert "Groq" in resp.json()["errors"][0]["message"]


def test_translate_invalid_body_returns_400(client: TestClient):
    resp = client.post("/api/v1/recipes:translate", json={"recipes": "not-a-list"})
    assert resp.status_code == 400


def test_translate_recipe_missing_field_returns_400(client: TestClient):
    incomplete = {"id": 1, "title": "Soup"}
    resp = client.post("/api/v1/recipes:translate", json={"recipes": [incomplete]})
    assert resp.status_code == 400
