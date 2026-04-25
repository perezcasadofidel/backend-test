from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Pincha Local API"
    environment: Literal["local", "dev", "test", "prod"] = "local"
    debug: bool = True
    api_prefix: str = "/api/local"

    innovasoft_base_url: str = "https://pruebareactjs.test-class.com/Api"
    innovasoft_timeout_seconds: float = 20.0

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "pincha_local"
    sesiones_collection: str = "sesiones"
    operaciones_collection: str = "operaciones"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
