from __future__ import annotations

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps import get_redis, require_permission, require_platform_admin
from app.schema.iam import (
    AssignUserRolesSchema,
    TenantMembershipSchema,
    UserCreateSchema,
    UserItemSchema,
    UserQuerySchema,
    UserUpdateSchema,
)
from app.schema.response import ListSchema, ResponseSchema
from app.security.permission import CurrentPrincipal
from app.service.iam import user_service


router = APIRouter(prefix="/iam/users", tags=["iam-users"])


@router.post("/list", response_model=ResponseSchema[ListSchema[UserItemSchema]])
async def list_users_api(
    query: UserQuerySchema,
    current: CurrentPrincipal = Depends(require_permission("iam:user:list")),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[ListSchema[UserItemSchema]]:
    return ResponseSchema(data=await user_service.list_users(db, query))


@router.post("", response_model=ResponseSchema[UserItemSchema])
async def create_user_api(
    data: UserCreateSchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[UserItemSchema]:
    return ResponseSchema(data=await user_service.create_user(db, data))


@router.get("/{user_id}", response_model=ResponseSchema[UserItemSchema])
async def get_user_api(
    user_id: int,
    current: CurrentPrincipal = Depends(require_permission("iam:user:detail")),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[UserItemSchema]:
    return ResponseSchema(data=await user_service.get_user(db, user_id))


@router.put("/{user_id}", response_model=ResponseSchema[UserItemSchema])
async def update_user_api(
    user_id: int,
    data: UserUpdateSchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[UserItemSchema]:
    return ResponseSchema(data=await user_service.update_user(db, user_id, data))


@router.delete("/{user_id}", response_model=ResponseSchema[None])
async def delete_user_api(
    user_id: int,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[None]:
    await user_service.delete_user(db, user_id)
    return ResponseSchema(data=None)


@router.post("/{user_id}/tenants", response_model=ResponseSchema[dict[str, int]])
async def add_user_to_tenant_api(
    user_id: int,
    data: TenantMembershipSchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[dict[str, int]]:
    tenant_user = await user_service.add_user_to_tenant(db, user_id, data)
    return ResponseSchema(data={"tenant_user_id": tenant_user.id})


@router.post("/{user_id}/roles", response_model=ResponseSchema[dict[str, int]])
async def assign_user_roles_api(
    user_id: int,
    data: AssignUserRolesSchema,
    current: CurrentPrincipal = Depends(require_permission("iam:user:assign_role")),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ResponseSchema[dict[str, int]]:
    if not current.is_platform_admin:
        data.tenant_id = int(current.tenant_id)
    tenant_user = await user_service.assign_user_roles(db, redis, user_id, data)
    return ResponseSchema(data={"tenant_user_id": tenant_user.id})
