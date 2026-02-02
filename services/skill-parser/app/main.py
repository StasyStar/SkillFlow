from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import parse
from app.core.config import settings
from app.core.database import engine
from app.models.database import Base

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Skill Parser API",
    description="API для парсинга резюме и извлечения навыков",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем эндпоинты
app.include_router(parse.router, prefix="/api/v1", tags=["parsing"])


@app.get("/")
async def root():
    return {"message": "Skill Parser API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
