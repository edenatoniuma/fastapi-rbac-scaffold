"""initial iam schema

Revision ID: 0001_initial_iam
Revises:
Create Date: 2026-05-18
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_iam"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "iam_feature",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("gmt_create", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("gmt_modified", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_iam_feature_code"), "iam_feature", ["code"], unique=True)
    op.create_index(op.f("ix_iam_feature_status"), "iam_feature", ["status"], unique=False)

    op.create_table(
        "iam_permission",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("resource", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("gmt_create", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("gmt_modified", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_iam_permission_action"), "iam_permission", ["action"], unique=False)
    op.create_index(op.f("ix_iam_permission_code"), "iam_permission", ["code"], unique=True)
    op.create_index(op.f("ix_iam_permission_module"), "iam_permission", ["module"], unique=False)
    op.create_index(op.f("ix_iam_permission_resource"), "iam_permission", ["resource"], unique=False)
    op.create_index(op.f("ix_iam_permission_status"), "iam_permission", ["status"], unique=False)

    op.create_table(
        "iam_plan",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("gmt_create", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("gmt_modified", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_iam_plan_code"), "iam_plan", ["code"], unique=True)
    op.create_index(op.f("ix_iam_plan_status"), "iam_plan", ["status"], unique=False)

    op.create_table(
        "iam_user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_platform_admin", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("gmt_create", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("gmt_modified", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_iam_user_email"), "iam_user", ["email"], unique=True)
    op.create_index(op.f("ix_iam_user_status"), "iam_user", ["status"], unique=False)
    op.create_index(op.f("ix_iam_user_username"), "iam_user", ["username"], unique=True)

    op.create_table(
        "iam_feature_permission",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("feature_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.Column("gmt_create", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("gmt_modified", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["feature_id"], ["iam_feature.id"]),
        sa.ForeignKeyConstraint(["permission_id"], ["iam_permission.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("feature_id", "permission_id", name="uq_feature_permission"),
    )
    op.create_index(op.f("ix_iam_feature_permission_feature_id"), "iam_feature_permission", ["feature_id"], unique=False)
    op.create_index(op.f("ix_iam_feature_permission_permission_id"), "iam_feature_permission", ["permission_id"], unique=False)

    op.create_table(
        "iam_plan_feature",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("feature_id", sa.Integer(), nullable=False),
        sa.Column("gmt_create", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("gmt_modified", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["feature_id"], ["iam_feature.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["iam_plan.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plan_id", "feature_id", name="uq_plan_feature"),
    )
    op.create_index(op.f("ix_iam_plan_feature_feature_id"), "iam_plan_feature", ["feature_id"], unique=False)
    op.create_index(op.f("ix_iam_plan_feature_plan_id"), "iam_plan_feature", ["plan_id"], unique=False)

    op.create_table(
        "iam_tenant",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("gmt_create", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("gmt_modified", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["iam_plan.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_iam_tenant_code"), "iam_tenant", ["code"], unique=True)
    op.create_index(op.f("ix_iam_tenant_name"), "iam_tenant", ["name"], unique=True)
    op.create_index(op.f("ix_iam_tenant_status"), "iam_tenant", ["status"], unique=False)

    op.create_table(
        "iam_role",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("is_system_preset", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("gmt_create", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("gmt_modified", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["iam_tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_role_tenant_code"),
    )
    op.create_index(op.f("ix_iam_role_code"), "iam_role", ["code"], unique=False)
    op.create_index(op.f("ix_iam_role_status"), "iam_role", ["status"], unique=False)
    op.create_index(op.f("ix_iam_role_tenant_id"), "iam_role", ["tenant_id"], unique=False)

    op.create_table(
        "iam_tenant_user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("gmt_create", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("gmt_modified", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["iam_tenant.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["iam_user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_tenant_user"),
    )
    op.create_index(op.f("ix_iam_tenant_user_status"), "iam_tenant_user", ["status"], unique=False)
    op.create_index(op.f("ix_iam_tenant_user_tenant_id"), "iam_tenant_user", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_iam_tenant_user_user_id"), "iam_tenant_user", ["user_id"], unique=False)

    op.create_table(
        "iam_role_permission",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.Column("gmt_create", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("gmt_modified", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["iam_permission.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["iam_role.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )
    op.create_index(op.f("ix_iam_role_permission_permission_id"), "iam_role_permission", ["permission_id"], unique=False)
    op.create_index(op.f("ix_iam_role_permission_role_id"), "iam_role_permission", ["role_id"], unique=False)

    op.create_table(
        "iam_tenant_user_role",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("gmt_create", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("gmt_modified", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["iam_role.id"]),
        sa.ForeignKeyConstraint(["tenant_user_id"], ["iam_tenant_user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_user_id", "role_id", name="uq_tenant_user_role"),
    )
    op.create_index(op.f("ix_iam_tenant_user_role_role_id"), "iam_tenant_user_role", ["role_id"], unique=False)
    op.create_index(op.f("ix_iam_tenant_user_role_tenant_user_id"), "iam_tenant_user_role", ["tenant_user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_iam_tenant_user_role_tenant_user_id"), table_name="iam_tenant_user_role")
    op.drop_index(op.f("ix_iam_tenant_user_role_role_id"), table_name="iam_tenant_user_role")
    op.drop_table("iam_tenant_user_role")
    op.drop_index(op.f("ix_iam_role_permission_role_id"), table_name="iam_role_permission")
    op.drop_index(op.f("ix_iam_role_permission_permission_id"), table_name="iam_role_permission")
    op.drop_table("iam_role_permission")
    op.drop_index(op.f("ix_iam_tenant_user_user_id"), table_name="iam_tenant_user")
    op.drop_index(op.f("ix_iam_tenant_user_tenant_id"), table_name="iam_tenant_user")
    op.drop_index(op.f("ix_iam_tenant_user_status"), table_name="iam_tenant_user")
    op.drop_table("iam_tenant_user")
    op.drop_index(op.f("ix_iam_role_tenant_id"), table_name="iam_role")
    op.drop_index(op.f("ix_iam_role_status"), table_name="iam_role")
    op.drop_index(op.f("ix_iam_role_code"), table_name="iam_role")
    op.drop_table("iam_role")
    op.drop_index(op.f("ix_iam_tenant_status"), table_name="iam_tenant")
    op.drop_index(op.f("ix_iam_tenant_name"), table_name="iam_tenant")
    op.drop_index(op.f("ix_iam_tenant_code"), table_name="iam_tenant")
    op.drop_table("iam_tenant")
    op.drop_index(op.f("ix_iam_plan_feature_plan_id"), table_name="iam_plan_feature")
    op.drop_index(op.f("ix_iam_plan_feature_feature_id"), table_name="iam_plan_feature")
    op.drop_table("iam_plan_feature")
    op.drop_index(op.f("ix_iam_feature_permission_permission_id"), table_name="iam_feature_permission")
    op.drop_index(op.f("ix_iam_feature_permission_feature_id"), table_name="iam_feature_permission")
    op.drop_table("iam_feature_permission")
    op.drop_index(op.f("ix_iam_user_username"), table_name="iam_user")
    op.drop_index(op.f("ix_iam_user_status"), table_name="iam_user")
    op.drop_index(op.f("ix_iam_user_email"), table_name="iam_user")
    op.drop_table("iam_user")
    op.drop_index(op.f("ix_iam_plan_status"), table_name="iam_plan")
    op.drop_index(op.f("ix_iam_plan_code"), table_name="iam_plan")
    op.drop_table("iam_plan")
    op.drop_index(op.f("ix_iam_permission_status"), table_name="iam_permission")
    op.drop_index(op.f("ix_iam_permission_resource"), table_name="iam_permission")
    op.drop_index(op.f("ix_iam_permission_module"), table_name="iam_permission")
    op.drop_index(op.f("ix_iam_permission_code"), table_name="iam_permission")
    op.drop_index(op.f("ix_iam_permission_action"), table_name="iam_permission")
    op.drop_table("iam_permission")
    op.drop_index(op.f("ix_iam_feature_status"), table_name="iam_feature")
    op.drop_index(op.f("ix_iam_feature_code"), table_name="iam_feature")
    op.drop_table("iam_feature")

