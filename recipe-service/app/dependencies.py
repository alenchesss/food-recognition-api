from functools import lru_cache

from app.config import Settings, load_settings
from app.services.recipe import RecipeService
from app.services.spoonacular import SpoonacularClient


@lru_cache
def get_settings() -> Settings:
    return load_settings()


@lru_cache
def get_spoonacular_client() -> SpoonacularClient:
    return SpoonacularClient(settings=get_settings())


def get_recipe_service() -> RecipeService:
    return RecipeService(client=get_spoonacular_client())
