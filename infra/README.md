# Infrastructure

## Local stack

[`docker-compose.yml`](docker-compose.yml) defines the local services. Run it from the **repo root** with `docker compose up --build`. The root [`compose.yaml`](../compose.yaml) includes this file and resolves its paths from the root.

| Service | Image | Purpose | Host port |
|---|---|---|---|
| postgres | `pgvector/pgvector:pg16` | Main database (PostgreSQL 16 + pgvector) | 5432 |
| redis | `redis:7-alpine` | Task queue broker, rate limits | 6379 |
| minio | `minio/minio` | S3-compatible object storage | 9000 (API), 9001 (console) |
| minio-init | `minio/mc` | One-shot: creates the `adp-raw` and `adp-exports` buckets | none |
| backend | `./backend` | FastAPI; runs `alembic upgrade head` on start | 8000 |
| frontend | `./frontend` | Next.js dev server | 3000 |

The Postgres user in local dev is a superuser, and superusers bypass row-level security. From Phase 3 the app and the AI SQL tool connect as separate non-superuser roles, so RLS is actually enforced.

## Notes on MinIO

MinIO stopped publishing new community Docker images in late 2025. The `latest` tags still work for local development. We only use the S3 API, so swapping in another S3-compatible store (Garage, SeaweedFS, Ceph RGW, or AWS S3 in production) needs only a change of `S3_ENDPOINT_URL` and credentials.

## Deployment

The deployment guide is written in **Phase 10**.
