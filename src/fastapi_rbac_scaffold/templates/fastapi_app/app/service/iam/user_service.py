from __future__ import annotations

from redis.asyncio import Redis
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.iam import TenantUser, TenantUserRole, User
from app.schema.iam import (
    AssignUserRolesSchema,
    TenantMembershipSchema,
    UserCreateSchema,
    UserQuerySchema,
    UserUpdateSchema,
)
from app.security.password import hash_password
from app.service.common_service import get_obj_or_404, list_by_query


USER_FILTERS = {"username": "like", "email": "like", "status": "eq"}


async def list_users(db: AsyncSession, query: UserQuerySchema):
    return await list_by_query(db, User, query, USER_FILTERS)


async def create_user(db: AsyncSession, data: UserCreateSchema) -> User:
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        is_platform_admin=data.is_platform_admin,
        status=data.status,
    )
    db.add(user)
    await db.flush()
    if data.tenant_id is not None:
        db.add(TenantUser(tenant_id=data.tenant_id, user_id=user.id))
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: int) -> User:
    return await get_obj_or_404(db, User, user_id)


async def update_user(db: AsyncSession, user_id: int, data: UserUpdateSchema) -> User:
    user = await get_user(db, user_id)
    values = data.model_dump(exclude_unset=True, by_alias=False)
    password = values.pop("password", None)
    for key, value in values.items():
        setattr(user, key, value)
    if password:
        user.hashed_password = hash_password(password)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> None:
    user = await get_user(db, user_id)
    await db.delete(user)
    await db.commit()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    return await db.scalar(select(User).where(User.username == username))


async def add_user_to_tenant(
    db: AsyncSession,
    user_id: int,
    data: TenantMembershipSchema,
) -> TenantUser:
    await get_user(db, user_id)
    tenant_user = await db.scalar(
        select(TenantUser)
        .where(TenantUser.user_id == user_id)
        .where(TenantUser.tenant_id == data.tenant_id)
    )
    if tenant_user is None:
        tenant_user = TenantUser(user_id=user_id, tenant_id=data.tenant_id)
        db.add(tenant_user)
    else:
        tenant_user.status = "active"
    await db.commit()
    await db.refresh(tenant_user)
    return tenant_user


async def assign_user_roles(
    db: AsyncSession,
    redis: Redis,
    user_id: int,
    data: AssignUserRolesSchema,
) -> TenantUser:
    tenant_user = await db.scalar(
        select(TenantUser)
        .where(TenantUser.user_id == user_id)
        .where(TenantUser.tenant_id == data.tenant_id)
    )
    if tenant_user is None:
        tenant_user = TenantUser(user_id=user_id, tenant_id=data.tenant_id)
        db.add(tenant_user)
        await db.flush()

    await db.execute(
        delete(TenantUserRole).where(TenantUserRole.tenant_user_id == tenant_user.id)
    )
    for role_id in data.role_ids:
        db.add(TenantUserRole(tenant_user_id=tenant_user.id, role_id=role_id))
    await db.commit()
    await redis.delete(f"rbac:user_permissions:{data.tenant_id}:{user_id}")
    await db.refresh(tenant_user)
    return tenant_user
