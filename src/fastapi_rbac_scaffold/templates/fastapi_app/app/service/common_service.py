from __future__ import annotations

from typing import Any, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import Select, asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import paginate
from app.schema.base import SortCamelModel
from app.schema.response import ListSchema
from app.security.permission import CurrentPrincipal


ModelT = TypeVar("ModelT")


async def get_obj_or_404(
    db: AsyncSession,
    model: type[ModelT],
    object_id: int,
) -> ModelT:
    instance = await db.get(model, object_id)
    if instance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} not found",
        )
    return instance


def apply_tenant_scope(stmt: Select[Any], model: type[Any], current: CurrentPrincipal):
    if current.is_platform_admin:
        return stmt
    if not hasattr(model, "tenant_id"):
        return stmt
    return stmt.where(model.tenant_id == current.tenant_id)


def ensure_tenant_access(instance: Any, current: CurrentPrincipal) -> None:
    if current.is_platform_admin:
        return
    tenant_id = getattr(instance, "tenant_id", None)
    if tenant_id is not None and tenant_id != current.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant access denied",
        )


async def list_by_query(
    db: AsyncSession,
    model: type[Any],
    query: SortCamelModel,
    filters: dict[str, Any] | None = None,
) -> ListSchema[Any]:
    stmt = select(model)
    filters = filters or {}
    values = query.model_dump(by_alias=False, exclude_unset=True)
    for field_name, operator in filters.items():
        value = values.get(field_name)
        if value is None:
            continue
        column = getattr(model, field_name)
        if operator == "like":
            stmt = stmt.where(column.ilike(f"%{value}%"))
        else:
            stmt = stmt.where(column == value)

    if query.sort_field and hasattr(model, query.sort_field):
        column = getattr(model, query.sort_field)
        stmt = stmt.order_by(desc(column) if query.sort_order == "desc" else asc(column))
    elif hasattr(model, "id"):
        stmt = stmt.order_by(desc(model.id))

    items, total = await paginate(db, stmt, start=query.start, limit=query.limit)
    return ListSchema(items=items, total=total, start=query.start, limit=query.limit)

