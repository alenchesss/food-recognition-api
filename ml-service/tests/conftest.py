"""
conftest для ml-service.

"""

import os
from dataclasses import dataclass

os.environ.setdefault("YANDEX_API_KEY", "test-key")
os.environ.setdefault("YANDEX_PROJECT_ID", "test-project")
os.environ.setdefault("YANDEX_PROMPT_ID", "test-prompt")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.dependencies import get_recognizer  # noqa: E402
from app.main import app  # noqa: E402


@dataclass(frozen=True)
class FakePrediction:
    name: str


class FakeRecognizer:
    def __init__(self, ingredients: list[str] | None = None) -> None:
        self.ingredients = ingredients or []
        self.calls: list[tuple[bytes, str]] = []

    def predict(self, *, image_bytes: bytes, content_type: str):
        self.calls.append((image_bytes, content_type))
        return [FakePrediction(name=n) for n in self.ingredients]


@pytest.fixture
def fake_recognizer() -> FakeRecognizer:
    return FakeRecognizer(ingredients=["tomato", "cheese"])


@pytest.fixture
def client(fake_recognizer):
    app.dependency_overrides[get_recognizer] = lambda: fake_recognizer
    yield TestClient(app)
    app.dependency_overrides.clear()
