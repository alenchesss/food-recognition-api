from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str


class MLServiceIngredientData(BaseModel):
    ingredients: list[Ingredient]


class MLServiceResponse(BaseModel):
    data: MLServiceIngredientData


class MissingIngredient(BaseModel):
    name: str


class Recipe(BaseModel):
    id: int
    name: str
    description: str
    ingredients: list[str]
    missing_ingredients: list[MissingIngredient]
    instructions: str


class RecognizeResponse(BaseModel):
    detected_ingredients: list[Ingredient]
    recipes: list[Recipe]


class HealthResponse(BaseModel):
    status: str
    services: dict[str, str]


class HealthData(BaseModel):
    status: str
    services: dict[str, str]
