# Backend — FastAPI service

## Layout
```
app/
  main.py            app factory: logging → middleware → errors → routers
  config.py          pydantic-settings (env), single Settings object
  db.py              SQLAlchemy engine + session, get_db dependency
  models/            ORM: lead.py (Lead + LeadState enum), user.py
  schemas/           Pydantic I/O: lead.py, auth.py
  api/
    deps.py          DbSession, Storage, require_attorney (JWT guard)
    routes/          leads.py, auth.py, health.py
  services/          business logic: leads.py, email.py
  storage/           backend interface + local.py + s3.py + factory.py
  core/              errors, security (JWT/bcrypt), logging, middleware
alembic/             migrations (0001_initial)
scripts/             seed.py (attorney), entrypoint.sh
tests/               pytest
```

## Layering (keep it)
`route → service → model/storage`. Routes parse/validate only; all domain logic
lives in `services/`. Errors raised as `AppError` (`core/errors.py`) → consistent
`{"error":{"code","message"}}` envelope.

## Rules
- Add new env vars to `config.Settings` **and** `.env.example`.
- Storage access goes through the `StorageBackend` interface — never import
  boto3 or touch the filesystem outside `storage/`.
- State transitions only via `services/leads.update_lead_state` (enforces the
  PENDING→REACHED_OUT machine).
- Every service logs structured events via `core.logging.get_logger`.
- Migrations, not `create_all`. New model change → new Alembic revision.

## Commands
Dependencies are managed with **uv** (`pyproject.toml` + `uv.lock`). `uv sync`
installs them; `uv run <cmd>` runs inside the project venv.
- Run: `uv run uvicorn app.main:app --reload`
- Migrate: `uv run alembic upgrade head`  · Seed: `uv run python -m scripts.seed`
- Test: `uv run pytest`  · Lint: `uv run ruff check app scripts tests`
