from __future__ import annotations

from fastapi import APIRouter

from app.schema.response import ResponseSchema


router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=ResponseSchema[dict[str, str]])
async def health_check() -> ResponseSchema[dict[str, str]]:
    return ResponseSchema(data={"status": "ok"})

