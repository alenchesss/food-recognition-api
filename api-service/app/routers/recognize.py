from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.core.http_client import get_http_client
from app.schemas.models import RecognizeResponse
from app.services.ml_client import recognize_ingredients
from app.services.recipe_client import get_recipes_by_ingredients

router = APIRouter(prefix="/api/v1", tags=["recognition"])


@router.post("/recognize", response_model=RecognizeResponse)
async def recognize(image: UploadFile = File(...)) -> RecognizeResponse:
    # Проверяем тип файла
    if image.content_type not in settings.allowed_image_types:
        raise HTTPException(
            status_code=400,
            detail=f"Неверный тип файла: {image.content_type}",
        )

    # Проверяем размер
    image_bytes = await image.read()
    if len(image_bytes) > settings.max_image_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой. Максимум: {settings.max_image_size_mb}MB",
        )

    async with get_http_client() as client:
        # отправляем картинку в ml-service
        try:
            ingredients = await recognize_ingredients(client, image_bytes, image.content_type)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Ошибка ml-service: {e}") from e

        if not ingredients:
            return RecognizeResponse(detected_ingredients=[], recipes=[])

        # отправляем ингредиенты в recipe-service
        ingredient_names = [i.name for i in ingredients]
        try:
            recipes = await get_recipes_by_ingredients(client, ingredient_names)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Ошибка recipe-service: {e}") from e

    return RecognizeResponse(detected_ingredients=ingredients, recipes=recipes)
