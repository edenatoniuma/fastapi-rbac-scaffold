from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import build_api_router
from app.config import get_settings
from app.config.logging import setup_logging
from app.core.database import close_database
from app.core.errors import AppError
from app.core.redis import close_redis_client, create_redis_client
from app.core.tracing import instrument_fastapi_app, setup_telemetry
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.tenant_context import TenantContextMiddleware


logger = logging.getLogger(__name__)

AUTH_EXCLUDE_PATHS = (
    "/api/health",
    "/api/auth/login",
    "/api/auth/refresh",
    "/docs",
    "/openapi.json",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await create_redis_client()
    logger.info("Redis client initialized")
    try:
        yield
    finally:
        await close_redis_client(getattr(app.state, "redis", None))
        await close_database()
        logger.info("Application resources closed")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"code": 42200, "message": "Validation failed", "detail": exc.errors()},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": 10000 + exc.status_code, "message": exc.detail},
            headers=exc.headers,
        )

    @app.exception_handler(AppError)
    async def app_exception_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"code": exc.code, "message": exc.message},
        )


def register_middlewares(app: FastAPI) -> None:
    settings = get_settings()
    app.add_middleware(AuthMiddleware, exclude_paths=AUTH_EXCLUDE_PATHS)
    app.add_middleware(TenantContextMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )


def create_app() -> FastAPI:
    setup_logging()
    setup_telemetry()
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )
    instrument_fastapi_app(app)
    app.include_router(build_api_router())
    register_exception_handlers(app)
    register_middlewares(app)
    return app


app = create_app()
