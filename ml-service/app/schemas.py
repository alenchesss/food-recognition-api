from pydantic import BaseModel, Field


class IngredientRecognitionRequest(BaseModel):
    image: str = Field(..., min_length=1)
    content_type: str = Field(..., min_length=1)


class IngredientItem(BaseModel):
    name: str


class IngredientRecognitionData(BaseModel):
    ingredients: list[IngredientItem]


class IngredientRecognitionResponse(BaseModel):
    data: IngredientRecognitionData


class HealthData(BaseModel):
    status: str


class HealthResponse(BaseModel):
    data: HealthData
