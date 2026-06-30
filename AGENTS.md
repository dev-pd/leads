# Leads — project & agent guide

Publicly-fillable lead intake + auth-guarded internal dashboard.
Prospect submits **first/last name, email, resume PDF** → app emails prospect +
attorney → attorney reviews leads, flips state **PENDING → REACHED_OUT**.

## Stack
- **backend/** — FastAPI, SQLAlchemy 2, Alembic, Postgres. JWT auth, Resend email,
  pluggable storage (local disk / MinIO-S3). See `backend/AGENTS.md`.
- **frontend/** — Next.js (App Router, TS), Tailwind, react-hook-form + zod.
  See `frontend/AGENTS.md`.
- **nginx/** — reverse proxy: `/api` → backend, `/` → frontend (single origin).
- Orchestrated by root `docker-compose.yml` (db, minio, backend, frontend, nginx).

## Run
`cp backend/.env.example backend/.env` (set `RESEND_API_KEY`, attorney emails) →
`docker compose up --build` → app at http://localhost.

## Rules
- **Scoped commits.** One logical change per commit, conventional style
  (`feat(backend): ...`, `feat(frontend): ...`).
- **No secrets in git.** Edit `.env.example`; never the gitignored `.env`.
- Work inside one app at a time; read that app's `AGENTS.md` first.

## Boundaries
- Public route: `POST /api/leads` only. Everything else needs the attorney JWT.
- State machine is one-way `PENDING → REACHED_OUT`, enforced in
  `backend/app/services/leads.py`.

## Verify before done
- Backend: `docker compose up backend` boots, migrations apply, `/health` 200.
- Frontend: `npm run build` + `npm run typecheck` clean.
- Full stack: `docker compose up --build`, app reachable at http://localhost.
