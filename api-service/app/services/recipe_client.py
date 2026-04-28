import httpx

from app.core.config import settings
from app.schemas.models import MissingIngredient, Recipe, RecipeFindResponseEnvelope


async def get_recipes_by_ingredients(
    client: httpx.AsyncClient,
    ingredient_names: list[str],
) -> list[Recipe]:
    """
    Запрашивает рецепты у recipe-service по списку ингредиентов.

    recipe-service отвечает в формате Ensi API Guide:
        {"data": [ {...recipe...}, ... ]}
    """
    response = await client.post(
        f"{settings.recipe_service_url}/api/v1/recipes:find",
        json={"ingredients": [{"name": name} for name in ingredient_names]},
    )
    response.raise_for_status()

    envelope = RecipeFindResponseEnvelope(**response.json())

    # Маппинг recipe-service -> внутренней модели api-service
    recipes: list[Recipe] = []
    for item in envelope.data:
        recipes.append(
            Recipe(
                id=item.id,
                name=item.title,
                description=item.title,
                ingredients=[m.name for m in item.missing_ingredients],
                missing_ingredients=[
                    MissingIngredient(name=m.name) for m in item.missing_ingredients
                ],
                instructions="\n".join(
                    f"{step.number}. {step.description}" for step in item.instructions
                ),
            )
        )

    return recipes
