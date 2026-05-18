from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.iam import Tenant
from app.schema.iam import TenantCreateSchema, TenantQuerySchema, TenantUpdateSchema
from app.service.common_service import get_obj_or_404, list_by_query


TENANT_FILTERS = {"name": "like", "code": "like", "status": "eq"}


async def list_tenants(db: AsyncSession, query: TenantQuerySchema):
    return await list_by_query(db, Tenant, query, TENANT_FILTERS)


async def create_tenant(db: AsyncSession, data: TenantCreateSchema) -> Tenant:
    tenant = Tenant(**data.model_dump(by_alias=False))
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


async def get_tenant(db: AsyncSession, tenant_id: int) -> Tenant:
    return await get_obj_or_404(db, Tenant, tenant_id)


async def update_tenant(
    db: AsyncSession,
    tenant_id: int,
    data: TenantUpdateSchema,
) -> Tenant:
    tenant = await get_tenant(db, tenant_id)
    data.apply(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


async def delete_tenant(db: AsyncSession, tenant_id: int) -> None:
    tenant = await get_tenant(db, tenant_id)
    await db.delete(tenant)
    await db.commit()

