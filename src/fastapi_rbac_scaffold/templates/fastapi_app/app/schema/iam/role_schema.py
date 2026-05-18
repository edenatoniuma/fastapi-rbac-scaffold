from __future__ import annotations

from app.schema.base import SortCamelModel, UpdateCamelModel
from app.schema.response import ResponseCamelModel


class RoleQuerySchema(SortCamelModel):
    tenant_id: int | None = None
    name: str | None = None
    code: str | None = None
    status: str | None = None


class RoleCreateSchema(UpdateCamelModel):
    name: str
    code: str
    tenant_id: int | None = None
    is_system_preset: bool = False
    status: str = "active"


class RoleUpdateSchema(UpdateCamelModel):
    name: str | None = None
    status: str | None = None


class AssignPermissionsSchema(UpdateCamelModel):
    permission_ids: list[int]


class RoleItemSchema(ResponseCamelModel):
    tenant_id: int | None = None
    name: str
    code: str
    is_system_preset: bool
    status: str

