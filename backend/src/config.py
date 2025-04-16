import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseSettings, Field, AnyHttpUrl

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    APP_NAME: str = "AgroHack App"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")

    YANDEX_API_KEY: str = Field(..., env="YANDEX_API_KEY")
    YANDEX_MODEL_URI: str = Field(..., env="YANDEX_MODEL_URI")

    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
