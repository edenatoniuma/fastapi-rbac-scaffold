from __future__ import annotations

import argparse
import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, close_database
from app.model.iam import (
    Feature,
    FeaturePermission,
    Permission,
    Plan,
    PlanFeature,
)


DEFAULT_PERMISSIONS = [
    ("iam:tenant:list", "List tenants", "iam", "tenant", "list"),
    ("iam:tenant:create", "Create tenant", "iam", "tenant", "create"),
    ("iam:tenant:detail", "Get tenant detail", "iam", "tenant", "detail"),
    ("iam:tenant:update", "Update tenant", "iam", "tenant", "update"),
    ("iam:tenant:delete", "Delete tenant", "iam", "tenant", "delete"),
    ("iam:user:list", "List users", "iam", "user", "list"),
    ("iam:user:create", "Create user", "iam", "user", "create"),
    ("iam:user:detail", "Get user detail", "iam", "user", "detail"),
    ("iam:user:update", "Update user", "iam", "user", "update"),
    ("iam:user:delete", "Delete user", "iam", "user", "delete"),
    ("iam:user:assign_role", "Assign user roles", "iam", "user", "assign_role"),
    ("iam:role:list", "List roles", "iam", "role", "list"),
    ("iam:role:create", "Create role", "iam", "role", "create"),
    ("iam:role:update", "Update role", "iam", "role", "update"),
    ("iam:role:delete", "Delete role", "iam", "role", "delete"),
    (
        "iam:role:assign_permission",
        "Assign role permissions",
        "iam",
        "role",
        "assign_permission",
    ),
    ("iam:permission:list", "List permissions", "iam", "permission", "list"),
    ("iam:permission:create", "Create permission", "iam", "permission", "create"),
    ("iam:plan:list", "List plans", "iam", "plan", "list"),
    ("iam:plan:create", "Create plan", "iam", "plan", "create"),
    ("iam:plan:update", "Update plan", "iam", "plan", "update"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="app-seed-iam",
        description="Seed default IAM permissions, feature, and plan.",
    )
    parser.add_argument("--plan-code", default="default")
    parser.add_argument("--plan-name", default="Default Plan")
    parser.add_argument("--feature-code", default="iam")
    parser.add_argument("--feature-name", default="IAM")
    return parser


async def seed_iam(
    *,
    plan_code: str,
    plan_name: str,
    feature_code: str,
    feature_name: str,
) -> None:
    async with AsyncSessionLocal() as db:
        feature = await db.scalar(select(Feature).where(Feature.code == feature_code))
        if feature is None:
            feature = Feature(code=feature_code, name=feature_name, status="active")
            db.add(feature)
            await db.flush()

        plan = await db.scalar(select(Plan).where(Plan.code == plan_code))
        if plan is None:
            plan = Plan(code=plan_code, name=plan_name, status="active")
            db.add(plan)
            await db.flush()

        existing_plan_feature = await db.scalar(
            select(PlanFeature)
            .where(PlanFeature.plan_id == plan.id)
            .where(PlanFeature.feature_id == feature.id)
        )
        if existing_plan_feature is None:
            db.add(PlanFeature(plan_id=plan.id, feature_id=feature.id))

        for code, name, module, resource, action in DEFAULT_PERMISSIONS:
            permission = await db.scalar(select(Permission).where(Permission.code == code))
            if permission is None:
                permission = Permission(
                    code=code,
                    name=name,
                    module=module,
                    resource=resource,
                    action=action,
                    status="active",
                )
                db.add(permission)
                await db.flush()

            existing_feature_permission = await db.scalar(
                select(FeaturePermission)
                .where(FeaturePermission.feature_id == feature.id)
                .where(FeaturePermission.permission_id == permission.id)
            )
            if existing_feature_permission is None:
                db.add(
                    FeaturePermission(
                        feature_id=feature.id,
                        permission_id=permission.id,
                    )
                )

        await db.commit()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    async def runner() -> None:
        try:
            await seed_iam(
                plan_code=args.plan_code,
                plan_name=args.plan_name,
                feature_code=args.feature_code,
                feature_name=args.feature_name,
            )
        finally:
            await close_database()

    asyncio.run(runner())

    print("Default IAM permissions, feature, and plan are ready.")


if __name__ == "__main__":
    main()
