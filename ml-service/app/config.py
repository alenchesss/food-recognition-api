import os

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()


class Settings(BaseModel):
    yandex_api_key: str
    yandex_project_id: str
    yandex_prompt_id: str
    yandex_base_url: str = "https://ai.api.cloud.yandex.net/v1"


def load_settings() -> Settings:
    return Settings(
        yandex_api_key=_get_required_env("YANDEX_API_KEY"),
        yandex_project_id=_get_required_env("YANDEX_PROJECT_ID"),
        yandex_prompt_id=_get_required_env("YANDEX_PROMPT_ID"),
        yandex_base_url=os.getenv(
            "YANDEX_BASE_URL", "https://ai.api.cloud.yandex.net/v1"
        ),
    )


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value
