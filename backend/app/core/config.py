from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables (and a local .env)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["local", "staging", "production"] = "local"

    project_name: str = "SmartPaperCheck Chatbot API"
    api_v1_prefix: str = "/api/v1"

    # Comma-separated in the environment, e.g. "http://localhost:5173,https://app.example.com".
    cors_allow_origins: str = ""

    # DATABASE_URL is the pooled/runtime connection. DIRECT_URL (Supabase only) is the direct
    # connection used for migrations; unset locally, where migrations use DATABASE_URL.
    database_url: str
    direct_url: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    @property
    def migration_url(self) -> str:
        return self.direct_url or self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
