# Repository Guidelines

## Project Structure & Module Organization

This repository is a Python package that generates a FastAPI RBAC scaffold. Package code lives in `src/fastapi_rbac_scaffold/`: `cli/` contains the console entrypoint, `generator/` contains project creation logic, and `templates/fastapi_app/` contains the files copied into generated applications. Tests live in `tests/`, with `tests/test_generator.py` covering name normalization and scaffold output. Design notes and domain references are in `FASTAPI_SCAFFOLD_DESIGN.md`, `RBAC.md`, and `docs/`. The `dist/` directory is build output and should not be edited by hand.

## Build, Test, and Development Commands

Use Python 3.12 or newer. Install the package for local development with:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Build distribution artifacts:

```bash
python -m build
```

Exercise the CLI locally:

```bash
fastapi-rbac-scaffold new demo-api
```

Inside a generated app, follow its `README.md` for `docker compose`, Alembic, seed, bootstrap, and `uvicorn app.main:app --reload` commands.

## Coding Style & Naming Conventions

Write typed, idiomatic Python with 4-space indentation and `from __future__ import annotations` where it matches existing modules. Use `snake_case` for functions, variables, modules, and test files; use `PascalCase` for classes. Keep generator behavior in `generator/project.py`, CLI parsing in `cli/main.py`, and template application code inside `templates/fastapi_app/`. Prefer `pathlib.Path` for filesystem work and UTF-8 when reading or writing template files.

## Testing Guidelines

Tests use `pytest`. Add tests under `tests/` using `test_*.py` files and `test_*` functions. For generator changes, assert both filesystem output and rendered template content, similar to `test_create_project`. Clean up temporary output directories so local runs do not leave generated projects behind.

## Commit & Pull Request Guidelines

Current history only shows the initial `first-commit`, so no strict commit convention is established. Use concise imperative commit messages, for example `Add scaffold template tests` or `Update CLI error handling`. Pull requests should describe the change, note test commands run, and call out any generated-template behavior changes. Link related issues when available and include screenshots only if documentation or generated UI output changes.

## Security & Configuration Tips

Do not commit real secrets. Keep example configuration in `templates/fastapi_app/.env.example`, and document new required settings in the generated app `README.md`. Treat generated authentication, JWT, Redis, and database defaults as development defaults unless explicitly hardened.
