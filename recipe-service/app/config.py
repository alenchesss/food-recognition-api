from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    spoonacular_api_key: str
    spoonacular_base_url: str = "https://api.spoonacular.com"

    database_url: str

    class Config:
        env_file = ".env"


def load_settings() -> Settings:
    return Settings()
