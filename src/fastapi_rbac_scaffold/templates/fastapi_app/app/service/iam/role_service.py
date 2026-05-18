from __future__ import annotations

from redis.asyncio import Redis
from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.iam import FeaturePermission, PlanFeature, Role, RolePermission, Tenant
from app.schema.iam import (
    AssignPermissionsSchema,
    RoleCreateSchema,
    RoleQuerySchema,
    RoleUpdateSchema,
)
from app.service.cache_service import delete_cache
from app.service.common_service import get_obj_or_404, list_by_query


ROLE_FILTERS = {"tenant_id": "eq", "name": "like", "code": "like", "status": "eq"}


async def list_roles(db: AsyncSession, query: RoleQuerySchema):
    return await list_by_query(db, Role, query, ROLE_FILTERS)


async def create_role(db: AsyncSession, data: RoleCreateSchema) -> Role:
    role = Role(**data.model_dump(by_alias=False))
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def update_role(db: AsyncSession, role_id: int, data: RoleUpdateSchema) -> Role:
    role = await get_obj_or_404(db, Role, role_id)
    data.apply(role)
    await db.commit()
    await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, role_id: int) -> None:
    role = await get_obj_or_404(db, Role, role_id)
    await db.delete(role)
    await db.commit()


async def assign_permissions(
    db: AsyncSession,
    redis: Redis,
    role_id: int,
    data: AssignPermissionsSchema,
) -> Role:
    role = await get_obj_or_404(db, Role, role_id)
    if role.tenant_id is not None:
        allowed_permission_ids = await get_tenant_allowed_permission_ids(db, role.tenant_id)
        invalid_permission_ids = set(data.permission_ids) - allowed_permission_ids
        if invalid_permission_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role permissions cannot exceed tenant plan permissions",
            )
    await db.execute(delete(RolePermission).where(RolePermission.role_id == role_id))
    for permission_id in data.permission_ids:
        db.add(RolePermission(role_id=role_id, permission_id=permission_id))
    await db.commit()
    await delete_cache(redis, f"rbac:role_permissions:{role_id}")
    await db.refresh(role)
    return role


async def get_tenant_allowed_permission_ids(
    db: AsyncSession,
    tenant_id: int,
) -> set[int]:
    tenant = await get_obj_or_404(db, Tenant, tenant_id)
    if tenant.plan_id is None:
        return set()
    stmt = (
        select(FeaturePermission.permission_id)
        .join(PlanFeature, PlanFeature.feature_id == FeaturePermission.feature_id)
        .where(PlanFeature.plan_id == tenant.plan_id)
    )
    return {int(value) for value in (await db.scalars(stmt)).all()}
