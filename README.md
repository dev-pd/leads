# Leads

A publicly-fillable lead intake application with an auth-guarded internal
dashboard for attorneys, plus **AI résumé scoring** that triages prospects.

- **Prospects** submit a public form: first name, last name, email, résumé (PDF).
- On submit, the app stores the résumé and emails **both** the prospect (a
  confirmation) and an **attorney** (a notification).
- A background job **parses the résumé and scores the prospect** against a
  weighted rubric (Anthropic API), so the attorney sees the strongest leads.
- **Attorneys** log into an internal dashboard — a sortable, filterable table of
  leads with fit scores — review each one, download the résumé, and mark a lead
  **PENDING → REACHED_OUT**.

## Architecture

```
            ┌─────────── nginx (:80) ───────────┐
browser ──▶ │  /        → frontend (Next.js)     │
            │  /api/*   → backend  (FastAPI)      │
            └────────────────┬───────────────────┘
                             │
          ┌──────────┬───────┼────────┬─────────────┐
      Postgres   MinIO (S3)  Resend   Anthropic API  (background
     (lead data) (résumés)  (email)   (résumé score)  worker)
```

- **backend/** — FastAPI + SQLAlchemy + Alembic, layered `route → service →
  repository → model`. JWT auth, Resend email, pluggable storage (local/S3),
  async résumé analysis.
- **frontend/** — Next.js (App Router, TypeScript), Tailwind, react-hook-form.
- **nginx/** — reverse proxy giving the app a single origin (no CORS).

## Quick start

```bash
cp backend/.env.example backend/.env       # set JWT_SECRET + ATTORNEY_* (required)
cp frontend/.env.example frontend/.env.local
make up                                    # or: docker compose up --build -d
```

Then open **http://localhost**. API docs at **http://localhost/docs**.

Optional keys in `backend/.env`: `RESEND_API_KEY` (real emails) and
`ANTHROPIC_API_KEY` (résumé scoring). Empty = that feature is skipped.

## Documentation

- [`docs/RUNNING.md`](docs/RUNNING.md) — run it locally, step by step
- [`docs/SYSTEM_DESIGN.md`](docs/SYSTEM_DESIGN.md) — why it's built this way
- [`docs/AGENT_USAGE.md`](docs/AGENT_USAGE.md) — how coding agents were used
- [`docs/PROMPTS.md`](docs/PROMPTS.md) — representative prompt excerpts
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — the path to production
- [`NOTES.md`](NOTES.md) — attribution
