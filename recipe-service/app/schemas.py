from pydantic import BaseModel, Field


# Request


class IngredientItem(BaseModel):
    name: str


class RecipeFindRequest(BaseModel):
    ingredients: list[IngredientItem] = Field(..., min_length=1)


# Response


class MissingIngredientItem(BaseModel):
    name: str
    amount: float
    unit: str


class RecipeStep(BaseModel):
    number: int
    description: str


class RecipeItem(BaseModel):
    id: int
    title: str
    image: str | None
    used_ingredients_count: int
    missing_ingredients: list[MissingIngredientItem]
    instructions: list[RecipeStep]


class RecipeFindResponse(BaseModel):
    data: list[RecipeItem]


class HealthData(BaseModel):
    status: str


class HealthResponse(BaseModel):
    data: HealthData
