from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# PUBLIC_INTERFACE
class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment variables:
    - DATABASE_URL: PostgreSQL connection string (e.g., postgres://user:pass@host:port/db)
    - POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB:
      Used to construct a fallback DSN when DATABASE_URL is not provided.
    - BACKEND_CORS_ORIGINS: Comma-separated list of allowed CORS origins (e.g., https://app.example.com,http://localhost:3000)
    - JOB_SOURCE_API_KEYS: Comma-separated list of API keys allowed to push jobs to the system
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database - optional to allow app boot without DB for health/docs
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection URL; if absent, a fallback is constructed from POSTGRES_* vars.",
    )
    # Defaults are None to avoid fabricating unusable DSNs. We'll construct only when all pieces exist.
    POSTGRES_USER: Optional[str] = Field(default=None, description="PostgreSQL username for fallback DSN")
    POSTGRES_PASSWORD: Optional[str] = Field(default=None, description="PostgreSQL password for fallback DSN")
    POSTGRES_HOST: Optional[str] = Field(default=None, description="PostgreSQL host for fallback DSN")
    POSTGRES_PORT: Optional[int] = Field(default=None, description="PostgreSQL port for fallback DSN")
    POSTGRES_DB: Optional[str] = Field(default=None, description="PostgreSQL database name for fallback DSN")

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
        """Return list of configured CORS origins; falls back to http://localhost:3000."""
        if not self.BACKEND_CORS_ORIGINS:
            return ["http://localhost:3000"]
        # Clean and split by comma, ignore empty parts
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    # PUBLIC_INTERFACE
    def job_source_api_keys(self) -> List[str]:
        """Return list of configured job source API keys (empty if not set)."""
        if not self.JOB_SOURCE_API_KEYS:
            return []
        return [key.strip() for key in self.JOB_SOURCE_API_KEYS.split(",") if key.strip()]

    # PUBLIC_INTERFACE
    def database_dsn(self) -> Optional[str]:
        """Return a usable PostgreSQL DSN string if available; otherwise None.

        Priority:
        1) Use DATABASE_URL if provided.
        2) Construct DSN from POSTGRES_* values if all are present.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_HOST, self.POSTGRES_PORT, self.POSTGRES_DB]):
            return (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return None


# PUBLIC_INTERFACE
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and cache application settings from environment/.env without forcing DB validation.

    Intentionally avoids raising on missing DATABASE_URL/POSTGRES_* so the app can start without DB.
    """
    # BaseSettings already validates field types; we only avoid wrapping with RuntimeError
    return Settings()  # type: ignore[call-arg]
