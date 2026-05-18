from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, Header, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps.redis import get_redis
from app.security.jwt import decode_token
from app.security.permission import CurrentPrincipal
from app.service.iam.auth_service import build_principal


async def get_current_principal(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> CurrentPrincipal:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    if await redis.get(f"jwt:blacklist:{token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
    return await build_principal(db=db, redis=redis, payload=payload)


def require_permission(
    permission_code: str,
) -> Callable[[CurrentPrincipal], CurrentPrincipal]:
    async def dependency(
        current: CurrentPrincipal = Depends(get_current_principal),
    ) -> CurrentPrincipal:
        if current.is_platform_admin:
            return current
        if permission_code not in current.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )
        return current

    return dependency


async def require_platform_admin(
    current: CurrentPrincipal = Depends(get_current_principal),
) -> CurrentPrincipal:
    if not current.is_platform_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform admin required",
        )
    return current

