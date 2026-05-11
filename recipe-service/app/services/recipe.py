from app.schemas import RecipeItem
from app.services.spoonacular import SpoonacularClient


class RecipeService:
    def __init__(self, client: SpoonacularClient) -> None:
        self._client = client

    async def find_by_ingredients(
        self,
        ingredient_names: list[str],
        number: int = 3,
    ) -> list[RecipeItem]:
        if not ingredient_names:
            return []

        return await self._client.find_by_ingredients(
            ingredients=ingredient_names,
            number=number,
        )
