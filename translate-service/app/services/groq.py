import json

import httpx

from app.core.config import settings
from app.schemas.models import Recipe

_SYSTEM_PROMPT = """Ты профессиональный переводчик кулинарных текстов.
Переводи с английского на русский точно и естественно.
Сохраняй кулинарную терминологию. Не добавляй пояснений.

Тебе придёт JSON-массив объектов рецептов. Переведи только следующие поля:
- title — название рецепта
- missing_ingredients[].name — только поле name каждого ингредиента
- instructions[].description — только поле description каждого шага

Не трогай поля: id, image, used_ingredients_count, amount, unit, number.
Структуру JSON сохраняй точно.
Верни только валидный JSON объект вида {"recipes": [...]}, без пояснений и markdown-блоков."""


async def translate_recipes(
    client: httpx.AsyncClient,
    recipes: list[Recipe],
) -> list[Recipe]:
    if not recipes:
        return []

    recipes_json = json.dumps(
        [r.model_dump() for r in recipes],
        ensure_ascii=False,
        indent=2,
    )

    response = await client.post(
        f"{settings.groq_api_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": recipes_json},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        },
    )
    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]
    parsed = json.loads(content)

    if isinstance(parsed, dict):
        translated_list = parsed.get("recipes", list(parsed.values())[0])
    else:
        translated_list = parsed

    return [Recipe(**item) for item in translated_list]
