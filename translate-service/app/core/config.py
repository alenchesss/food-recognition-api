from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    groq_api_url: str = "https://api.groq.com/openai/v1"

    class Config:
        env_file = ".env"


settings = Settings()
