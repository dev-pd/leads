# Backend — FastAPI service

## Layout
```
app/
  main.py            app factory: logging → middleware → errors → routers
  config.py          pydantic-settings (env), single Settings object
  db.py              SQLAlchemy engine + session, get_db dependency
  models/            ORM: lead.py (Lead + LeadState enum + résumé/score cols), user.py
  schemas/           Pydantic I/O: lead.py, auth.py
  api/
    deps.py          DbSession, Storage, repositories, require_attorney (JWT guard)
    routes/          leads.py (+ /leads/stats), auth.py, health.py
  services/          business logic: leads.py, email.py, resume_ai.py (AI scoring)
  prompts/           resume.py — versioned O-1 assessment prompt (RESUME_PROMPT_VERSION)
  repositories/      data access: leads.py, users.py (the only DB queries)
  storage/           backend interface + local.py + s3.py + factory.py
  core/              errors, security (JWT/bcrypt), logging, middleware
alembic/             migrations
scripts/             seed.py (attorney), entrypoint.sh
tests/               pytest
```

## Layering (keep it)
`route → service → repository → model`, with `storage/` for files. Routes
parse/validate only; domain rules live in `services/`; **all DB queries live in
`repositories/`** (services never touch the session directly). Errors raised as
`AppError` (`core/errors.py`) → consistent `{"error":{"code","message"}}` envelope.

## Rules
- Add new env vars to `config.Settings` **and** `.env.example`.
- Storage access goes through the `StorageBackend` interface — never import
  boto3 or touch the filesystem outside `storage/`.
- State transitions only via `services/leads.update_lead_state` (enforces the
  PENDING→REACHED_OUT machine).
- Every service logs structured events via `core.logging.get_logger`.
- Migrations, not `create_all`. New model change → new Alembic revision.
- **AI scoring** (`services/resume_ai.py`) runs in a `BackgroundTask`, never
  blocks submission, and degrades gracefully (no API key → skipped). It uses a
  **forced `record_assessment` tool call** for schema-valid output — don't go
  back to parsing free-form model text. Prompt edits bump `RESUME_PROMPT_VERSION`
  in `app/prompts/resume.py`.

## Commands
Dependencies are managed with **uv** (`pyproject.toml` + `uv.lock`). `uv sync`
installs them; `uv run <cmd>` runs inside the project venv.
- Run: `uv run uvicorn app.main:app --reload`
- Migrate: `uv run alembic upgrade head`  · Seed: `uv run python -m scripts.seed`
- Test: `uv run pytest`  · Lint: `uv run ruff check app scripts tests`
