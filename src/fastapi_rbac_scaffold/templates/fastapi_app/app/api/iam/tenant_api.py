from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps import require_platform_admin
from app.schema.iam import TenantCreateSchema, TenantItemSchema, TenantQuerySchema, TenantUpdateSchema
from app.schema.response import ListSchema, ResponseSchema
from app.security.permission import CurrentPrincipal
from app.service.iam import tenant_service


router = APIRouter(prefix="/iam/tenants", tags=["iam-tenants"])


@router.post("/list", response_model=ResponseSchema[ListSchema[TenantItemSchema]])
async def list_tenants_api(
    query: TenantQuerySchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[ListSchema[TenantItemSchema]]:
    return ResponseSchema(data=await tenant_service.list_tenants(db, query))


@router.post("", response_model=ResponseSchema[TenantItemSchema])
async def create_tenant_api(
    data: TenantCreateSchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[TenantItemSchema]:
    return ResponseSchema(data=await tenant_service.create_tenant(db, data))


@router.get("/{tenant_id}", response_model=ResponseSchema[TenantItemSchema])
async def get_tenant_api(
    tenant_id: int,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[TenantItemSchema]:
    return ResponseSchema(data=await tenant_service.get_tenant(db, tenant_id))


@router.put("/{tenant_id}", response_model=ResponseSchema[TenantItemSchema])
async def update_tenant_api(
    tenant_id: int,
    data: TenantUpdateSchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[TenantItemSchema]:
    return ResponseSchema(data=await tenant_service.update_tenant(db, tenant_id, data))


@router.delete("/{tenant_id}", response_model=ResponseSchema[None])
async def delete_tenant_api(
    tenant_id: int,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[None]:
    await tenant_service.delete_tenant(db, tenant_id)
    return ResponseSchema(data=None)

