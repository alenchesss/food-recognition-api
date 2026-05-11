import httpx

from app.config import Settings
from app.schemas import MissingIngredientItem, RecipeItem, RecipeStep


class SpoonacularError(Exception):
    pass


class SpoonacularClient:
    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.spoonacular_api_key
        self._client = httpx.AsyncClient(
            base_url=settings.spoonacular_base_url,
            timeout=10.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def find_by_ingredients(
        self,
        ingredients: list[str],
        number: int = 3,
    ) -> list[RecipeItem]:
        raw_list = await self._fetch_by_ingredients(ingredients, number)

        recipes = []
        for raw in raw_list:
            info = await self._fetch_recipe_info(raw["id"])
            recipes.append(self._parse_recipe(raw, info))

        return recipes

    async def _fetch_by_ingredients(
        self,
        ingredients: list[str],
        number: int,
    ) -> list[dict]:
        try:
            response = await self._client.get(
                "/recipes/findByIngredients",
                params={
                    "apiKey": self._api_key,
                    "ingredients": ",".join(ingredients),
                    "number": number,
                    "ranking": 1,
                    "ignorePantry": True,
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise SpoonacularError(
                f"Spoonacular findByIngredients failed: {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise SpoonacularError(f"Spoonacular request error: {exc}") from exc

        return response.json()

    async def _fetch_recipe_info(self, recipe_id: int) -> dict:
        try:
            response = await self._client.get(
                f"/recipes/{recipe_id}/information",
                params={"apiKey": self._api_key, "stepBreakdown": True},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise SpoonacularError(
                f"Spoonacular recipe info failed: {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise SpoonacularError(f"Spoonacular request error: {exc}") from exc

        return response.json()

    @staticmethod
    def _parse_recipe(raw: dict, info: dict) -> RecipeItem:
        missed = [
            MissingIngredientItem(
                name=ing.get("name", ""),
                amount=ing.get("amount", 0.0),
                unit=ing.get("unit", ""),
            )
            for ing in raw.get("missedIngredients", [])
        ]

        steps: list[RecipeStep] = []
        analyzed = info.get("analyzedInstructions", [])
        if analyzed:
            for step in analyzed[0].get("steps", []):
                steps.append(
                    RecipeStep(
                        number=step.get("number", 0),
                        description=step.get("step", ""),
                    )
                )

        return RecipeItem(
            id=raw["id"],
            title=raw["title"],
            image=raw.get("image"),
            used_ingredients_count=raw.get("usedIngredientCount", 0),
            missing_ingredients=missed,
            instructions=steps,
        )
