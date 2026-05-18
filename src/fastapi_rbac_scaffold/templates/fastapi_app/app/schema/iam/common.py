from __future__ import annotations

from app.schema.base import CamelModel


class IdsSchema(CamelModel):
    ids: list[int]

