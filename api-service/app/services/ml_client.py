import base64

import httpx

from app.core.config import settings
from app.schemas.models import Ingredient, MLServiceResponse


async def recognize_ingredients(
    client: httpx.AsyncClient,
    image_bytes: bytes,
    content_type: str,
) -> list[Ingredient]:
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = await client.post(
        f"{settings.ml_service_url}/api/v1/ingredient-recognitions",
        json={
            "image": image_b64,
            "content_type": content_type,
        },
    )
    print(f"ML service status: {response.status_code}")
    print(f"ML service response: {response.text}")
    response.raise_for_status()
    result = MLServiceResponse(**response.json())
    return result.data.ingredients
