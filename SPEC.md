# Project Spec: Africa Data Platform (working name)

> Instructions for Claude Code: read this whole file before writing code. Build in the phases listed at the end, one phase per session. Stop after each phase, summarise what was built, and wait for approval before starting the next. Ask before changing anything in "Decisions already made".

## 1. What we are building

A platform that gives people clean, ready-to-use African data on mining, tourism, agriculture, finance and healthcare. Users get it three ways:

- **REST API:** developers call it with an API key.
- **AI chat:** users ask questions in plain English ("How did Botswana's diamond output change since 2015?") and get an answer, a table and a chart, with sources.
- **Downloads:** CSV / Excel / Parquet exports of cleaned datasets.

Every API key carries permissions that decide exactly what data it can reach (see §4). The AI chat obeys the same permissions as the key or user asking.

First market: Botswana and SADC countries (16). All 54 African countries must be supported by the data model from day one, even if only some have data.

## 2. Users and roles

| Role | Can do |
|---|---|
| Visitor | See catalogue, sample data, pricing |
| Registered user | Use AI chat (limited), create API keys within their plan |
| Organisation admin | Manage team members, keys and billing for their organisation |
| Platform admin (us) | Manage datasets, sources, licences, plans, users; view usage |

Users belong to an organisation (a company, NGO, university). Keys belong to the organisation and are created by a member.

## 3. Data model

### 3.1 Hierarchy

```
Category (sector)        e.g. agriculture
 └─ Data type (topic)    e.g. crop_production
     └─ Dataset          e.g. faostat_crop_production
         └─ Level        raw | cleaned | harmonised | derived
             └─ Series   e.g. maize production, Botswana, tonnes, annual
```

Categories (v1): mining, tourism, agriculture, finance, healthcare

Levels:

- **raw:** as received from the source (kept for audit; usually not sold)
- **cleaned:** errors fixed, missing values flagged, units consistent
- **harmonised:** standard format across all sources (see 3.2), joinable
- **derived:** our own indicators (e.g. food price stress index), our IP

### 3.2 Standard (harmonised) record format

Every harmonised data point is stored in this shape:

| Field | Example | Notes |
|---|---|---|
| series_id | agri.crop_prod.maize.BWA.A | stable unique id |
| category | agriculture | |
| data_type | crop_production | |
| dataset_id | faostat_crop_production | |
| indicator | production_quantity | |
| country_iso3 | BWA | ISO 3166-1 alpha-3 only |
| admin1_code | BW-CE | optional, sub-national |
| period | 2023 / 2023-09 / 2023-Q3 | |
| frequency | A / Q / M / D | |
| value | 12400 | numeric |
| unit | tonnes | from a controlled unit list |
| currency | USD | if monetary |
| price_basis | nominal / real_2015 | if monetary |
| status | official / estimate / imputed / forecast | |
| source_id | fao | |
| licence_id | cc-by-4.0 | |
| retrieved_at | timestamp | |
| version | 2026-11-01 | dataset release version |

### 3.3 Metadata (required for every dataset)

- Title, description, category, data type, countries covered, time coverage, frequency
- Source organisation and URL
- Licence (id, name, URL, commercial_use_allowed true/false, attribution text)
- Update schedule, last updated, next expected update
- Cleaning notes: what was changed and why
- Column dictionary: name, type, unit, description

**Rule:** a dataset whose licence has `commercial_use_allowed = false` can never be served to a paid plan or an API key. The code must enforce this, not just document it.

**Rule:** every API response and every AI answer includes the attribution text of each dataset it used.

## 4. API keys and permissions (core feature)

### 4.1 Scopes

A key holds a list of scopes. Scope format:

```
<category>:<data_type>:<dataset>:<level>
```

Wildcards (`*`) are allowed at any position. Examples:

| Scope | Meaning |
|---|---|
| `agriculture:*:*:*` | everything in agriculture |
| `mining:production:*:harmonised` | harmonised mining production data only |
| `finance:*:*:cleaned` | cleaned finance data only, no derived indicators |
| `*:*:*:derived` | only our premium derived indicators |

The three permission layers you described map onto this format: category → data type → dataset/level.

### 4.2 Extra restrictions per key

| Restriction | Example |
|---|---|
| countries | `["BWA","ZAF","NAM"]` or `["SADC"]` (region groups allowed) |
| years | from: 2010, to: 2026 |
| fields | limit which columns are returned |
| formats | json, csv, parquet, xlsx |
| actions | read, bulk_download, ai_chat, forecast |
| rate_limit | e.g. 60 requests/min |
| monthly_quota | e.g. 50,000 rows or 10,000 calls |
| ip_allowlist | optional |
| expires_at | optional |
| environment | live / test (test keys get sample data only) |

