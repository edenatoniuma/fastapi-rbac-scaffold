from __future__ import annotations

from app.schema.base import SortCamelModel, UpdateCamelModel
from app.schema.response import ResponseCamelModel


class UserQuerySchema(SortCamelModel):
    username: str | None = None
    email: str | None = None
    status: str | None = None


class UserCreateSchema(UpdateCamelModel):
    username: str
    password: str
    email: str | None = None
    tenant_id: int | None = None
    is_platform_admin: bool = False
    status: str = "active"


class UserUpdateSchema(UpdateCamelModel):
    email: str | None = None
    password: str | None = None
    status: str | None = None


class TenantMembershipSchema(UpdateCamelModel):
    tenant_id: int


class AssignUserRolesSchema(UpdateCamelModel):
    tenant_id: int
    role_ids: list[int]


class UserItemSchema(ResponseCamelModel):
    username: str
    email: str | None = None
    is_platform_admin: bool
    status: str
