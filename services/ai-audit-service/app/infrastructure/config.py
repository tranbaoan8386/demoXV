from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = Field(..., validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.1-flash-lite", validation_alias="GEMINI_MODEL")
    gemini_fallback_model: str = Field(default="gemini-2.0-flash", validation_alias="GEMINI_FALLBACK_MODEL")
    doc_processor_url: str = Field(default="http://doc-processor:8081", validation_alias="DOC_PROCESSOR_URL")
    database_url: str = Field(default="postgresql+psycopg://demoxv_admin:demoxv_secret_pass@postgres:5432/ai_audit_db?sslmode=disable", validation_alias="DATABASE_URL")
    auto_migrate: bool = Field(default=True, validation_alias="AUTO_MIGRATE")
    env: str = Field(default="development", validation_alias="ENV")


def get_settings() -> Settings:
    return Settings()
