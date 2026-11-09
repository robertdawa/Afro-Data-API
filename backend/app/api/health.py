"""Liveness and readiness endpoints.

- ``GET /health``        the process is up (no dependencies touched). Used by Docker.
- ``GET /health/ready``  Postgres, Redis and object storage are all reachable.
"""

import logging
from collections.abc import Callable
from typing import Annotated, Literal

import redis
from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from app import __version__
from app.config import get_settings
from app.db import engine
from app.storage import make_s3_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

Check = Callable[[], None]


def check_database() -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def check_redis() -> None:
    client = redis.Redis.from_url(
        get_settings().redis_url, socket_connect_timeout=2, socket_timeout=2
    )
    try:
        client.ping()
    finally:
        client.close()


def check_object_storage() -> None:
    make_s3_client(timeout=2).head_bucket(Bucket=get_settings().s3_bucket_raw)


def get_checks() -> dict[str, Check]:
    """Dependency so tests can swap in fake checks."""
    return {
        "database": check_database,
        "redis": check_redis,
        "object_storage": check_object_storage,
    }


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str


class ReadinessResponse(BaseModel):
    status: Literal["ok", "degraded"]
    checks: dict[str, str]


@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@router.get(
    "/health/ready",
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadinessResponse}},
)
def ready(
    response: Response, checks: Annotated[dict[str, Check], Depends(get_checks)]
) -> ReadinessResponse:
    # Sync route: FastAPI runs it in a worker thread, so blocking checks are fine.
    results: dict[str, str] = {}
    for name, check in checks.items():
        try:
            check()
            results[name] = "ok"
        except Exception as exc:
            # Log the detail; return only the error type so hostnames etc. don't leak.
            logger.warning("readiness check %s failed: %s", name, exc)
            results[name] = f"error: {type(exc).__name__}"

    healthy = all(v == "ok" for v in results.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(status="ok" if healthy else "degraded", checks=results)
