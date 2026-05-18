from __future__ import annotations

from app.schema.base import SortCamelModel, UpdateCamelModel
from app.schema.response import ResponseCamelModel


class PlanQuerySchema(SortCamelModel):
    name: str | None = None
    code: str | None = None
    status: str | None = None


class PlanCreateSchema(UpdateCamelModel):
    code: str
    name: str
    description: str | None = None
    status: str = "active"


class PlanUpdateSchema(UpdateCamelModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


class PlanItemSchema(ResponseCamelModel):
    code: str
    name: str
    description: str | None = None
    status: str

