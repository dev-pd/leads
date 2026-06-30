"""Application configuration loaded from environment variables.

Mirrors the Zod-validated `env.ts` pattern from the reference repo: a single
typed settings object, validated once at import, injected everywhere else.
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Core ---
    app_name: str = "Leads API"
    environment: Literal["development", "production", "test"] = "development"
    api_prefix: str = "/api"
    # Comma-separated list of allowed CORS origins (the Next.js app).
    cors_origins: str = "http://localhost:3000"

    # --- Database ---
    database_url: str = "postgresql+psycopg://leads:leads@localhost:5432/leads"

    # --- Auth (JWT) ---
    jwt_secret: str = "dev-insecure-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24  # 24h

    # Seed attorney account (created by scripts/seed.py).
    attorney_email: str = "attorney@example.com"
    attorney_password: str = "changeme123"
    attorney_name: str = "Default Attorney"

    # --- Email (Resend) ---
    resend_api_key: str = ""  # empty -> send is skipped, payload logged only
    email_from: str = "onboarding@resend.dev"
    # Where the internal attorney notification is delivered.
    notify_attorney_email: str = "attorney@example.com"

    # --- Storage ---
    storage_backend: Literal["local", "s3"] = "local"
    local_storage_dir: str = "/data/resumes"
    # S3 / MinIO (used only when storage_backend == "s3")
    s3_endpoint_url: str = "http://localhost:9000"
    s3_bucket: str = "resumes"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_region: str = "us-east-1"

    # --- Upload constraints ---
    max_upload_mb: int = 10
    allowed_resume_types: str = "application/pdf"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allowed_resume_types_list(self) -> list[str]:
        return [t.strip() for t in self.allowed_resume_types.split(",") if t.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
