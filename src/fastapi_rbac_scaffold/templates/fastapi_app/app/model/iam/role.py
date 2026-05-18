from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.model.iam.mixins import TimestampMixin


class Role(TimestampMixin, Base):
    __tablename__ = "iam_role"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_role_tenant_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("iam_tenant.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(128))
    code: Mapped[str] = mapped_column(String(64), index=True)
    is_system_preset: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)

    permission_links = relationship("RolePermission", back_populates="role")
    tenant_user_links = relationship("TenantUserRole", back_populates="role")

