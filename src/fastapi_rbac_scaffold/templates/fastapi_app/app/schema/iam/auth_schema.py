from __future__ import annotations

from app.schema.base import CamelModel


class LoginRequest(CamelModel):
    username: str
    password: str
    tenant_id: int | None = None


class LoginResponse(CamelModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class PrincipalSchema(CamelModel):
    user_id: int
    username: str
    tenant_id: int | None = None
    is_platform_admin: bool = False
    role_ids: list[int] = []
    permissions: list[str] = []

