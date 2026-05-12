import httpx
from fastapi import APIRouter

from app.core.config import settings
from app.schemas.models import HealthData

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
async def health() -> dict:
    services: dict[str, str] = {}

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(
                f"{settings.groq_api_url}/models",
                headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            )
            services["groq"] = "ok" if resp.status_code == 200 else "degraded"
        except Exception:
            services["groq"] = "unavailable"

    overall = "ok" if all(v == "ok" for v in services.values()) else "degraded"
    return {"data": HealthData(status=overall, services=services).model_dump()}
