from __future__ import annotations

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.model.iam.mixins import TimestampMixin


class TenantUserRole(TimestampMixin, Base):
    __tablename__ = "iam_tenant_user_role"
    __table_args__ = (
        UniqueConstraint("tenant_user_id", "role_id", name="uq_tenant_user_role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_user_id: Mapped[int] = mapped_column(
        ForeignKey("iam_tenant_user.id"), index=True
    )
    role_id: Mapped[int] = mapped_column(ForeignKey("iam_role.id"), index=True)

    tenant_user = relationship("TenantUser", back_populates="role_links")
    role = relationship("Role", back_populates="tenant_user_links")


class RolePermission(TimestampMixin, Base):
    __tablename__ = "iam_role_permission"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("iam_role.id"), index=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("iam_permission.id"), index=True
    )

    role = relationship("Role", back_populates="permission_links")
    permission = relationship("Permission", back_populates="role_links")


class PlanFeature(TimestampMixin, Base):
    __tablename__ = "iam_plan_feature"
    __table_args__ = (
        UniqueConstraint("plan_id", "feature_id", name="uq_plan_feature"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("iam_plan.id"), index=True)
    feature_id: Mapped[int] = mapped_column(ForeignKey("iam_feature.id"), index=True)

    plan = relationship("Plan", back_populates="feature_links")
    feature = relationship("Feature", back_populates="plan_links")


class FeaturePermission(TimestampMixin, Base):
    __tablename__ = "iam_feature_permission"
    __table_args__ = (
        UniqueConstraint(
            "feature_id", "permission_id", name="uq_feature_permission"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    feature_id: Mapped[int] = mapped_column(ForeignKey("iam_feature.id"), index=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("iam_permission.id"), index=True
    )

    feature = relationship("Feature", back_populates="permission_links")
    permission = relationship("Permission", back_populates="feature_links")

