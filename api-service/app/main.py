from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
 
from app.routers import health, recognize
 
app = FastAPI(
    title="Food Recognition API",
    description="Загрузи фото еды — получи ингредиенты и рецепты.",
    version="0.1.0",
)
 
# В проде прописать конкретный домен фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
app.include_router(health.router)
app.include_router(recognize.router)
 
 
