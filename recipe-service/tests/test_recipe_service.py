"""
Тесты сервисного слоя RecipeService.

"""

import pytest

from app.schemas import RecipeItem
from app.services.recipe import RecipeService


class _StubClient:
    def __init__(self, recipes: list[RecipeItem] | None = None) -> None:
        self.recipes = recipes or []
        self.calls: list[tuple[list[str], int]] = []

    async def find_by_ingredients(
        self, ingredients: list[str], number: int = 3
    ) -> list[RecipeItem]:
        self.calls.append((ingredients, number))
        return self.recipes


def _make_recipe(id_: int = 1, title: str = "x") -> RecipeItem:
    return RecipeItem(
        id=id_,
        title=title,
        image=None,
        used_ingredients_count=0,
        missing_ingredients=[],
        instructions=[],
    )


@pytest.mark.asyncio
async def test_empty_ingredients_returns_empty_without_client_call():
    stub = _StubClient(recipes=[_make_recipe()])
    service = RecipeService(client=stub)  # type: ignore[arg-type]

    result = await service.find_by_ingredients([])

    assert result == []
    assert stub.calls == []


@pytest.mark.asyncio
async def test_passes_ingredients_to_client():
    expected = [_make_recipe(title="Pasta")]
    stub = _StubClient(recipes=expected)
    service = RecipeService(client=stub)  # type: ignore[arg-type]

    result = await service.find_by_ingredients(["tomato", "onion"])

    assert result == expected
    assert stub.calls == [(["tomato", "onion"], 3)]


@pytest.mark.asyncio
async def test_default_number_is_3():
    stub = _StubClient()
    service = RecipeService(client=stub)  # type: ignore[arg-type]
    await service.find_by_ingredients(["x"])
    assert stub.calls[0][1] == 3


@pytest.mark.asyncio
async def test_custom_number():
    stub = _StubClient()
    service = RecipeService(client=stub)  # type: ignore[arg-type]
    await service.find_by_ingredients(["x"], number=10)
    assert stub.calls[0][1] == 10
