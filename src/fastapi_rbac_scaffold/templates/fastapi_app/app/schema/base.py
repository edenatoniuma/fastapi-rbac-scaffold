from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class SortCamelModel(CamelModel):
    start: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=200)
    sort_field: str | None = None
    sort_order: str | None = Field(default=None, pattern="^(asc|desc)$")


class UpdateCamelModel(CamelModel):
    def apply(self, instance: Any, exclude: set[str] | None = None) -> Any:
        exclude = exclude or set()
        values = self.model_dump(exclude_unset=True, by_alias=False)
        for key, value in values.items():
            if key not in exclude:
                setattr(instance, key, value)
        return instance

