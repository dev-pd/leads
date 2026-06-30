# System Design

## 1. Problem

Build an application that lets prospects publicly submit a lead (first name, last
name, email, resume/CV) and lets attorneys manage those leads internally.

Distilled requirements:

1. A **public** lead-creation form (no auth).
2. On submit: persist the lead + resume, and **email both** the prospect and an
   internal attorney.
3. An **internal, auth-guarded** UI listing every lead and its data.
4. Each lead has a **state**: starts `PENDING`, attorney moves it to
   `REACHED_OUT` manually.
5. Persistent storage + a real email integration, structured as a production
   repository.

Two capabilities were added after the core app was working, on my call as the
person driving the project (see `AGENT_USAGE.md`):

6. **AI resume scoring** — parse each resume, score the prospect against a
   weighted rubric, and surface the strongest leads to the attorney.
7. Dashboard **table with pagination, a rating filter, and global KPIs**.

## 2. High-level architecture

```
                 ┌──────────────── nginx (:80) ────────────────┐
   browser ────▶ │   /         → frontend (Next.js, App Router) │
                 │   /api/*    → backend  (FastAPI)             │
                 │   /docs     → backend  (OpenAPI UI)          │
                 └───────────────────┬─────────────────────────┘
                                     │
            ┌────────────────────────┼───────────────────────────┐
            ▼            ▼           ▼            ▼                ▼
        Postgres     MinIO/S3     Resend      Anthropic API   (background
       (lead/user   (resume      (transactional  (resume       worker:
         rows)       PDFs)         email)        scoring)      analysis)
```

A single reverse-proxy origin means the browser only ever talks to
`http://localhost`. That removes CORS, keeps the auth cookie first-party, and
mirrors a production ALB/CloudFront edge.

## 3. Components & choices

### Backend — FastAPI, layered

`route → service → repository → model`, with a `storage/` interface for files.

- **Routes** parse/validate only.
- **Services** hold domain rules (state machine, uniqueness, storage + AI
  orchestration).
- **Repositories** own *all* DB queries — services never touch the session
  directly. This keeps data access in one layer and makes the services testable.
- **Errors**: one `AppError` type + central handlers produce a consistent
  `{"error": {"code", "message"}}` envelope.
- **Observability**: structured JSON logs with a per-request `X-Request-Id`.

### Persistence — Postgres + SQLAlchemy + Alembic

Relational store for the simple, queryable `leads`/`users` schema. **Alembic
migrations** (not `create_all`) so schema changes are versioned and reproducible;
they run on container start.

### File storage — pluggable `StorageBackend`

Resumes are binary blobs that don't belong in the DB, so only a **storage key** +
content type live in Postgres. A small interface (`put`/`get`/`delete`) has two
implementations: `LocalDiskBackend` (zero-infra) and `S3Backend` (MinIO locally,
AWS S3 in prod — same code). Selected by one env var. MinIO is used locally so
the exact `boto3` path is exercised with no AWS account.

### Email — Resend

Real transactional email. Two messages on submit (prospect confirmation +
attorney notification), sent in a **background task** so email latency/failure
never blocks or fails the submission.

### Auth — JWT, single chokepoint

One seeded attorney (bcrypt-hashed). `POST /api/auth/login` issues an HS256 JWT
stored in an **httpOnly cookie**; `require_attorney` validates it on every
internal route. Because every guarded route depends on that one dependency, the
scheme can later be swapped for a hosted provider by changing only that seam.

### Frontend — Next.js (App Router, TypeScript)

- Public `/` landing = the intake form (react-hook-form + zod, validation
  mirroring the backend).
- Auth-guarded `/dashboard`: a **data table** of leads with a fit-score column,
  global KPI tiles, a rating filter, and pagination; a lead detail page with the
  AI summary, fit assessment, résumé button, and the state control.
- Login is a **modal**; logout returns to the landing page; `middleware.ts`
  guards `/dashboard`.
- A server route proxies résumé downloads, bridging the httpOnly cookie to the
  Bearer-guarded backend.

## 4. AI resume scoring (the standout feature)

Added after the base app worked. Pipeline:

