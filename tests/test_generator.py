from __future__ import annotations

import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi_rbac_scaffold.generator.project import create_project, normalize_package_name


def test_normalize_package_name() -> None:
    assert normalize_package_name("Demo-API") == "demo_api"
    assert normalize_package_name("123-api") == "app_123_api"


def test_create_project() -> None:
    output_dir = Path(__file__).resolve().parents[1] / ".test-generated"
    project_path = output_dir / "demo-api"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    try:
        project_path = create_project(name="demo-api", directory=output_dir)

        assert (project_path / "pyproject.toml").exists()
        assert (project_path / "app" / "main.py").exists()
        assert (project_path / "app" / "cli" / "bootstrap.py").exists()
        assert (project_path / "app" / "cli" / "seed_iam.py").exists()
        assert (
            project_path / "migrations" / "versions" / "0001_initial_iam.py"
        ).exists()

        pyproject = (project_path / "pyproject.toml").read_text(encoding="utf-8")
        assert "app-bootstrap" in pyproject
        assert "app-seed-iam" in pyproject

        settings = (project_path / "app" / "config" / "settings.py").read_text(
            encoding="utf-8"
        )
        assert "{{ project_name }}" not in settings
        assert "demo-api" in settings
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)
