from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from importlib import resources
from pathlib import Path


PROJECT_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


@dataclass(frozen=True)
class ProjectContext:
    project_name: str
    package_name: str


def normalize_package_name(name: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z_]+", "_", name).lower().strip("_")
    if not normalized:
        raise ValueError("Project name cannot produce an empty package name.")
    if normalized[0].isdigit():
        normalized = f"app_{normalized}"
    return normalized


def validate_project_name(name: str) -> None:
    if not PROJECT_NAME_RE.fullmatch(name):
        raise ValueError(
            "Project name must start with a letter and contain only letters, numbers, '-' or '_'."
        )


def create_project(
    *,
    name: str,
    directory: Path,
    package_name: str | None = None,
    force: bool = False,
) -> Path:
    validate_project_name(name)
    target_dir = directory.resolve() / name
    context = ProjectContext(
        project_name=name,
        package_name=package_name or normalize_package_name(name),
    )

    if target_dir.exists():
        if not target_dir.is_dir():
            raise FileExistsError(f"Target exists and is not a directory: {target_dir}")
        if any(target_dir.iterdir()) and not force:
            raise FileExistsError(
                f"Target directory is not empty: {target_dir}. Use --force to allow an existing empty directory."
            )
    else:
        target_dir.mkdir(parents=True)

    template_root = resources.files("fastapi_rbac_scaffold.templates").joinpath(
        "fastapi_app"
    )
    with resources.as_file(template_root) as source_dir:
        copy_template(source_dir, target_dir, context)

    return target_dir


def copy_template(source_dir: Path, target_dir: Path, context: ProjectContext) -> None:
    for source_path in source_dir.rglob("*"):
        relative_path = source_path.relative_to(source_dir)
        if source_path.name == ".template-root":
            continue

        rendered_relative = render_text(str(relative_path), context)
        target_path = target_dir / rendered_relative

        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            continue

        target_path.parent.mkdir(parents=True, exist_ok=True)
        if is_text_template(source_path):
            content = source_path.read_text(encoding="utf-8")
            target_path.write_text(render_text(content, context), encoding="utf-8")
        else:
            shutil.copy2(source_path, target_path)


def is_text_template(path: Path) -> bool:
    if path.suffix.lower() in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".ico"}:
        return False
    return True


def render_text(value: str, context: ProjectContext) -> str:
    return (
        value.replace("{{ project_name }}", context.project_name)
        .replace("{{ package_name }}", context.package_name)
        .replace("{{ package_name_upper }}", context.package_name.upper())
    )

