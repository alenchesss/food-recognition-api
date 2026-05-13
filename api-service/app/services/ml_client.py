import base64

import httpx

from app.core.config import settings
from app.schemas.models import Ingredient


async def recognize_ingredients(
    client: httpx.AsyncClient,
    image_bytes: bytes,
    content_type: str,
) -> list[Ingredient]:
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    url = f"{settings.ml_service_url}/api/v1/ingredient-recognitions"
    print(f"[ML CLIENT] URL: {url}", flush=True)
    print(f"[ML CLIENT] base64 length: {len(image_b64)}", flush=True)
    print(f"[ML CLIENT] content_type: {content_type}", flush=True)

    response = await client.post(
        url,
        json={
            "image": image_b64,
            "content_type": content_type,
        },
    )

    print(f"[ML CLIENT] response.status_code: {response.status_code}", flush=True)
    print(f"[ML CLIENT] response.headers: {dict(response.headers)}", flush=True)
    print(f"[ML CLIENT] response.text (first 500 chars): {response.text[:500]!r}", flush=True)
    print(f"[ML CLIENT] response.content length: {len(response.content)}", flush=True)

    response.raise_for_status()
    data = response.json()
    return [Ingredient(name=i["name"], confidence=1.0) for i in data["data"]["ingredients"]]
