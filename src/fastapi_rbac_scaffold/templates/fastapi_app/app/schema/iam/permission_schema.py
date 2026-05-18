from __future__ import annotations

from app.schema.base import SortCamelModel, UpdateCamelModel
from app.schema.response import ResponseCamelModel


class PermissionQuerySchema(SortCamelModel):
    module: str | None = None
    resource: str | None = None
    action: str | None = None
    status: str | None = None


class PermissionCreateSchema(UpdateCamelModel):
    code: str
    name: str
    module: str
    resource: str
    action: str
    description: str | None = None
    status: str = "active"


class PermissionItemSchema(ResponseCamelModel):
    code: str
    name: str
    module: str
    resource: str
    action: str
    description: str | None = None
    status: str


class FeatureCreateSchema(UpdateCamelModel):
    code: str
    name: str
    description: str | None = None
    status: str = "active"


class FeatureItemSchema(ResponseCamelModel):
    code: str
    name: str
    description: str | None = None
    status: str

