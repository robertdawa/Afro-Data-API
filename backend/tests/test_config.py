from typing import Any

import pytest
from pydantic import ValidationError

from app.config import Settings

STRONG_SECRET = "x" * 48


def make(**kwargs: Any) -> Settings:
    # _env_file=None: ignore any developer .env so tests are deterministic.
    return Settings(_env_file=None, **kwargs)


def test_local_allows_dev_secret() -> None:
    assert not make(environment="local").is_deployed


@pytest.mark.parametrize("env", ["staging", "production"])
def test_deployed_rejects_default_secret(env: str) -> None:
    with pytest.raises(ValidationError, match="API_KEY_HASH_SECRET"):
        make(environment=env)


def test_deployed_rejects_short_secret() -> None:
    with pytest.raises(ValidationError, match="API_KEY_HASH_SECRET"):
        make(environment="production", api_key_hash_secret="short")


def test_deployed_accepts_strong_secret() -> None:
    assert make(environment="production", api_key_hash_secret=STRONG_SECRET).is_deployed


def test_cors_origins_parsed_from_json_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", '["https://a.example","https://b.example"]')
    assert make().cors_origins == ["https://a.example", "https://b.example"]
