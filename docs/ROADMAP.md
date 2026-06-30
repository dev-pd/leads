# Production Roadmap

How this app evolves from a working local stack into a hardened, scalable
production service. It documents the deliberate seams already built in so each
upgrade is an isolated change rather than a rewrite.

## Current architecture (baseline)

```
nginx ─┬─ /api → FastAPI (route → service → repository → model)
       └─ /    → Next.js
Postgres · MinIO/S3 (resumes) · Resend (email) · Anthropic API (resume scoring)
```

Resume analysis runs **asynchronously** after submission: the lead is stored and
the form returns instantly; a background task extracts the PDF text (pypdf),
sends it to the Anthropic API for a structured profile + fit score, and writes
the result back. The attorney dashboard shows an "Analyzing…" state until it
lands.

---

## 1. Async pipeline → a managed work queue

**Today:** FastAPI `BackgroundTasks` (in-process threadpool). Fine for a demo
and moderate load; the web process does the LLM call, and jobs don't survive a
restart.

**Production:** move the resume-analysis job to a real queue.

- **Broker/workers:** Celery or Arq backed by Redis or SQS; a dedicated worker
  pool runs the Anthropic calls so the API process never blocks.
- **Reliability:** at-least-once delivery, exponential-backoff retries, a
  dead-letter queue for poison messages, and idempotency keyed on `lead_id`
  (re-running an analysis is safe).
- **Backpressure:** rate-limit Anthropic calls and autoscale workers on queue
  depth — many prospects submitting at once just deepens the queue.
- **Why it's a small change:** the job is already isolated behind
  `resume_ai.generate_and_store_summary(lead_id, …)`. Swapping `background.add_task`
  for `task.delay` is the entire migration.

A `lead.analysis_status` enum (`pending` → `processing` → `done`/`failed`) would
replace the current "score is NULL ⇒ analyzing" heuristic for precise UI states
and retry visibility.

---

## 2. AWS infrastructure

| Concern | Service |
|---|---|
| Containers | ECS Fargate (api + worker services) behind an ALB |
| Edge | CloudFront in front of the Next.js app + ALB; WAF for L7 protection |
| Database | RDS Postgres (Multi-AZ), automated backups + PITR |
| Object storage | S3 for resumes (the `S3Backend` already speaks the S3 API) |
| Queue/cache | ElastiCache Redis or SQS |
| Secrets | Secrets Manager / SSM (no secrets in env files or images) |
| Networking | Private subnets for api/worker/RDS; only ALB + CloudFront public |
| IaC | Terraform or CDK; one stack per environment (dev/staging/prod) |

The storage interface means S3 is a config flip (`STORAGE_BACKEND=s3`), and
migrations already run on container start (`alembic upgrade head`).

---

## 3. Database hardening

- **Migrations** are the only schema path (Alembic) — already enforced.
- **Backups:** automated snapshots + point-in-time recovery; periodic restore
  drills.
- **Least privilege:** the app role gets DML only; migrations run under a
  separate role.
- **Encryption:** at rest (RDS KMS) and in transit (TLS-required connections).
- **Connection management:** PgBouncer / RDS Proxy for pooling under many
  workers.
- **Integrity:** unique/`NOT NULL` constraints and indexes already in place
  (unique prospect email, indexed `state`/`profile_score`/`profile_rating`).
- **PII:** resumes and extracted text are personal data — define retention,
  deletion (right-to-be-forgotten), and access logging.

---

## 4. Observability & monitoring

- **Logs:** structured JSON with a per-request `X-Request-Id` already emitted →
  ship to CloudWatch Logs / Datadog / Loki.
- **Metrics:** request rate/latency/error (RED), queue depth, worker
  throughput, Anthropic latency + token spend per lead → CloudWatch / Prometheus.
- **Tracing:** OpenTelemetry across api → worker → external calls.
- **Errors:** Sentry on both backend and frontend.
- **Alerts:** error-rate and latency SLOs, queue backlog, failed-analysis rate,
  RDS health; health probe already exists at `/health`.

---

## 5. AI / RAG / agentic roadmap

The current scorer is a single, stateless LLM call against an explicit weighted
rubric (`app/prompts/resume.py`, versioned). Where it goes next:

- **RAG-assisted scoring:** embed each resume and retrieve similar past leads +
  firm-specific intake guidelines/case criteria from a vector store (pgvector /
  OpenSearch). Feed those as context so scores reflect *this firm's* definition
  of a strong prospect, not a generic one.
- **Knowledge base:** index practice-area playbooks and historical outcomes;
  ground the rationale in retrieved, citable material.
- **Agentic enrichment:** a tool-using agent that verifies/augments a profile —
  cross-checking claims, looking up public professional history, flagging
  conflicts — with human-in-the-loop review before it affects a score.
- **Evaluation:** a labeled set of attorney-rated leads to measure scoring
  precision/recall, plus A/B of prompt versions (already version-tagged) and
  models. Capture the model + prompt version on each assessment for auditability.
- **Cost/latency controls:** batch off-peak analysis, cache by resume hash, and
  tier models (cheap default — currently Sonnet — escalating only on ambiguity).
- **Guardrails:** PII minimization in prompts, output validation (already
  defensive JSON parsing + rubric clamping), and bias review of scoring.

---

## 6. Security & auth

- Swap the seeded-attorney JWT for a hosted identity provider (Clerk / Cognito /
  Auth0) — isolated behind the single `require_attorney` dependency, so it's a
  one-seam change. Add roles (attorney/admin) and per-firm tenancy.
- Rate limiting at nginx/ALB, CSRF protection on cookie auth, security headers
  (CSP/HSTS), and an append-only audit log of lead access and state changes.

---

## 7. Scaling summary

- **API:** stateless → scale horizontally behind the ALB.
- **Workers:** autoscale on queue depth, independent of the API.
- **DB:** read replicas for dashboard reads; partition/archive old leads.
- **Caching:** cache dashboard list/aggregates; CDN for static assets.
