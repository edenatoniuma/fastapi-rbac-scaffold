from __future__ import annotations

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps import get_redis, require_permission
from app.schema.iam import AssignPermissionsSchema, RoleCreateSchema, RoleItemSchema, RoleQuerySchema, RoleUpdateSchema
from app.schema.response import ListSchema, ResponseSchema
from app.security.permission import CurrentPrincipal
from app.service.iam import role_service


router = APIRouter(prefix="/iam/roles", tags=["iam-roles"])


@router.post("/list", response_model=ResponseSchema[ListSchema[RoleItemSchema]])
async def list_roles_api(
    query: RoleQuerySchema,
    current: CurrentPrincipal = Depends(require_permission("iam:role:list")),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[ListSchema[RoleItemSchema]]:
    if not current.is_platform_admin:
        query.tenant_id = current.tenant_id
    return ResponseSchema(data=await role_service.list_roles(db, query))


@router.post("", response_model=ResponseSchema[RoleItemSchema])
async def create_role_api(
    data: RoleCreateSchema,
    current: CurrentPrincipal = Depends(require_permission("iam:role:create")),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[RoleItemSchema]:
    if not current.is_platform_admin:
        data.tenant_id = current.tenant_id
    return ResponseSchema(data=await role_service.create_role(db, data))


@router.put("/{role_id}", response_model=ResponseSchema[RoleItemSchema])
async def update_role_api(
    role_id: int,
    data: RoleUpdateSchema,
    current: CurrentPrincipal = Depends(require_permission("iam:role:update")),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[RoleItemSchema]:
    return ResponseSchema(data=await role_service.update_role(db, role_id, data))


@router.delete("/{role_id}", response_model=ResponseSchema[None])
async def delete_role_api(
    role_id: int,
    current: CurrentPrincipal = Depends(require_permission("iam:role:delete")),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[None]:
    await role_service.delete_role(db, role_id)
    return ResponseSchema(data=None)


@router.post("/{role_id}/permissions", response_model=ResponseSchema[RoleItemSchema])
async def assign_permissions_api(
    role_id: int,
    data: AssignPermissionsSchema,
    current: CurrentPrincipal = Depends(require_permission("iam:role:assign_permission")),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> ResponseSchema[RoleItemSchema]:
    return ResponseSchema(data=await role_service.assign_permissions(db, redis, role_id, data))

