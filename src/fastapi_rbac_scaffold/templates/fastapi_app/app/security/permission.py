from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CurrentPrincipal:
    user_id: int
    username: str
    tenant_id: int | None = None
    is_platform_admin: bool = False
    role_ids: list[int] = field(default_factory=list)
    permissions: set[str] = field(default_factory=set)

