from contextlib import asynccontextmanager

import httpx

from app.core.config import settings

ML_SERVICE_URL = settings.ml_service_url
RECIPE_SERVICE_URL = settings.recipe_service_url


@asynccontextmanager
async def get_http_client():
    async with httpx.AsyncClient(timeout=120.0) as client:
        yield client
