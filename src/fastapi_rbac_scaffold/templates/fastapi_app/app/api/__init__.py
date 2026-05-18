from __future__ import annotations

from collections.abc import Sequence

from fastapi import APIRouter

from app.api.auth.auth_api import router as auth_router
from app.api.health import router as health_router
from app.api.iam.permission_api import router as permission_router
from app.api.iam.plan_api import router as plan_router
from app.api.iam.role_api import router as role_router
from app.api.iam.tenant_api import router as tenant_router
from app.api.iam.user_api import router as user_router


ROUTERS: Sequence[APIRouter] = (
    health_router,
    auth_router,
    tenant_router,
    user_router,
    role_router,
    permission_router,
    plan_router,
)


def build_api_router() -> APIRouter:
    api_router = APIRouter(prefix="/api")
    for router in ROUTERS:
        api_router.include_router(router)
    return api_router

