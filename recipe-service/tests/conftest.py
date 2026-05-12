import os

os.environ.setdefault("SPOONACULAR_API_KEY", "test-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.dependencies import get_recipe_service  # noqa: E402
from app.main import app  # noqa: E402
from app.schemas import RecipeItem  # noqa: E402


class FakeRecipeService:
    """In-memory заглушка RecipeService для эндпоинт-тестов."""

    def __init__(self) -> None:
        self.recipes_to_return: list[RecipeItem] = []
        self.exception_to_raise: Exception | None = None
        self.last_call: list[str] | None = None

    async def find_by_ingredients(
        self, ingredient_names: list[str], number: int = 3
    ) -> list[RecipeItem]:
        self.last_call = ingredient_names
        if self.exception_to_raise is not None:
            raise self.exception_to_raise
        return self.recipes_to_return


@pytest.fixture
def fake_service() -> FakeRecipeService:
    return FakeRecipeService()


@pytest.fixture
def client(fake_service):
    app.dependency_overrides[get_recipe_service] = lambda: fake_service
    yield TestClient(app)
    app.dependency_overrides.clear()
