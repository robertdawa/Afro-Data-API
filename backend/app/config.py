"""Application settings, read from environment variables (and .env in local dev)."""

from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Placeholder for local dev only; the validator below rejects it in staging/production.
DEFAULT_HASH_SECRET = "dev-only-change-me"  # noqa: S105

Environment = Literal["local", "test", "staging", "production"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Look in backend/ first, then the repo root, when running outside Docker.
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Africa Data Platform API"
    environment: Environment = "local"
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    database_url: str = "postgresql+psycopg://adp:adp@localhost:5432/adp"
    redis_url: str = "redis://localhost:6379/0"

    s3_endpoint_url: str | None = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: SecretStr = SecretStr("minioadmin")
    s3_region: str = "us-east-1"
    s3_bucket_raw: str = "adp-raw"
    s3_bucket_exports: str = "adp-exports"

    api_key_hash_secret: SecretStr = SecretStr(DEFAULT_HASH_SECRET)

    anthropic_api_key: SecretStr | None = None
    anthropic_model: str = "claude-sonnet-5-5"

    @property
    def is_deployed(self) -> bool:
        return self.environment in ("staging", "production")

    @model_validator(mode="after")
    def _reject_dev_secrets_when_deployed(self) -> Self:
        if self.is_deployed and (
            self.api_key_hash_secret.get_secret_value() == DEFAULT_HASH_SECRET
            or len(self.api_key_hash_secret.get_secret_value()) < 32
        ):
            raise ValueError(
                "API_KEY_HASH_SECRET must be set to a random value of at least 32 characters "
                f"when ENVIRONMENT={self.environment}"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
