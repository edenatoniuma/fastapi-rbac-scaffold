# FastAPI 工程骨架拆分设计

适用目标：从当前 `AI_management_platform` 中抽离一个干净、可复用的 FastAPI 工程脚手架。

边界说明：

- 只保留工程骨架、基础设施、统一规范和多租户 RBAC 鉴权设计。
- 不保留 AI 平台业务，包括 Agent、LangGraph、聊天流式、模型供应商、工具执行、记忆系统、模板、草稿发布等能力。
- RBAC 以 `misc/RBAC.md` 的设计为准，不与现有项目中的系统表、菜单表、功能表实现强绑定。

## 1. 脚手架定位

脚手架应该解决的是“一个新的 FastAPI 后端项目如何快速落地”，而不是复制当前 AI 平台。

默认能力：

- FastAPI 应用工厂
- lifespan 启停管理
- 路由统一注册
- 全局异常处理
- 统一响应格式
- Pydantic schema 基类
- Async SQLAlchemy
- Alembic migration
- Redis client
- JWT 登录鉴权
- 多租户 RBAC
- 权限缓存
- 分页、排序、筛选 helper
- 日志配置
- OpenTelemetry 可选接入
- Docker 本地开发环境

不进入脚手架默认层的能力：

- Agent 应用管理
- Agent draft / publish / version
- LangGraph runtime
- GraphManager
- Postgres checkpointer
- SSE chat streaming
- Async chat worker
- TurnEventBus
- MemorySyncWorker
- Weaviate memory store
- Model provider
- Tool validation / execution
- Agent template
- SSO
- Agent 统计聚合

## 2. 推荐目录结构

```text
fastapi_scaffold/
  app/
    main.py
    api/
      __init__.py
      health.py
      auth/
        __init__.py
        auth_api.py
      iam/
        __init__.py
        tenant_api.py
        user_api.py
        role_api.py
        permission_api.py
        plan_api.py
    config/
      __init__.py
      settings.py
      logging.py
    core/
      __init__.py
      database.py
      redis.py
      errors.py
      pagination.py
      tracing.py
    deps/
      __init__.py
      auth.py
      database.py
      redis.py
    middleware/
      __init__.py
      auth_middleware.py
      request_context.py
      tenant_context.py
    model/
      __init__.py
      base.py
      iam/
        __init__.py
        tenant.py
        user.py
        role.py
        permission.py
        plan.py
        association.py
    schema/
      __init__.py
      base.py
      response.py
      iam/
        __init__.py
        auth_schema.py
        tenant_schema.py
        user_schema.py
        role_schema.py
        permission_schema.py
        plan_schema.py
    service/
      __init__.py
      common_service.py
      cache_service.py
      iam/
        __init__.py
        auth_service.py
        tenant_service.py
        user_service.py
        role_service.py
        permission_service.py
        plan_service.py
    security/
      __init__.py
      jwt.py
      password.py
      permission.py
    utils/
      __init__.py
      time.py
      ids.py

  migrations/
  docker/
  log_config/
  scripts/
  tests/
  .env.example
  alembic.ini
  docker-compose.yml
  pyproject.toml
  README.md
```

## 3. 分层职责

### `app/main.py`

只负责应用装配：

- `setup_telemetry()`
- `create_app()`
- `build_lifespan()`
- `register_exception_handlers()`
- `register_middlewares()`
- `include_routers()`

脚手架版 `main.py` 不应该初始化任何业务 runtime，例如 GraphManager、聊天 worker、记忆 worker、checkpointer。

### `api`

只处理 HTTP 层：

- 路由定义
- 入参 schema
- 当前用户依赖
- 权限依赖
- 调用 service
- 返回统一响应

不在 API 层写复杂业务逻辑。

### `service`

处理业务编排：

- 登录
- 用户管理
- 租户管理
- 角色权限分配
- 套餐权限校验
- 缓存失效
- 数据权限检查

### `model`

SQLAlchemy ORM 模型层。

所有业务表如果需要租户隔离，必须有 `tenant_id`。平台级全局配置表可以不带 `tenant_id`，但必须明确标记。

### `schema`

Pydantic 请求/响应模型。

保留通用基类：

- `CamelModel`
- `SortCamelModel`
- `UpdateCamelModel`
- `ResponseCamelModel`
- `ResponseSchema[T]`
- `ListSchema[T]`

### `deps`

FastAPI dependency：

- 获取 DB session
- 获取 Redis client
- 解析当前登录主体
- 接口级权限校验
- 平台管理员校验
- 当前租户上下文校验

### `middleware`

