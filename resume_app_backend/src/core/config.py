from functools import lru_cache
from typing import List, Optional

from pydantic import Field, PostgresDsn, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


# PUBLIC_INTERFACE
class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment variables:
    - DATABASE_URL: PostgreSQL connection string (e.g., postgres://user:pass@host:port/db)
    - BACKEND_CORS_ORIGINS: Comma-separated list of allowed CORS origins (e.g., https://app.example.com,http://localhost:3000)
    - JOB_SOURCE_API_KEYS: Comma-separated list of API keys allowed to push jobs to the system
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    DATABASE_URL: PostgresDsn = Field(..., description="PostgreSQL connection URL")

    # CORS
    BACKEND_CORS_ORIGINS: Optional[str] = Field(
        default=None,
        description="Comma-separated list of allowed origins for CORS",
    )

    # Job source API keys
    JOB_SOURCE_API_KEYS: Optional[str] = Field(
        default=None,
        description="Comma-separated list of API keys for job source integrations",
    )

    # PUBLIC_INTERFACE
    def cors_origins(self) -> List[str]:
        """Return list of configured CORS origins (empty means allow none)."""
        if not self.BACKEND_CORS_ORIGINS:
            return []
        # Clean and split by comma, ignore empty parts
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    # PUBLIC_INTERFACE
    def job_source_api_keys(self) -> List[str]:
        """Return list of configured job source API keys (empty if not set)."""
        if not self.JOB_SOURCE_API_KEYS:
            return []
        return [key.strip() for key in self.JOB_SOURCE_API_KEYS.split(",") if key.strip()]


# PUBLIC_INTERFACE
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and cache application settings from environment/.env."""
    try:
        return Settings()  # type: ignore[call-arg]
    except ValidationError as exc:
        # Raise a clear error to help during boot
        raise RuntimeError(f"Invalid configuration: {exc}") from exc
