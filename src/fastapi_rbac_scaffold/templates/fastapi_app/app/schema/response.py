from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from app.schema.base import CamelModel


T = TypeVar("T")


class ResponseSchema(CamelModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: T | None = None


class ListSchema(CamelModel, Generic[T]):
    items: list[T]
    total: int
    start: int
    limit: int


class ResponseCamelModel(CamelModel):
    id: int
    gmt_create: datetime | None = None
    gmt_modified: datetime | None = None

