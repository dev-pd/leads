#!/usr/bin/env sh
# Container entrypoint: apply migrations, seed the attorney, then serve.
# Migrations are idempotent (alembic) so this is safe on every boot.
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding attorney account..."
python -m scripts.seed

echo "Starting API on :8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
