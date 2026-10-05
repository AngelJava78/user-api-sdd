"""Configuración de la aplicación leída de variables de entorno y `.env` (NFR-005)."""

from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Límite máximo de `limit` fijado por el contrato OpenAPI (ADR-0007).
CONTRACT_MAX_LIMIT = 100

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "users-api"
    log_level: LogLevel = "INFO"

    # SecretStr evita que la contraseña aparezca en repr() o en logs.
    database_url: SecretStr
    db_pool_size: int = Field(default=10, ge=1)
    db_max_overflow: int = Field(default=5, ge=0)
    db_pool_timeout_seconds: float = Field(default=5, gt=0)

    pagination_default_limit: int = Field(default=20, ge=1)
    pagination_max_limit: int = Field(default=100, ge=1, le=CONTRACT_MAX_LIMIT)

    shutdown_grace_seconds: float = Field(default=30, ge=0)
    readiness_db_timeout_seconds: float = Field(default=2, gt=0)

    @model_validator(mode="after")
    def _default_limit_within_max(self) -> Self:
        if self.pagination_default_limit > self.pagination_max_limit:
            msg = "PAGINATION_DEFAULT_LIMIT no puede superar PAGINATION_MAX_LIMIT"
            raise ValueError(msg)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
