from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps import require_platform_admin
from app.schema.iam import PlanCreateSchema, PlanItemSchema, PlanQuerySchema, PlanUpdateSchema
from app.schema.response import ListSchema, ResponseSchema
from app.security.permission import CurrentPrincipal
from app.service.iam import plan_service


router = APIRouter(prefix="/iam/plans", tags=["iam-plans"])


@router.post("/list", response_model=ResponseSchema[ListSchema[PlanItemSchema]])
async def list_plans_api(
    query: PlanQuerySchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[ListSchema[PlanItemSchema]]:
    return ResponseSchema(data=await plan_service.list_plans(db, query))


@router.post("", response_model=ResponseSchema[PlanItemSchema])
async def create_plan_api(
    data: PlanCreateSchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[PlanItemSchema]:
    return ResponseSchema(data=await plan_service.create_plan(db, data))


@router.put("/{plan_id}", response_model=ResponseSchema[PlanItemSchema])
async def update_plan_api(
    plan_id: int,
    data: PlanUpdateSchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema[PlanItemSchema]:
    return ResponseSchema(data=await plan_service.update_plan(db, plan_id, data))

