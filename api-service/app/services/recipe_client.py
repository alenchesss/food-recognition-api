from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Recipe Service")

RECIPES = [
    {
        "id": 1,
        "name": "Томатный суп",
        "description": "Классический томатный суп",
        "ingredients": ["tomato", "onion", "garlic", "cream"],
        "instructions": "Обжарь лук и чеснок. Добавь томаты, вари 20 мин. Блендер, добавь сливки.",
    },
    {
        "id": 2,
        "name": "Брускетта",
        "description": "Итальянский тост с томатами",
        "ingredients": ["tomato", "garlic", "basil", "bread"],
        "instructions": "Поджарь хлеб. Смешай томат, чеснок, базилик. Выложи на хлеб.",
    },
]


class SearchRequest(BaseModel):
    ingredients: list[str]


class MissingIngredient(BaseModel):
    name: str


class RecipeOut(BaseModel):
    id: int
    name: str
    description: str
    ingredients: list[str]
    missing_ingredients: list[MissingIngredient]
    instructions: str


class SearchResponse(BaseModel):
    recipes: list[RecipeOut]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/recipes/search", response_model=SearchResponse)
async def search_recipes(request: SearchRequest) -> SearchResponse:
    available = {i.lower() for i in request.ingredients}
    results = []

    for recipe in RECIPES:
        recipe_ingredients = set(recipe["ingredients"])
        if recipe_ingredients & available:
            missing = [MissingIngredient(name=i) for i in recipe_ingredients - available]
            results.append(
                RecipeOut(
                    id=recipe["id"],
                    name=recipe["name"],
                    description=recipe["description"],
                    ingredients=recipe["ingredients"],
                    missing_ingredients=missing,
                    instructions=recipe["instructions"],
                )
            )

    results.sort(key=lambda r: len(r.missing_ingredients))
    return SearchResponse(recipes=results)
