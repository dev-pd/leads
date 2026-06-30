"""Application errors and handlers producing a consistent
``{"error": {"code", "message"}}`` envelope."""
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def not_found(code: str, message: str) -> AppError:
    return AppError(code, message, 404)


def bad_request(code: str, message: str) -> AppError:
    return AppError(code, message, 400)


def unauthorized(code: str, message: str) -> AppError:
    return AppError(code, message, 401)


def forbidden(code: str, message: str) -> AppError:
    return AppError(code, message, 403)


def conflict(code: str, message: str) -> AppError:
    return AppError(code, message, 409)


def _envelope(code: str, message: str, status_code: int, details=None) -> JSONResponse:
    body = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError):
        return _envelope(exc.code, exc.message, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError):
        return _envelope(
            "VALIDATION_ERROR",
            "Request validation failed",
            422,
            jsonable_encoder(exc.errors()),
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):  # pragma: no cover
        from app.core.logging_config import get_logger

        get_logger("app.error").exception(
            "unhandled_exception",
            extra={"path": request.url.path, "method": request.method},
        )
        return _envelope("INTERNAL_ERROR", "Something went wrong", 500)
