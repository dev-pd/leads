# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x scripts/entrypoint.sh \
    && adduser --disabled-password --gecos "" appuser \
    && mkdir -p /data/resumes \
    && chown -R appuser:appuser /app /data
USER appuser

EXPOSE 8000
CMD ["./scripts/entrypoint.sh"]
