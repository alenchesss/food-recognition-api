from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.responses import error_response
from app.dependencies import get_recipe_service, get_spoonacular_client
from app.schemas import (
    HealthData,
    HealthResponse,
    RecipeFindRequest,
    RecipeFindResponse,
)
from app.services.recipe import RecipeService
from app.services.spoonacular import SpoonacularError


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await get_spoonacular_client().close()


app = FastAPI(title="Recipe Service", lifespan=lifespan)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.get("/api/v1/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        data=HealthData(status="ok"),
    )


@app.post("/api/v1/recipes:find", response_model=RecipeFindResponse)
async def find_recipes(
    request: RecipeFindRequest,
    recipe_service: RecipeService = Depends(get_recipe_service),
) -> RecipeFindResponse:
    try:
        recipes = await recipe_service.find_by_ingredients(
            ingredient_names=[item.name for item in request.ingredients],
        )
    except SpoonacularError as exc:
        return error_response(
            status_code=502,
            code="ExternalServiceError",
            message=str(exc),
        )

    return RecipeFindResponse(data=recipes)
