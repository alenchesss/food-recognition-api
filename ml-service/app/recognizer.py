import base64
import json
from dataclasses import dataclass

import httpx

from app.config import Settings


@dataclass(frozen=True)
class RecognizedIngredient:
    name: str


class IngredientRecognizer:
    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.groq_api_key
        self._api_url = settings.groq_api_url

    def predict(
        self,
        *,
        image_bytes: bytes,
        content_type: str,
    ) -> list[RecognizedIngredient]:
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self._api_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "Identify all food products and ingredients visible in this image. "
                                        'Return strictly a JSON object in format: {"ingredients":[{"name":"bread"},{"name":"cheese"}]}. '
                                        "No markdown, no explanations, no extra text."
                                    ),
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{content_type};base64,{image_base64}",
                                    },
                                },
                            ],
                        }
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()

        raw_text = response.json()["choices"][0]["message"]["content"]
        return self._parse_response(raw_text)

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
