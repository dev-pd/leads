# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install dependencies first, from the lockfile, for reproducible + cached builds.
# (dev group included so `make test` / `make lint` work inside the container.)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

RUN chmod +x scripts/entrypoint.sh \
    && adduser --disabled-password --gecos "" appuser \
    && mkdir -p /data/resumes \
    && chown -R appuser:appuser /app /data
USER appuser

EXPOSE 8000
CMD ["./scripts/entrypoint.sh"]
