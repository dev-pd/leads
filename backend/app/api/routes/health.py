"""Liveness/readiness probe. Dependency-free so a load balancer can hit it."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
