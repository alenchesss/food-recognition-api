from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ml_service_url: str = "http://localhost:8001"
    recipe_service_url: str = "http://recipe-service:8002"
    max_image_size_mb: int = 10
    allowed_image_types: list[str] = ["image/jpeg", "image/png", "image/webp"]

    class Config:
        env_file = ".env"


settings = Settings()
