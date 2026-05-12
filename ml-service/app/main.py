import base64
import binascii

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.core.exceptions import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.dependencies import get_recognizer
from app.recognizer import IngredientRecognizer
from app.schemas import (
    HealthData,
    HealthResponse,
    IngredientItem,
    IngredientRecognitionData,
    IngredientRecognitionRequest,
    IngredientRecognitionResponse,
)

app = FastAPI(title="ML Service")

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

image_types = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

max_size = 10 * 1024 * 1024


@app.get("/api/v1/health", response_model=HealthResponse)
async def health() -> HealthResponse:
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
    return HealthResponse(data=HealthData(status=overall, services=services))


@app.post(
    "/api/v1/ingredient-recognitions",
    response_model=IngredientRecognitionResponse,
)
async def recognize(
    request: IngredientRecognitionRequest,
    recognizer: IngredientRecognizer = Depends(get_recognizer),
) -> IngredientRecognitionResponse:
    print(f"GOT ML REQUEST, content_type: {request.content_type}, image size: {len(request.image)}")
    if request.content_type not in image_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported content_type",
        )

    try:
        image_bytes = base64.b64decode(request.image, validate=True)
    except binascii.Error as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid base64 image",
        ) from exc

    if len(image_bytes) > max_size:
        raise HTTPException(
            status_code=400,
            detail="Image is too large",
        )
    try:
        predictions = recognizer.predict(
            image_bytes=image_bytes,
            content_type=request.content_type,
        )
    except Exception as exc:
        print(f"PREDICT FAILED: {type(exc).__name__}: {exc}", flush=True)
        raise
    print(f"PREDICT OK, count={len(predictions)}", flush=True)

    return IngredientRecognitionResponse(
        data=IngredientRecognitionData(
            ingredients=[IngredientItem(name=item.name) for item in predictions]
        )
    )
