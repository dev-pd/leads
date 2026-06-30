"""Application configuration loaded from environment variables."""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Core ---
    app_name: str = "Leads API"
    app_version: str = "1.0.0"
    environment: Literal["development", "production", "test"] = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api"
    # Comma-separated list of allowed CORS origins (the Next.js app).
    cors_origins: str = "http://localhost:3000"

    # --- Database ---
    database_url: str = "postgresql+psycopg://leads:leads@localhost:5432/leads"

    # --- Auth (JWT) ---
    # Required — no insecure default; must be provided via env (see .env.example).
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24  # 24h

    # Seed attorney account — required, provided via env (no hardcoded credentials).
    attorney_email: str
    attorney_password: str
    attorney_name: str

    # --- Email (Resend) — optional; empty values disable sending ---
    resend_api_key: str = ""  # empty -> send is skipped, payload logged only
    email_from: str = ""
    notify_attorney_email: str = ""

    # --- AI resume summary (Anthropic API) ---
    anthropic_api_key: str = ""  # empty -> summary generation is skipped
    # Sonnet is the cost-effective default for summarization; override per env.
    claude_model: str = "claude-sonnet-5"

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
