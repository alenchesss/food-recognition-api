import httpx
from fastapi import APIRouter

from app.core.config import settings
from app.schemas.models import HealthData

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
async def health() -> dict:
    services: dict[str, str] = {}

    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in [
            ("ml-service", settings.ml_service_url),
            ("recipe-service", settings.recipe_service_url),
            ("translate-service", settings.translate_service_url),
        ]:
            try:
                resp = await client.get(f"{url}/api/v1/health")
                services[name] = "ok" if resp.status_code == 200 else "degraded"
            except Exception:
                services[name] = "unavailable"

    overall = "ok" if all(v == "ok" for v in services.values()) else "degraded"
    return {"data": HealthData(status=overall, services=services).model_dump()}
