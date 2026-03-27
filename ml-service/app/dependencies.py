from functools import lru_cache

from app.config import Settings, load_settings
from app.recognizer import IngredientRecognizer


@lru_cache
def get_settings() -> Settings:
    return load_settings()


@lru_cache
def get_recognizer() -> IngredientRecognizer:
    return IngredientRecognizer(settings=get_settings())