### 4.3 Key security

- Show the full key once at creation. Store only a hash (argon2 or SHA-256 with a server-side secret). Show a prefix (`adp_live_3f9a…`) in the dashboard.
- Keys can be renamed, rotated, paused and revoked. Revocation takes effect immediately.
- Org admins can only grant scopes their plan allows. A key can never have more access than the user who created it.
- Log every request: key id, endpoint, scopes used, rows returned, status, latency.

### 4.4 Enforcement

One central permission check (`authorize(key, request)`) is used by every route, including AI chat and downloads. Requests outside scope return 403 with a clear message saying which scope is missing. Write thorough tests for this module.

## 5. API endpoints (v1)

```
GET  /v1/catalog/categories
GET  /v1/catalog/categories/{category}/data-types
GET  /v1/catalog/datasets?category=&data_type=&country=
GET  /v1/catalog/datasets/{dataset_id}                 # metadata, licence, columns
GET  /v1/data/{dataset_id}?country=&from=&to=&level=&fields=&format=&page=
GET  /v1/series/{series_id}
GET  /v1/indicators/search?q=
POST /v1/exports        # bulk export job → returns job id
GET  /v1/exports/{job_id}
POST /v1/ask            # AI question (see §6)
GET  /v1/usage          # the key's own usage and quota
```

- Auth: `Authorization: Bearer <key>`
- Pagination: cursor-based
- Response headers: rate-limit remaining, quota remaining
- Every data response body includes `meta.sources[]` with attribution and licence
- Auto-generated OpenAPI docs at `/docs`

## 6. AI chat ("ask questions")

### 6.1 How it works

1. User asks a question (web chat or `POST /v1/ask`).
2. The system finds relevant datasets by searching dataset metadata (title, description, column dictionary). Use embeddings plus keyword search.
3. Only datasets the user's key or role can access are passed to the model. Filter before the model sees anything.
4. The model writes a read-only SQL query against the harmonised tables, using tools.
5. Run the query in a read-only database role, with row limits and a timeout.
6. The model answers in plain language, with a table, an optional chart spec, the SQL used, and the sources.

### 6.2 Rules

- Use the Anthropic API (Claude) with tool use. Keep the model name in config.
- The SQL runs as a database user that has SELECT only on views that are pre-filtered for the requester's scopes (row-level security in PostgreSQL). Even a bad query must not be able to leak data outside scope.
- Never invent numbers: if the data is not there, say so and suggest the closest dataset.
- Answers show which datasets were used, with their attribution.
- Count each question against the key's quota (ai_chat action).
- Save the conversation history per user; users can delete it.

## 7. Data pipeline

- One connector per source in `pipeline/connectors/<source>.py` with the same interface: `fetch()` → raw files, `clean()` → cleaned table, `harmonise()` → standard records.
- Raw files are stored unchanged (object storage), with a checksum and retrieval date.
- Validation checks on each run: schema, units, country codes, duplicates, outliers, sudden jumps. A dataset that fails validation is not published; an alert is raised.
- Versioning: every published release gets a version; old versions stay queryable.
- Scheduled runs (daily, weekly or monthly per source).

### 7.1 Starter sources (verify each licence before enabling commercial access)

| Category | Source | Licence to confirm |
|---|---|---|
| Agriculture | FAOSTAT | CC BY 4.0 |
| Agriculture | USDA PSD / NASS | US public domain |
| Agriculture / climate | CHIRPS rainfall, NASA POWER | check terms |
| Finance | World Bank WDI, commodity prices (Pink Sheet) | CC BY 4.0 |
| Finance | OECD | CC BY 4.0 (since July 2024) |
| Finance | IMF | needs written permission for commercial reuse |
| Finance | Central banks (e.g. Bank of Botswana) | check each |
| Mining | USGS Mineral Commodity Summaries / Minerals Yearbook | US public domain |
| Mining | EITI country data | check terms |
| Tourism | World Bank tourism indicators (arrivals, receipts) | CC BY 4.0 |
| Tourism | UN Tourism (UNWTO) | check terms; may restrict |
| Healthcare | WHO GHO | CC BY-NC-SA 3.0 IGO: non-commercial, block from paid plans |
| Healthcare | World Bank health indicators | CC BY 4.0 |
| Cross-sector | Statistics Botswana and other national statistics offices | check each |

Start with 2–3 sources per category, not all of them.

