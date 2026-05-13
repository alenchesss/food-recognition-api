from pydantic import BaseModel


# входящий рецепт
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
    image: str | None = None
    used_ingredients_count: int
    missing_ingredients: list[MissingIngredient]
    instructions: list[InstructionStep]


# запрос
class TranslateRecipesRequest(BaseModel):
    recipes: list[Recipe]


# ответ
class TranslateRecipesData(BaseModel):
    recipes: list[Recipe]


class TranslateRecipesResponse(BaseModel):
    data: TranslateRecipesData


# health
class HealthData(BaseModel):
    status: str
    services: dict[str, str]
