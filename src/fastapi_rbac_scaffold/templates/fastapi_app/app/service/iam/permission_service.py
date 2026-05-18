from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.iam import Feature, Permission
from app.schema.iam import (
    FeatureCreateSchema,
    PermissionCreateSchema,
    PermissionQuerySchema,
)
from app.service.common_service import list_by_query


PERMISSION_FILTERS = {
    "module": "eq",
    "resource": "eq",
    "action": "eq",
    "status": "eq",
}


async def list_permissions(db: AsyncSession, query: PermissionQuerySchema):
    return await list_by_query(db, Permission, query, PERMISSION_FILTERS)


async def create_permission(
    db: AsyncSession,
    data: PermissionCreateSchema,
) -> Permission:
    permission = Permission(**data.model_dump(by_alias=False))
    db.add(permission)
    await db.commit()
    await db.refresh(permission)
    return permission


async def create_feature(db: AsyncSession, data: FeatureCreateSchema) -> Feature:
    feature = Feature(**data.model_dump(by_alias=False))
    db.add(feature)
    await db.commit()
    await db.refresh(feature)
    return feature

