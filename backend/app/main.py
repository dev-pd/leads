"""FastAPI application factory."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health, leads
from app.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging_config import configure_logging, get_logger
from app.core.middleware import RequestContextMiddleware


def create_app() -> FastAPI:
    configure_logging(settings.log_level)
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=["x-request-id"],
    )

    register_exception_handlers(app)

    # Health stays unprefixed so load balancers can probe it directly.
    app.include_router(health.router)
    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(leads.router, prefix=settings.api_prefix)

    get_logger("app.startup").info(
        "app_configured",
        extra={
            "environment": settings.environment,
            "storage_backend": settings.storage_backend,
        },
    )
    return app


app = create_app()
