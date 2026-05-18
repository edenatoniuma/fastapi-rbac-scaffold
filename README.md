# fastapi-rbac-scaffold

A PyPI-ready scaffold generator for creating FastAPI services with async SQLAlchemy, Redis, JWT authentication, and multi-tenant RBAC.

## Usage

```bash
pip install fastapi-rbac-scaffold
fastapi-rbac-scaffold new acme-api
cd acme-api
copy .env.example .env
docker compose up -d postgres redis
pip install -e ".[dev]"
alembic upgrade head
app-seed-iam
app-bootstrap --username admin --password change-me --email admin@example.com
uvicorn app.main:app --reload
```

## Layout

```text
src/fastapi_rbac_scaffold/
  cli/          # Command-line entrypoints
  generator/    # Project generation logic
  templates/    # Files copied into generated FastAPI projects
```

The generated FastAPI application template lives under:

```text
src/fastapi_rbac_scaffold/templates/fastapi_app/
```

## Generated App

The generated application includes:

- FastAPI app factory and lifespan
- async SQLAlchemy setup
- Redis lifecycle management
- Alembic initial IAM migration
- JWT login, refresh, logout, and `/me`
- multi-tenant RBAC models
- permission dependency helpers
- IAM tenant/user/role/permission/plan API skeletons
