import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import __version__
from app.api import health


def _ok() -> None:
    return None


def _fail() -> None:
    raise ConnectionError("could not reach db.internal:5432")


def test_health_is_ok_without_dependencies(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "version": __version__}


def test_ready_ok_when_all_checks_pass(app: FastAPI, client: TestClient) -> None:
    app.dependency_overrides[health.get_checks] = lambda: {"a": _ok, "b": _ok}
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "checks": {"a": "ok", "b": "ok"}}


def test_ready_503_when_a_check_fails(app: FastAPI, client: TestClient) -> None:
    app.dependency_overrides[health.get_checks] = lambda: {"db": _fail, "redis": _ok}
    resp = client.get("/health/ready")
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["redis"] == "ok"
    # Only the error type is exposed, never the message (which may contain hostnames).
    assert body["checks"]["db"] == "error: ConnectionError"
    assert "db.internal" not in resp.text


def test_default_checks_cover_all_services() -> None:
    assert set(health.get_checks()) == {"database", "redis", "object_storage"}


def test_openapi_docs_are_served(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    spec = client.get("/openapi.json").json()
    assert "/health" in spec["paths"]
    assert "/health/ready" in spec["paths"]


@pytest.mark.integration
def test_ready_against_real_services(client: TestClient) -> None:
    """Needs real Postgres, Redis and MinIO: runs in CI and inside docker compose."""
    resp = client.get("/health/ready")
    assert resp.status_code == 200, resp.json()