### 7.2 Healthcare and privacy

- Aggregate statistics only. No personal or patient-level data in v1.
- Suppress small counts (fewer than 10 people) in any sub-national health data.
- Follow Botswana's Data Protection Act and similar laws in each country we serve.

## 8. Web app pages

- Home, catalogue (browse by category → data type → dataset), dataset page (metadata, licence, preview, chart, "copy API call" snippet)
- AI chat page
- Dashboard: API keys (create with scope picker, see usage, revoke), usage charts, team members, billing, invoices
- Admin: sources, datasets, licences, pipeline runs and failures, users, plans, usage
- Docs: quick start, authentication, scopes, endpoints, examples in Python, JavaScript, R, Excel / Power Query

The scope picker is a tree: tick a whole category, or open it and tick data types, then datasets, then levels. Then choose countries, years, formats and actions.

## 9. Plans and billing

Plans are configurable in the admin panel, not hard-coded. Starting point:

| Plan | Access | Limits |
|---|---|---|
| Free | harmonised level, 1 category, AI chat 20 questions/month | 1 key, 1,000 calls/month |
| Developer | all categories, cleaned + harmonised | 5 keys, 50,000 calls/month |
| Business | + derived indicators, bulk export, forecasts | team, higher quotas |
| Enterprise / NGO / Government | custom | invoiced |

- Usage metering per organisation (calls, rows, AI questions, exports).
- Payment provider behind an interface (`billing/provider.py`) so it can be swapped. Implement Stripe first, and make sure an African provider (e.g. Paystack, Flutterwave or DPO Pay) can be added later. Support invoicing for organisations that pay by bank transfer.
- Prices in USD, with BWP and ZAR display.

## 10. Decisions already made (tech stack)

- Backend: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2
- Database: PostgreSQL 16 with row-level security; DuckDB + Parquet for bulk exports
- Search: PostgreSQL full-text + pgvector for metadata embeddings
- Jobs / pipeline: a task queue (Celery or Dramatiq with Redis), scheduled runs
- Object storage: S3-compatible (MinIO locally)
- Frontend: Next.js (App Router, TypeScript), Tailwind
- Auth (web users): email + password and Google sign-in, email verification; org invites
- AI: Anthropic API via the official Python SDK
- Local dev: `docker compose up` starts everything, with seed data
- Quality: pytest (aim for over 80% coverage on auth/, permissions/, billing/), ruff, mypy, ESLint; GitHub Actions CI on every push
- Config: all secrets in environment variables; `.env.example` committed, `.env` never

## 11. Repository layout

```
/backend
  /app
    /api          # routes
    /auth         # users, sessions, orgs
    /permissions  # scopes, authorize(), tests
    /keys         # API key create/hash/rotate/revoke
    /catalog
    /data         # query service
    /ai           # chat, retrieval, SQL tool, guardrails
    /billing
    /usage        # metering, rate limits, quotas
    /admin
  /migrations
  /tests
/pipeline
  /connectors
  /validation
  /harmonise
/frontend
/docs
/infra            # docker-compose, deployment notes
README.md
SPEC.md           # this file
.env.example
```

## 12. Build phases (one per session; stop after each)

1. **Skeleton:** repo layout, docker compose (Postgres, Redis, MinIO), FastAPI health check, Next.js shell, CI, README with setup steps.
2. **Data model + catalogue:** tables for categories, data types, datasets, licences, series, observations; seed with sample data for 2 countries × 5 categories; catalogue endpoints.
3. **Auth, orgs, API keys, permissions:** users, orgs, keys (hashed), scopes, `authorize()`, rate limits, quotas, usage logging. Full test suite for permissions.
4. **Data API:** `/v1/data`, `/v1/series`, filters, pagination, formats, attribution in responses, licence enforcement.
5. **Pipeline:** connector interface + 2 real connectors (FAOSTAT, World Bank), validation, versioning, scheduling.
6. **AI chat:** retrieval over metadata, scoped read-only SQL tool, answers with sources; web chat page + `/v1/ask`.
7. **Web dashboard:** catalogue pages, dataset pages, key management with scope picker, usage charts.
8. **Billing:** plans, metering, Stripe, invoices.
9. **Admin panel + docs site.**
10. **Hardening:** security review of auth/permissions/AI SQL, load test, backups, deployment guide.

## 13. Definition of done (every phase)

- Runs with `docker compose up` from a fresh clone
- Tests pass in CI; new code has tests
- README / docs updated
- No secrets in the repo
- Short summary of what was built and what's next
