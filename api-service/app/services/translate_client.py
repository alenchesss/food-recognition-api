import httpx

from app.core.config import settings
from app.schemas.models import Recipe


async def translate_recipes(
    client: httpx.AsyncClient,
    recipes: list[Recipe],
) -> list[Recipe]:
    response = await client.post(
        f"{settings.translate_service_url}/api/v1/recipes:translate",
        json={"recipes": [r.model_dump() for r in recipes]},
    )
    response.raise_for_status()
    data = response.json()
    return [Recipe(**r) for r in data["data"]["recipes"]]
