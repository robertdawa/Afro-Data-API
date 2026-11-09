"""S3-compatible object storage client (MinIO locally)."""

from typing import Any

import boto3
from botocore.config import Config

from app.config import Settings, get_settings


def make_s3_client(settings: Settings | None = None, *, timeout: float = 5.0) -> Any:
    s = settings or get_settings()
    return boto3.client(
        "s3",
        endpoint_url=s.s3_endpoint_url,
        aws_access_key_id=s.s3_access_key,
        aws_secret_access_key=s.s3_secret_key.get_secret_value(),
        region_name=s.s3_region,
        config=Config(
            connect_timeout=timeout,
            read_timeout=timeout,
            retries={"max_attempts": 1},
            s3={"addressing_style": "path"},
        ),
    )
