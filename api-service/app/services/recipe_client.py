import httpx

from app.core.config import settings
from app.schemas.models import Ingredient, Recipe


async def get_recipes_by_ingredients(
    client: httpx.AsyncClient,
    ingredients: list[Ingredient],
) -> list[Recipe]:
    response = await client.post(
        f"{settings.recipe_service_url}/api/v1/recipes:find",
        json={"ingredients": [{"name": i.name} for i in ingredients]},
    )
    response.raise_for_status()
    data = response.json()
    return [Recipe(**r) for r in data["data"]]
