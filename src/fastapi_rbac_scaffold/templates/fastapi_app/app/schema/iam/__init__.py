from app.schema.iam.auth_schema import LoginRequest, LoginResponse, PrincipalSchema
from app.schema.iam.common import IdsSchema
from app.schema.iam.permission_schema import (
    FeatureCreateSchema,
    FeatureItemSchema,
    PermissionCreateSchema,
    PermissionItemSchema,
    PermissionQuerySchema,
)
from app.schema.iam.plan_schema import (
    PlanCreateSchema,
    PlanItemSchema,
    PlanQuerySchema,
    PlanUpdateSchema,
)
from app.schema.iam.role_schema import (
    AssignPermissionsSchema,
    RoleCreateSchema,
    RoleItemSchema,
    RoleQuerySchema,
    RoleUpdateSchema,
)
from app.schema.iam.tenant_schema import (
    TenantCreateSchema,
    TenantItemSchema,
    TenantQuerySchema,
    TenantUpdateSchema,
)
from app.schema.iam.user_schema import (
    AssignUserRolesSchema,
    TenantMembershipSchema,
    UserCreateSchema,
    UserItemSchema,
    UserQuerySchema,
    UserUpdateSchema,
)

__all__ = [
    "AssignPermissionsSchema",
    "FeatureCreateSchema",
    "FeatureItemSchema",
    "IdsSchema",
    "LoginRequest",
    "LoginResponse",
    "PermissionCreateSchema",
    "PermissionItemSchema",
    "PermissionQuerySchema",
    "PlanCreateSchema",
    "PlanItemSchema",
    "PlanQuerySchema",
    "PlanUpdateSchema",
    "PrincipalSchema",
    "RoleCreateSchema",
    "RoleItemSchema",
    "RoleQuerySchema",
    "RoleUpdateSchema",
    "AssignUserRolesSchema",
    "TenantMembershipSchema",
    "TenantCreateSchema",
    "TenantItemSchema",
    "TenantQuerySchema",
    "TenantUpdateSchema",
    "UserCreateSchema",
    "UserItemSchema",
    "UserQuerySchema",
    "UserUpdateSchema",
]
