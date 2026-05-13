from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str


class MLServiceIngredientData(BaseModel):
    ingredients: list[Ingredient]


class MLServiceResponse(BaseModel):
    data: MLServiceIngredientData


class MissingIngredient(BaseModel):
    name: str
    amount: float
    unit: str


class InstructionStep(BaseModel):
    number: int
    description: str


class Recipe(BaseModel):
    id: int
    title: str
    image: str | None
    used_ingredients_count: int
    missing_ingredients: list[MissingIngredient]
    instructions: list[InstructionStep]


class RecognizeResponse(BaseModel):
    detected_ingredients: list[Ingredient]
    recipes: list[Recipe]


class HealthResponse(BaseModel):
    status: str
    services: dict[str, str]


class HealthData(BaseModel):
    status: str
    services: dict[str, str]
