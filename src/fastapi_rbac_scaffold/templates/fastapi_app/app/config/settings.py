from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "{{ project_name }}"
    app_env: str = "local"
    app_timezone: str = "Asia/Shanghai"
    debug: bool = False

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/{{ package_name }}"
    )
    redis_url: str = "redis://127.0.0.1:6379/0"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7
    blacklist_token_expire_seconds: int = 60 * 60 * 24 * 7

    cors_allow_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    otel_enabled: bool = False
    otel_service_name: str = "{{ project_name }}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

