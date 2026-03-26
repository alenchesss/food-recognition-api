import httpx

from app.core.config import settings

ML_SERVICE_URL = settings.ml_service_url
RECIPE_SERVICE_URL = settings.recipe_service_url


def get_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=30.0)
