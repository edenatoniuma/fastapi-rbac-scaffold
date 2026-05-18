from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.model.iam.mixins import TimestampMixin


class Tenant(TimestampMixin, Base):
    __tablename__ = "iam_tenant"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    plan_id: Mapped[int | None] = mapped_column(ForeignKey("iam_plan.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)

    plan = relationship("Plan", back_populates="tenants")
    user_links = relationship("TenantUser", back_populates="tenant")


class TenantUser(TimestampMixin, Base):
    __tablename__ = "iam_tenant_user"
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="uq_tenant_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("iam_tenant.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("iam_user.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)

    tenant = relationship("Tenant", back_populates="user_links")
    user = relationship("User", back_populates="tenant_links")
    role_links = relationship("TenantUserRole", back_populates="tenant_user")

