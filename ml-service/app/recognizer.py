import base64
import json
from dataclasses import dataclass

from openai import OpenAI

from app.config import Settings


@dataclass(frozen=True)
class RecognizedIngredient:
    name: str


class IngredientRecognizer:
    def __init__(self, settings: Settings) -> None:
        self._client = OpenAI(
            api_key=settings.yandex_api_key,
            base_url=settings.yandex_base_url,
            project=settings.yandex_project_id,
        )
        self._prompt_id = settings.yandex_prompt_id

    def predict(
        self,
        *,
        image_bytes: bytes,
        content_type: str,
    ) -> list[RecognizedIngredient]:
        image_base64 = self._encode_image(image_bytes)

        response = self._client.responses.create(
            prompt={"id": self._prompt_id},
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Определи продукты на изображении. "
                                "Верни строго JSON-объект формата "
                                '{"ingredients":[{"name":"bread"},{"name":"cheese"}]}. '
                                "Без markdown, без пояснений, без лишнего текста."
                            ),
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:{content_type};base64,{image_base64}",
                        },
                    ],
                }
            ],
        )

        return self._parse_response(response.output_text)

    @staticmethod
    def _encode_image(image_bytes: bytes) -> str:
        return base64.b64encode(image_bytes).decode("utf-8")

    @staticmethod
    def _parse_response(raw_text: str) -> list[RecognizedIngredient]:
        text = raw_text.strip()

        if not text:
            return []

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Model returned invalid JSON") from exc

        if not isinstance(parsed, dict):
            raise ValueError("Model response must be an object")

        ingredients = parsed.get("ingredients")
        if ingredients is None:
            raise ValueError("Model response must contain 'ingredients' field")

        if not isinstance(ingredients, list):
            raise ValueError("'ingredients' field must be a list")

        result: list[RecognizedIngredient] = []

        for item in ingredients:
            if not isinstance(item, dict):
                raise ValueError("Each ingredient must be an object")

            name = item.get("name")
            if not isinstance(name, str):
                raise ValueError("Ingredient field 'name' must be a string")

            normalized_name = name.strip()
            if not normalized_name:
                continue

            result.append(RecognizedIngredient(name=normalized_name))

        return result
