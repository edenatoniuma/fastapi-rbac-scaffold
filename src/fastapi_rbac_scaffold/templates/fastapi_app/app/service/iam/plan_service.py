from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.iam import Plan
from app.schema.iam import PlanCreateSchema, PlanQuerySchema, PlanUpdateSchema
from app.service.common_service import get_obj_or_404, list_by_query


PLAN_FILTERS = {"name": "like", "code": "like", "status": "eq"}


async def list_plans(db: AsyncSession, query: PlanQuerySchema):
    return await list_by_query(db, Plan, query, PLAN_FILTERS)


async def create_plan(db: AsyncSession, data: PlanCreateSchema) -> Plan:
    plan = Plan(**data.model_dump(by_alias=False))
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


async def update_plan(db: AsyncSession, plan_id: int, data: PlanUpdateSchema) -> Plan:
    plan = await get_obj_or_404(db, Plan, plan_id)
    data.apply(plan)
    await db.commit()
    await db.refresh(plan)
    return plan

