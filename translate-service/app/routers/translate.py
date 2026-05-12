import httpx
from fastapi import APIRouter, HTTPException

from app.schemas.models import (
    TranslateRecipesData,
    TranslateRecipesRequest,
    TranslateRecipesResponse,
)
from app.services.groq import translate_recipes

router = APIRouter(prefix="/api/v1", tags=["translate"])


@router.post("/recipes:translate", response_model=TranslateRecipesResponse)
async def translate_recipes_handler(
    body: TranslateRecipesRequest,
) -> TranslateRecipesResponse:
    if not body.recipes:
        return TranslateRecipesResponse(data=TranslateRecipesData(recipes=[]))

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            translated = await translate_recipes(client, body.recipes)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка Groq: {type(e).__name__}: {e}",
            ) from e

    return TranslateRecipesResponse(data=TranslateRecipesData(recipes=translated))
