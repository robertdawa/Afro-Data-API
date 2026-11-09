# Africa Data Platform (working name)

Clean, ready-to-use African data on **mining, tourism, agriculture, finance and healthcare**, delivered three ways:

- **REST API** with scoped API keys
- **AI chat**: ask questions in plain English and get answers, tables and charts, with sources
- **Downloads**: CSV, Excel and Parquet

The first market is Botswana and the SADC region. The data model covers all 54 African countries.

The full product and technical spec is in [SPEC.md](SPEC.md).

## Status

| Phase | Scope | Status |
|---|---|---|
| 1 | Skeleton: repo layout, Docker Compose, health check, Next.js shell, CI | ✅ done |
| 2 | Data model + catalogue | next |
| 3 | Auth, orgs, API keys, permissions | |
| 4 | Data API | |
| 5 | Pipeline (FAOSTAT, World Bank) | |
| 6 | AI chat | |
| 7 | Web dashboard | |
| 8 | Billing | |
| 9 | Admin panel + docs site | |
| 10 | Hardening | |

## Quick start (Docker)

Prerequisites: [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine with Compose v2.24+) and Git.

```bash
git clone https://github.com/robertdawa/Afro-Data-API.git
cd Afro-Data-API
cp .env.example .env        # optional: every setting has a working local default
docker compose up --build
```

The first build takes a few minutes. When it's up:

| What | URL |
|---|---|
| Web app | <http://localhost:3000> |
| API | <http://localhost:8000> |
| API docs (OpenAPI) | <http://localhost:8000/docs> |
| Liveness | <http://localhost:8000/health> |
| Readiness (DB, Redis, storage) | <http://localhost:8000/health/ready> |
| MinIO console | <http://localhost:9001> (user `minioadmin`, password `minioadmin`) |

The home page shows a green dot when the web app can reach the API.

Code changes in `backend/` and `frontend/` hot-reload inside the containers.

Useful commands:

```bash
docker compose exec backend pytest                 # all backend tests, against real services
docker compose exec backend alembic revision --autogenerate -m "describe change"
docker compose exec backend alembic upgrade head
docker compose down          # stop
docker compose down -v       # stop and delete all local data
```

## Running without Docker

You still need Postgres 16 (with pgvector), Redis and an S3-compatible store. The easiest way is to start only those from Compose:

```bash
docker compose up -d postgres redis minio minio-init
```

**Backend** (Python 3.12):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend** (Node 22):

```bash
cd frontend
npm install
npm run dev
```

Settings are read from `.env` in the repo root (see [.env.example](.env.example)).

## Quality checks

These are the same checks CI runs on every push ([.github/workflows/ci.yml](.github/workflows/ci.yml)):

```bash
# backend/
ruff check . && ruff format --check .
mypy
pytest --cov                          # needs Postgres, Redis and MinIO running
pytest -m "not integration"           # unit tests only, no services needed

# frontend/
npm run lint
npm run build
```

## Repository layout

```
backend/          FastAPI app
  app/
    api/          routes (health check so far)
    auth/ permissions/ keys/ catalog/ data/ ai/ billing/ usage/ admin/
                  feature modules, filled in by later phases
    config.py     settings from environment variables
    db.py         SQLAlchemy engine, session, declarative base
    storage.py    S3 client
  migrations/     Alembic
  tests/
pipeline/         data connectors, validation, harmonisation (Phase 5)
frontend/         Next.js (App Router, TypeScript, Tailwind)
docs/             documentation
infra/            docker-compose and deployment notes
SPEC.md           product and technical spec
```

## Configuration and secrets

- All configuration comes from environment variables. [.env.example](.env.example) lists them all.
- `.env` is git-ignored. Never commit real secrets.
- With `ENVIRONMENT=staging` or `production`, the API refuses to start unless `API_KEY_HASH_SECRET` is set to a random value of at least 32 characters.