只做横切拦截，不承载复杂鉴权逻辑。

建议保留：

- 全局异常兜底
- request id / trace id
- CORS
- AuthMiddleware 粗拦截
- tenant context 初始化

## 4. RBAC 核心模型

以 `misc/RBAC.md` 为准，采用多租户 RBAC。

核心表：

```text
User
Tenant
TenantUser
Role
Permission
Plan
Feature
```

关联表：

```text
TenantUserRole
RolePermission
PlanFeature
FeaturePermission
```

关系：

```text
User <-> TenantUser <-> Tenant
TenantUser <-> TenantUserRole <-> Role
Role <-> RolePermission <-> Permission
Tenant <-> Plan
Plan <-> PlanFeature <-> Feature
Feature <-> FeaturePermission <-> Permission
```

核心规则：

- 用户可以加入多个租户。
- 用户在不同租户下可以拥有不同角色。
- 角色可以是系统预设角色，也可以是租户自定义角色。
- 权限是系统定义的原子能力。
- 租户可用权限受套餐约束。
- 租户管理员只能在本租户套餐允许范围内分配权限。
- 普通租户用户不能访问其他租户数据。
- 平台管理员可以跨租户，但跨租户操作必须显式表达目标租户。

## 5. 接口鉴权设计

接口鉴权分三层。

### 5.1 `AuthMiddleware`：粗拦截

职责：

- 放行 `OPTIONS`
- 放行白名单路径
- 对受保护路径检查是否存在 `Authorization: Bearer <token>`
- 可选检查 token 格式

不做：

- 不解 JWT
- 不查用户
- 不查角色
- 不判断接口权限
- 不判断数据权限

推荐白名单：

```text
/docs
/openapi.json
/api/health
/api/auth/login
/api/auth/refresh
```

### 5.2 `get_current_principal`：解析身份

作为 FastAPI dependency。

职责：

- 解析 JWT
- 校验 token 类型和过期时间
- 检查 Redis token blacklist
- 获取 `user_id`
- 获取当前 `tenant_id`
- 校验用户状态
- 校验租户状态
- 校验用户是否属于当前租户
- 加载角色和权限
- 返回当前请求主体

当前主体建议结构：

```python
class CurrentPrincipal(BaseModel):
    user_id: int
    username: str
    tenant_id: int
    is_platform_admin: bool = False
    role_ids: list[int] = []
    permissions: set[str] = set()
```

JWT 建议只放必要信息：

```json
{
  "sub": "123",
  "tenant_id": 101,
  "session_id": "uuid",
  "type": "access",
  "exp": 1234567890
}
```

不要把完整权限列表长期放进 JWT。权限会变更，应该从 Redis 缓存或 DB 加载。

### 5.3 `require_permission`：接口级权限声明

每个需要鉴权的接口显式声明权限。

示例：

```python
@router.post("/users")
async def create_user(
    data: UserCreateSchema,
    current: CurrentPrincipal = Depends(require_permission("iam:user:create")),
):
    ...
```

推荐实现形态：

```python
def require_permission(permission_code: str):
    async def dependency(
        current: CurrentPrincipal = Depends(get_current_principal),
    ) -> CurrentPrincipal:
        if current.is_platform_admin:
            return current

        if permission_code not in current.permissions:
            raise HTTPException(status_code=403, detail="无权限访问")

        return current

    return dependency
```

平台管理员接口单独声明：

```python
@router.post("/tenants")
async def create_tenant(
    data: TenantCreateSchema,
    current: CurrentPrincipal = Depends(require_platform_admin),
):
    ...
```

## 6. 多租户数据隔离

强约束：

- 不信任前端传入的 `tenant_id`。
- 普通用户的 `tenant_id` 只能来自服务端上下文。
- 业务查询必须自动带上 `tenant_id = current.tenant_id`。
- 更新、删除、详情查询必须校验对象所属租户。
- 平台管理员跨租户操作必须显式传目标租户，并在 service 层校验。

推荐 helper：

```text
apply_tenant_scope(query, current)
ensure_tenant_access(obj, current)
get_tenant_obj_or_404(model, id, current)
require_platform_admin(current)
```

普通租户查询示例：

```python
@router.get("/users")
async def list_users(
    query: UserQuerySchema,
    current: CurrentPrincipal = Depends(require_permission("iam:user:list")),
    db: AsyncSession = Depends(get_db),
):
    query.tenant_id = current.tenant_id
    ...
```

## 7. 权限缓存设计

权限不建议放在 JWT 中长期使用，推荐 Redis 缓存。

缓存 key：

