import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_recipe() -> dict:
    return {
        "id": 633765,
        "title": "Baked Rigatoni With Sausage",
        "image": "https://img.spoonacular.com/recipes/633765-312x231.jpg",
        "used_ingredients_count": 7,
        "missing_ingredients": [{"name": "garlic cloves", "amount": 3, "unit": ""}],
        "instructions": [
            {"number": 1, "description": "Bring a large pot of salted water to a boil."},
            {"number": 2, "description": "Add the sausage and saute for 3 to 4 minutes."},
        ],
    }
