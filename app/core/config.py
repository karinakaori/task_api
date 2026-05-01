from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Task API"
    app_description: str = "Servico de gerenciamento de tarefas com FastAPI."
    app_version: str = "1.0.0"
    environment: Literal["development", "test", "production"] = "development"

    database_url: str = "sqlite:///./tasks.db"
    rate_limit_max_requests: int = Field(default=30, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)

    cors_origins: list[str] = ["http://localhost:8000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
