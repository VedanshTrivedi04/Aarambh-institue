"""
app/core/config.py
------------------
Environment-driven configuration using pydantic-settings.
All values are read from environment variables or a .env file.
No secrets are hard-coded here.
"""

from functools import lru_cache
from typing import Any, Literal

from pydantic import AnyHttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    APP_ENV: Literal["dev", "staging", "prod"] = "dev"
    DEBUG: bool = False
    APP_NAME: str = "Aarambh Institute ERP"
    APP_VERSION: str = "0.1.0"

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    DATABASE_URL: str  # required — postgresql+asyncpg://...
    TEST_DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            # Render and other clouds give postgres:// or postgresql://
            if v.startswith("postgres://"):
                v = "postgresql+asyncpg://" + v[len("postgres://"):]
            elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
                v = "postgresql+asyncpg://" + v[len("postgresql://"):]
            
            # asyncpg does not accept ?sslmode=..., it accepts ?ssl=...
            if "sslmode=require" in v:
                v = v.replace("sslmode=require", "ssl=require")
            elif "sslmode=verify-full" in v or "sslmode=verify-ca" in v:
                # Fallback to ssl=require which asyncpg supports natively
                v = v.replace("sslmode=verify-full", "ssl=require").replace("sslmode=verify-ca", "ssl=require")
        return v

    # ------------------------------------------------------------------ #
    # JWT / Auth
    # ------------------------------------------------------------------ #
    SECRET_KEY: str  # required — minimum 32 chars
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------ #
    # Redis
    # ------------------------------------------------------------------ #
    REDIS_URL: str = "redis://localhost:6379/0"

    # ------------------------------------------------------------------ #
    # CORS
    # Accepts comma-separated string OR JSON array string:
    # "http://localhost:3000,https://app.aarambh.in" or '["http://localhost:3000"]'
    # Also allows regex matching for preview deployments on Vercel
    # ------------------------------------------------------------------ #
    CORS_ORIGINS: list[str] | str = ["http://localhost:3000", "http://127.0.0.1:3000"]
    CORS_ORIGIN_REGEX: str | None = r"https:\/\/.*\.vercel\.app"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: Any) -> list[str]:
        if isinstance(v, list):
            return [str(origin).strip() for origin in v if str(origin).strip()]
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    import json
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(origin).strip() for origin in parsed if str(origin).strip()]
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return ["http://localhost:3000"]

    # ------------------------------------------------------------------ #
    # File storage
    # ------------------------------------------------------------------ #
    STORAGE_BACKEND: Literal["local", "s3"] = "local"
    LOCAL_STORAGE_PATH: str = "./uploads"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_S3_BUCKET: str | None = None
    AWS_S3_REGION: str = "ap-south-1"

    # ------------------------------------------------------------------ #
    # Celery / background tasks
    # ------------------------------------------------------------------ #
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ------------------------------------------------------------------ #
    # Rate limiting
    # ------------------------------------------------------------------ #
    RATE_LIMIT_AUTH_RPM: int = 10  # requests per minute per IP

    # ------------------------------------------------------------------ #
    # Razorpay (online fee payments)
    # ------------------------------------------------------------------ #
    RAZORPAY_KEY_ID: str | None = None
    RAZORPAY_KEY_SECRET: str | None = None
    RAZORPAY_WEBHOOK_SECRET: str | None = None

    # ------------------------------------------------------------------ #
    # Guards
    # ------------------------------------------------------------------ #
    @model_validator(mode="after")
    def production_guards(self) -> "Settings":
        if self.APP_ENV == "prod":
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production")
            if len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return self


@lru_cache
def get_settings() -> Settings:
    """Cached singleton — import and call this anywhere you need settings."""
    return Settings()
