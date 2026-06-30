# Leads

A publicly-fillable lead intake application with an auth-guarded internal
dashboard for attorneys.

- **Prospects** submit a public form: first name, last name, email, resume (PDF).
- On submit, the app stores the resume and emails **both** the prospect (a
  confirmation) and an **attorney** (a notification).
- **Attorneys** log into an internal dashboard, review every lead, download
  resumes, and mark a lead **PENDING → REACHED_OUT**.

## Architecture

```
            ┌─────────── nginx (:80) ───────────┐
browser ──▶ │  /        → frontend (Next.js)     │
            │  /api/*   → backend  (FastAPI)      │
            └────────────────┬───────────────────┘
                             │
              ┌──────────────┼───────────────┐
         Postgres        MinIO (S3)        Resend
        (lead data)   (resume PDFs)     (email API)
```

- **backend/** — FastAPI + SQLAlchemy + Alembic. JWT auth, Resend email,
  pluggable storage (local disk or MinIO/S3).
- **frontend/** — Next.js (App Router, TypeScript), Tailwind, react-hook-form.
- **nginx/** — reverse proxy giving the app a single origin (no CORS).

## Quick start

```bash
cp backend/.env.example backend/.env   # set RESEND_API_KEY + attorney emails
cp frontend/.env.example frontend/.env.local
docker compose up --build
```

Then open **http://localhost**. API docs at **http://localhost/docs**.

Full instructions and the design rationale:
- [`docs/RUNNING.md`](docs/RUNNING.md) — run it locally
- [`docs/SYSTEM_DESIGN.md`](docs/SYSTEM_DESIGN.md) — why it's built this way
- [`docs/AGENT_USAGE.md`](docs/AGENT_USAGE.md) — how coding agents were used
- [`NOTES.md`](NOTES.md) — agent vs hand-written attribution