```text
rbac:user_permissions:{tenant_id}:{user_id}
rbac:tenant_plan_permissions:{tenant_id}
rbac:role_permissions:{role_id}
```

缓存内容：

```json
{
  "role_ids": [1, 2],
  "permissions": ["iam:user:list", "iam:user:create"]
}
```

需要失效缓存的场景：

- 用户角色变更
- 角色权限变更
- 权限定义变更
- 租户套餐变更
- 套餐功能变更
- 功能权限变更
- 用户被禁用
- 租户被禁用

## 8. 权限命名规范

推荐格式：

```text
<module>:<resource>:<action>
```

示例：

```text
iam:user:list
iam:user:create
iam:user:update
iam:user:delete
iam:role:list
iam:role:assign_permission
iam:tenant:create
iam:plan:update
```

常用 action：

```text
list
detail
create
update
delete
enable
disable
assign
export
import
```

## 9. 应用启动生命周期

脚手架默认 lifespan：

```text
start
  初始化 Redis
  初始化 DB engine/session
  初始化可选 scheduler
  初始化可选 telemetry
ready
shutdown
  关闭 scheduler
  关闭 Redis
  关闭 DB engine
```

不包含：

- LangGraph checkpointer
- GraphManager listener
- Graph cleanup loop
- Chat worker
- Memory worker
- Agent post-commit worker

## 10. 默认 API

脚手架初版建议只保留这些 API。

基础接口：

```text
GET /api/health
```

认证接口：

```text
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh
GET  /api/auth/me
```

IAM 接口：

```text
POST /api/iam/tenants/list
POST /api/iam/tenants
GET  /api/iam/tenants/{tenant_id}
PUT  /api/iam/tenants/{tenant_id}
DELETE /api/iam/tenants/{tenant_id}

POST /api/iam/users/list
POST /api/iam/users
GET  /api/iam/users/{user_id}
PUT  /api/iam/users/{user_id}
DELETE /api/iam/users/{user_id}

POST /api/iam/roles/list
POST /api/iam/roles
PUT  /api/iam/roles/{role_id}
DELETE /api/iam/roles/{role_id}
POST /api/iam/roles/{role_id}/permissions

POST /api/iam/permissions/list

POST /api/iam/plans/list
POST /api/iam/plans
PUT  /api/iam/plans/{plan_id}
POST /api/iam/plans/{plan_id}/features
```

## 11. 从现有项目抽离时删除的内容

可以直接不迁移：

```text
app/api/agent/
app/api/model_provider/
app/api/datasets/
app/service/agent_app/
app/service/model_provider/
app/service/sso/
app/model/agent_table/
app/model/dataset/
app/model/sso/
app/schema/agent_app/
app/schema/model_provider/
app/schema/sso/
app/enum/agent_*
workflow/
problem/
problem_solved/
todo_list/
todo_list_completed/
study/
performance_report/
references/
data_migration/
version/
```

需要重写或精简：

```text
app/main.py
app/api/__init__.py
app/service/__init__.py
app/model/__init__.py
app/schema/__init__.py
app/config/app_config.py
docker-compose.yml
pyproject.toml
README.md
```

可以复用思想但不直接照搬业务实现：

```text
app/service/common_service.py
app/schema/base_schema.py
app/schema/response_schema.py
app/middleware/auth_middleware.py
app/core/tracing.py
app/core/database_connect.py
```

## 12. 初版落地顺序

推荐按以下顺序实现脚手架：

1. 建立目录结构和 `pyproject.toml`。
2. 实现配置读取和 `.env.example`。
3. 实现 DB、Redis、lifespan。
4. 实现统一响应和异常处理。
5. 实现基础 schema/model/service 分层。
6. 实现 JWT、密码哈希和登录接口。
7. 实现 `CurrentPrincipal` 和权限 dependency。
8. 实现 Tenant/User/Role/Permission/Plan 模型。
9. 实现 Alembic 初始 migration。
10. 实现 IAM CRUD。
11. 实现权限缓存和缓存失效。
12. 补 README、启动命令和最小测试。

## 13. 最小交付标准

脚手架完成后，至少应满足：

- 可以通过 Docker 启动 Postgres 和 Redis。
- 可以执行 Alembic migration。
- 可以启动 FastAPI 服务。
- 可以创建平台管理员。
- 可以创建租户。
- 可以创建租户用户。
- 可以登录并获得 JWT。
- 可以通过 `require_permission` 限制接口访问。
- 普通用户不能跨租户访问数据。
- 角色权限变更后权限缓存能失效。
- 新增一个普通资源时，只需要新增 model/schema/service/api/migration。

