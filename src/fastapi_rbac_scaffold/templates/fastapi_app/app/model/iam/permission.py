from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.model.iam.mixins import TimestampMixin


class Permission(TimestampMixin, Base):
    __tablename__ = "iam_permission"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    module: Mapped[str] = mapped_column(String(64), index=True)
    resource: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)

    role_links = relationship("RolePermission", back_populates="permission")
    feature_links = relationship("FeaturePermission", back_populates="permission")


class Feature(TimestampMixin, Base):
    __tablename__ = "iam_feature"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)

    plan_links = relationship("PlanFeature", back_populates="feature")
    permission_links = relationship("FeaturePermission", back_populates="feature")

