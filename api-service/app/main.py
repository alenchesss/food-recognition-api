from fastapi import FastAPI

from app.routers import health, recognize

app = FastAPI(
    title="Food Recognition API",
    description="Загрузи фото еды — получи ингредиенты и рецепты.",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(recognize.router)
