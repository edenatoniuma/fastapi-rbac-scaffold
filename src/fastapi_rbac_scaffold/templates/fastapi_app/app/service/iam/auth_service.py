from __future__ import annotations

from datetime import timedelta
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.model.iam import (
    Permission,
    Role,
    RolePermission,
    Tenant,
    TenantUser,
    TenantUserRole,
    User,
)
from app.schema.iam import LoginRequest, LoginResponse
from app.security.jwt import create_token
from app.security.jwt import decode_token
from app.security.password import verify_password
from app.security.permission import CurrentPrincipal
from app.service.cache_service import get_json_cache, set_json_cache


async def login(
    db: AsyncSession,
    data: LoginRequest,
) -> LoginResponse:
    stmt = select(User).where(User.username == data.username)
    user = await db.scalar(stmt)
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled",
        )

    tenant_id = data.tenant_id
    if not user.is_platform_admin:
        if tenant_id is None:
            tenant_id = await get_default_tenant_id(db, user.id)
        await ensure_tenant_membership(db, user.id, tenant_id)

    settings = get_settings()
    session_id = str(uuid4())
    access_token = create_token(
        subject=str(user.id),
        tenant_id=tenant_id,
        session_id=session_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh_token = create_token(
        subject=str(user.id),
        tenant_id=tenant_id,
        session_id=session_id,
        token_type="refresh",
        expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes),
    )
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh_token(token: str) -> LoginResponse:
    settings = get_settings()
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    subject = str(payload["sub"])
    tenant_id = payload.get("tenant_id")
    session_id = payload.get("session_id") or str(uuid4())
    access_token = create_token(
        subject=subject,
        tenant_id=tenant_id,
        session_id=session_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    new_refresh_token = create_token(
        subject=subject,
        tenant_id=tenant_id,
        session_id=session_id,
        token_type="refresh",
        expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes),
    )
    return LoginResponse(access_token=access_token, refresh_token=new_refresh_token)


async def get_default_tenant_id(db: AsyncSession, user_id: int) -> int:
    stmt = (
        select(TenantUser.tenant_id)
        .where(TenantUser.user_id == user_id)
        .where(TenantUser.status == "active")
        .limit(1)
    )
    tenant_id = await db.scalar(stmt)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to any active tenant",
        )
    return int(tenant_id)


async def ensure_tenant_membership(
    db: AsyncSession,
    user_id: int,
    tenant_id: int,
) -> TenantUser:
    stmt = (
        select(TenantUser)
        .join(Tenant, Tenant.id == TenantUser.tenant_id)
        .where(TenantUser.user_id == user_id)
        .where(TenantUser.tenant_id == tenant_id)
        .where(TenantUser.status == "active")
        .where(Tenant.status == "active")
    )
    tenant_user = await db.scalar(stmt)
    if tenant_user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant membership not found",
        )
    return tenant_user


async def build_principal(
    db: AsyncSession,
    redis: Redis,
    payload: dict[str, Any],
) -> CurrentPrincipal:
    user_id = int(payload["sub"])
    tenant_id = payload.get("tenant_id")
    user = await db.get(User, user_id)
    if user is None or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled",
        )

    if user.is_platform_admin:
        return CurrentPrincipal(
            user_id=user.id,
            username=user.username,
            tenant_id=tenant_id,
            is_platform_admin=True,
            role_ids=[],
            permissions=set(),
        )

    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant context is required",
        )

    tenant_user = await ensure_tenant_membership(db, user.id, int(tenant_id))
    cache_key = f"rbac:user_permissions:{tenant_id}:{user.id}"
    cached = await get_json_cache(redis, cache_key)
    if cached:
        return CurrentPrincipal(
            user_id=user.id,
            username=user.username,
            tenant_id=int(tenant_id),
            role_ids=list(cached.get("role_ids", [])),
            permissions=set(cached.get("permissions", [])),
        )

    role_ids, permissions = await load_user_permissions(db, tenant_user.id)
    await set_json_cache(
        redis,
        cache_key,
        {"role_ids": role_ids, "permissions": sorted(permissions)},
        expire_seconds=300,
    )
    return CurrentPrincipal(
        user_id=user.id,
        username=user.username,
        tenant_id=int(tenant_id),
        role_ids=role_ids,
        permissions=permissions,
    )


async def load_user_permissions(
    db: AsyncSession,
    tenant_user_id: int,
) -> tuple[list[int], set[str]]:
    role_stmt = (
        select(Role.id)
        .join(TenantUserRole, TenantUserRole.role_id == Role.id)
        .where(TenantUserRole.tenant_user_id == tenant_user_id)
        .where(Role.status == "active")
    )
    role_ids = [int(value) for value in (await db.scalars(role_stmt)).all()]
    if not role_ids:
        return [], set()

    permission_stmt = (
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id.in_(role_ids))
        .where(Permission.status == "active")
    )
    permissions = set((await db.scalars(permission_stmt)).all())
    return role_ids, permissions
