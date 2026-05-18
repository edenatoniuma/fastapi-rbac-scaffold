from __future__ import annotations

from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def paginate(
    db: AsyncSession,
    stmt: Select[Any],
    *,
    start: int = 0,
    limit: int = 20,
) -> tuple[list[Any], int]:
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = await db.scalar(count_stmt)
    result = await db.execute(stmt.offset(start).limit(limit))
    return list(result.scalars().all()), int(total or 0)

