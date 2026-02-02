from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Настройки приложения
    APP_NAME: str = "Skill Parser"
    DEBUG: bool = False

    # Настройки БД
    DATABASE_URL: str = "postgresql://skillflow:skillflow@localhost:5432/skillflow"

    # Настройки NLP
    SPACY_MODEL: str = "en_core_web_sm"

    # Настройки файлов
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".doc", ".txt"]

    # Redis для кэширования моделей (сделайте опциональным)
    REDIS_URL: Optional[str] = None  # Было: "redis://localhost:6379/0"

    # Добавьте эти поля из вашего .env, чтобы не было ошибок:
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    ELASTICSEARCH_URL: Optional[str] = None
    SCRAPING_ENABLED: bool = False
    EMAIL_ENABLED: bool = False
    CACHE_TTL_RESUME: int = 3600
    MAX_ANALYSIS_PER_DAY: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"
        env_file_encoding = "utf-8"


settings = Settings()
