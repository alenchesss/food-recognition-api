"""
Тесты Pydantic-моделей api-service.

"""
import pytest
from pydantic import ValidationError

from app.schemas.models import (
    Ingredient,
    MLServiceResponseEnvelope,
    Recipe,
    RecipeFindResponseEnvelope,
)


def test_ml_envelope_parses_valid_response():
    raw = {"data": {"ingredients": [{"name": "tomato"}, {"name": "basil"}]}}
    envelope = MLServiceResponseEnvelope(**raw)
    assert len(envelope.data.ingredients) == 2
    assert envelope.data.ingredients[0].name == "tomato"


def test_ml_envelope_rejects_response_without_data():
    with pytest.raises(ValidationError):
        MLServiceResponseEnvelope(**{"ingredients": [{"name": "tomato"}]})


def test_recipe_envelope_parses_full_response():
    raw = {
        "data": [
            {
                "id": 1,
                "title": "Pasta",
                "image": "http://x/y.jpg",
                "used_ingredients_count": 3,
                "missing_ingredients": [
                    {"name": "salt", "amount": 1, "unit": "tsp"}
                ],
                "instructions": [
                    {"number": 1, "description": "Boil water"},
                ],
            }
        ]
    }
    envelope = RecipeFindResponseEnvelope(**raw)
    assert len(envelope.data) == 1
    item = envelope.data[0]
    assert item.id == 1
    assert item.missing_ingredients[0].unit == "tsp"


def test_recipe_envelope_handles_optional_fields():
    """image, instructions, missing_ingredients — опциональны."""
    raw = {
        "data": [
            {
                "id": 1,
                "title": "Pasta",
            }
        ]
    }
    envelope = RecipeFindResponseEnvelope(**raw)
    assert envelope.data[0].image is None
    assert envelope.data[0].instructions == []


def test_recipe_envelope_empty_data():
    envelope = RecipeFindResponseEnvelope(**{"data": []})
    assert envelope.data == []


def test_ingredient_requires_confidence():
    with pytest.raises(ValidationError):
        Ingredient(name="tomato")  # type: ignore[call-arg]


def test_recipe_serializes_correctly():
    recipe = Recipe(
        id=1,
        name="Soup",
        description="...",
        ingredients=["tomato"],
        missing_ingredients=[],
        instructions="boil",
    )
    dumped = recipe.model_dump()
    assert dumped["id"] == 1
    assert dumped["missing_ingredients"] == []
