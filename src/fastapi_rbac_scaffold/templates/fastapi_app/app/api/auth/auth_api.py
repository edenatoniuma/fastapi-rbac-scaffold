from __future__ import annotations

from fastapi import APIRouter, Depends, Header
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.database import get_db
from app.deps import get_current_principal, get_redis
from app.schema.iam import LoginRequest, LoginResponse, PrincipalSchema
from app.schema.response import ResponseSchema
from app.security.permission import CurrentPrincipal
from app.service.iam.auth_service import login, refresh_token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=ResponseSchema[LoginResponse])
async def login_api(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[LoginResponse]:
    return ResponseSchema(data=await login(db, data))


@router.get("/me", response_model=ResponseSchema[PrincipalSchema])
async def me_api(
    current: CurrentPrincipal = Depends(get_current_principal),
) -> ResponseSchema[PrincipalSchema]:
    return ResponseSchema(
        data=PrincipalSchema(
            user_id=current.user_id,
            username=current.username,
            tenant_id=current.tenant_id,
            is_platform_admin=current.is_platform_admin,
            role_ids=current.role_ids,
            permissions=sorted(current.permissions),
        )
    )


@router.post("/refresh", response_model=ResponseSchema[LoginResponse])
async def refresh_api(
    authorization: str | None = Header(default=None),
    redis: Redis = Depends(get_redis),
) -> ResponseSchema[LoginResponse]:
    if not authorization or not authorization.lower().startswith("bearer "):
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )
    token = authorization.split(" ", 1)[1].strip()
    if await redis.get(f"jwt:blacklist:{token}"):
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
    return ResponseSchema(data=await refresh_token(token))


@router.post("/logout", response_model=ResponseSchema[None])
async def logout_api(
    authorization: str | None = Header(default=None),
    redis: Redis = Depends(get_redis),
) -> ResponseSchema[None]:
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        settings = get_settings()
        await redis.set(
            f"jwt:blacklist:{token}",
            "1",
            ex=settings.blacklist_token_expire_seconds,
        )
    return ResponseSchema(data=None)
