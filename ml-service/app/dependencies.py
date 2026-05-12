from functools import lru_cache

from app.config import Settings, settings
from app.recognizer import IngredientRecognizer


@lru_cache
def get_settings() -> Settings:
    return settings


@lru_cache
def get_recognizer() -> IngredientRecognizer:
    return IngredientRecognizer(settings=get_settings())
