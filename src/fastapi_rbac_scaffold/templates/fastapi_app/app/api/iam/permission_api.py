from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps import require_platform_admin
from app.schema.iam import FeatureCreateSchema, FeatureItemSchema, PermissionCreateSchema, PermissionItemSchema, PermissionQuerySchema
from app.schema.response import ListSchema, ResponseSchema
from app.security.permission import CurrentPrincipal
from app.service.iam import permission_service


router = APIRouter(prefix="/iam/permissions", tags=["iam-permissions"])


@router.post("/list", response_model=ResponseSchema[ListSchema[PermissionItemSchema]])
async def list_permissions_api(
    query: PermissionQuerySchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[ListSchema[PermissionItemSchema]]:
    return ResponseSchema(data=await permission_service.list_permissions(db, query))


@router.post("", response_model=ResponseSchema[PermissionItemSchema])
async def create_permission_api(
    data: PermissionCreateSchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[PermissionItemSchema]:
    return ResponseSchema(data=await permission_service.create_permission(db, data))


@router.post("/features", response_model=ResponseSchema[FeatureItemSchema])
async def create_feature_api(
    data: FeatureCreateSchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[FeatureItemSchema]:
    return ResponseSchema(data=await permission_service.create_feature(db, data))