```
submit ─▶ store lead (PENDING, profile = NULL) ─▶ 201 returned instantly
                          │  background task
                          ▼
   pypdf extracts text ─▶ Anthropic Messages API (claude-sonnet-5) ─▶
   {summary, score, rating, rationale, strengths, concerns, details} ─▶ UPDATE lead
```

Design decisions:

- **Parse then reason.** `pypdf` does the mechanical PDF→text extraction (cheap,
  deterministic) and we store the text; the LLM does the judgment a parser
  can't — structuring arbitrary layouts and scoring. If extraction yields almost
  nothing (a scanned image), we **fall back** to sending the PDF itself, which
  Claude reads via vision.
- **Explicit, versioned rubric.** Scoring is not a vibe: an explicit weighted
  rubric tied to the firm's matter — the O-1 / EB-1A extraordinary-ability
  criteria (awards 20 / original contributions 20 / critical role 15 / press 15 /
  scholarly work 10 / memberships 10 / remuneration 10) — lives in
  `app/prompts/resume.py` with a `RESUME_PROMPT_VERSION`, so scores are principled
  and the prompt can evolve traceably.
- **Async, never blocking.** Runs in a FastAPI `BackgroundTask`; the prospect
  never waits. The attorney UI shows an "Analyzing…" state and auto-refreshes
  until the score lands.
- **Structured output via forced tool call.** The assessment comes back as the
  input to a forced `record_assessment` tool, so the API validates it against a
  schema and we read guaranteed-valid JSON — no hand-parsing of model text that
  can break on an unescaped quote. Scores are clamped and the rating re-derived
  defensively. Model is env-configurable (Sonnet by default for cost).
- **Triage UX.** The score/rating is shown per lead and the dashboard can filter
  by strong/moderate/weak so the attorney focuses on the prospects worth
  pursuing.

## 5. Data model

```
users                          leads
─────                          ─────
id            (uuid pk)        id                  (uuid pk)
email         (unique)         first_name / last_name
name                           email               (unique, indexed)
password_hash                  resume_key / _filename / _content_type
created_at                     state  PENDING|REACHED_OUT  (indexed)
                               reached_out_at      (activity trail)
                               resume_text         (parsed text)
                               resume_summary
                               profile_score       (indexed)  ─┐ AI
                               profile_rating      (indexed)   │ scoring
                               profile_assessment  (JSON)     ─┘
                               created_at / updated_at
```

## 6. API surface

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST   | `/api/leads` | public | submit intake form + resume (multipart) |
| GET    | `/api/leads` | attorney | list (pagination, rating filter, sort) |
| GET    | `/api/leads/stats` | attorney | global counts for KPIs |
| GET    | `/api/leads/{id}` | attorney | lead detail |
| PATCH  | `/api/leads/{id}` | attorney | transition state |
| GET    | `/api/leads/{id}/resume` | attorney | stream the résumé |
| POST   | `/api/auth/login` | public | attorney login → JWT |
| GET    | `/api/auth/me` | attorney | current user |
| GET    | `/health` | public | liveness probe |

## 7. Security

- **No secrets in source.** `jwt_secret`, the seed attorney credentials, and S3
  keys are required from env (no insecure in-code defaults); secrets live only in
  the gitignored `.env`.
- Upload validation (PDF only, size limit) before any storage write.
- Resumes are never publicly served — only via the guarded proxy route.
- Login deliberately distinguishes "no account" vs "wrong password" for a
  single-attorney internal tool (a documented usability-over-enumeration choice).

## 8. Scope decisions (deliberately not built)

Right-sized to the assignment, with the upgrade path in
[`ROADMAP.md`](./ROADMAP.md):

- Cloud IaC / ECS / KMS — `docker-compose` + nginx model the same shape locally.
- A managed job queue — `BackgroundTasks` is sufficient for two emails + one LLM
  call per submit; the job is isolated behind one function, so moving it to
  Celery/RQ later is a one-line change.
- Multi-tenancy and hosted auth — the brief is one firm with one attorney.

See [`ROADMAP.md`](./ROADMAP.md) for the production path: managed queue, AWS
infra, DB hardening, monitoring, and a RAG/agentic evolution of the scorer.
