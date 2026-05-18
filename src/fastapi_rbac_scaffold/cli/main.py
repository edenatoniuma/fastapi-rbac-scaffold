from __future__ import annotations

import argparse
from pathlib import Path

from fastapi_rbac_scaffold.generator.project import create_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fastapi-rbac-scaffold",
        description="Create a FastAPI project with async SQLAlchemy, Redis, JWT, and multi-tenant RBAC.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("new", help="Create a new FastAPI project.")
    create_parser.add_argument("name", help="Project name, for example: acme-api")
    create_parser.add_argument(
        "--directory",
        "-d",
        type=Path,
        default=Path.cwd(),
        help="Parent directory for the generated project.",
    )
    create_parser.add_argument(
        "--package-name",
        help="Python package name for the generated app. Defaults to a normalized project name.",
    )
    create_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow writing into an existing empty directory.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "new":
        project_path = create_project(
            name=args.name,
            directory=args.directory,
            package_name=args.package_name,
            force=args.force,
        )
        print(f"Created project at {project_path}")
        return

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()

