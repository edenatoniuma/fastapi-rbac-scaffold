from __future__ import annotations

from app.schema.base import SortCamelModel, UpdateCamelModel
from app.schema.response import ResponseCamelModel


class TenantQuerySchema(SortCamelModel):
    name: str | None = None
    code: str | None = None
    status: str | None = None


class TenantCreateSchema(UpdateCamelModel):
    name: str
    code: str
    plan_id: int | None = None
    status: str = "active"


class TenantUpdateSchema(UpdateCamelModel):
    name: str | None = None
    plan_id: int | None = None
    status: str | None = None


class TenantItemSchema(ResponseCamelModel):
    name: str
    code: str
    plan_id: int | None = None
    status: str

