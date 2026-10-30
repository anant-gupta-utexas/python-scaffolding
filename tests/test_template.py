"""Tests for the Copier template: each flavor must generate a project that passes its own gate.

uv run pytest                  # everything (the gate tests need network for `uv sync`)
uv run pytest -m "not gate"    # fast: structure, rendering, validation, update
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from copier import run_copy, run_update

REPO = Path(__file__).resolve().parents[1]
FLAVORS = ("library_cli", "service", "datascience")
PACKAGE = "demo_app"

# Paths that exist in exactly one flavor ({pkg} is the package name).
FLAVOR_ONLY = {
    "library_cli": [
        "src/{pkg}/cli.py",
        "src/{pkg}/__main__.py",
        "tests/unit/test_cli.py",
    ],
    "service": [
        "src/{pkg}/domain/errors.py",
        "src/{pkg}/application/use_cases/__init__.py",
        "src/{pkg}/infrastructure/api/app.py",
        "tests/e2e/test_api.py",
        "Dockerfile",
        "docker-compose.yml",
        ".dockerignore",
        ".env.example",
        "docs/03_guides/core_concepts.md",
    ],
    "datascience": [
        "src/{pkg}/paths.py",
        "src/{pkg}/ingest/__init__.py",
        "tests/unit/test_paths.py",
        "notebooks/.gitkeep",
    ],
}

# The template is deliberately organization-neutral; org-specific variants live in forks.
BANNED_WORDS = ("walmart", "wal-mart", "wibey", "artifactory", "sysproxy")


def answers(flavor: str, **extra: object) -> dict[str, object]:
    return {"project_name": "Demo App", "description": "A demo.", "flavor": flavor, **extra}


def generate(dst: Path, flavor: str, **extra: object) -> Path:
    """Render the template without running post-generation tasks (fast, offline)."""
    run_copy(
        str(REPO), dst, data=answers(flavor, **extra), defaults=True, skip_tasks=True, quiet=True
    )
    return dst


@pytest.fixture(scope="session")
def projects(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    root = tmp_path_factory.mktemp("generated")
    return {flavor: generate(root / flavor, flavor) for flavor in FLAVORS}


def test_template_is_organization_neutral() -> None:
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    this_file = Path(__file__).resolve()
    offenders = []
    for name in filter(None, listing.split("\0")):
        path = REPO / name
        if not path.is_file() or path.resolve() == this_file:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        offenders += [f"{name}: {word}" for word in BANNED_WORDS if word in text]
    assert not offenders


@pytest.mark.parametrize("flavor", FLAVORS)
def test_each_flavor_gets_only_its_own_files(flavor: str, projects: dict[str, Path]) -> None:
    project = projects[flavor]
    for other, paths in FLAVOR_ONLY.items():
        for template_path in paths:
            exists = (project / template_path.format(pkg=PACKAGE)).exists()
            assert exists == (other == flavor), f"{flavor}: {template_path}"


@pytest.mark.parametrize("flavor", FLAVORS)
def test_every_flavor_gets_the_shared_scaffolding(flavor: str, projects: dict[str, Path]) -> None:
    project = projects[flavor]
    for path in (
        "AGENTS.md",
        "CLAUDE.md",
        "STATUS.md",
        "README.md",
        "pyproject.toml",
        ".python-version",
        ".gitignore",
        ".copier-answers.yml",
        "scripts/check.sh",
        "scripts/new_feature.sh",
        "dev/_templates/plan.md",
        "docs/README.md",
        "docs/00_research/.gitkeep",
        "docs/04_testing/index.md",
        f"src/{PACKAGE}/__init__.py",
    ):
        assert (project / path).exists(), path
    assert os.access(project / "scripts/check.sh", os.X_OK)
    assert os.access(project / "scripts/new_feature.sh", os.X_OK)


@pytest.mark.parametrize("flavor", FLAVORS)
def test_no_unrendered_jinja_is_left_behind(flavor: str, projects: dict[str, Path]) -> None:
    leftovers = [
        str(path.relative_to(projects[flavor]))
        for path in projects[flavor].rglob("*")
        if path.is_file() and ("{{" in path.read_text(errors="ignore") or ".jinja" in path.name)
    ]
    assert not leftovers


def test_answers_file_records_the_choices(projects: dict[str, Path]) -> None:
    recorded = yaml.safe_load((projects["service"] / ".copier-answers.yml").read_text())
    assert recorded["flavor"] == "service"
    assert recorded["package_name"] == PACKAGE
    assert "is_service" not in recorded  # derived values are recomputed, never stored


def test_package_name_is_derived_from_the_project_name(tmp_path: Path) -> None:
    project = generate(tmp_path / "p", "library_cli", project_name="My Cool-App!")
    assert (project / "src/my_cool_app/cli.py").exists()
    assert 'name = "my-cool-app"' in (project / "pyproject.toml").read_text()


def test_python_version_and_coverage_floor_flow_into_the_config(tmp_path: Path) -> None:
    project = generate(tmp_path / "p", "library_cli", python_version="3.12", min_coverage=90)
    config = (project / "pyproject.toml").read_text()
    assert (project / ".python-version").read_text().strip() == "3.12"
    assert 'requires-python = ">=3.12"' in config
    assert 'target-version = "py312"' in config
    assert "fail_under = 90" in config


def test_quotes_in_the_description_stay_valid_toml(tmp_path: Path) -> None:
    import tomllib

    project = generate(tmp_path / "p", "service", description='Says "hi" to everyone')
    parsed = tomllib.loads((project / "pyproject.toml").read_text())
    assert parsed["project"]["description"] == 'Says "hi" to everyone'


@pytest.mark.parametrize("bad", ["Bad-Name", "1abc", "has space"])
def test_invalid_package_names_are_rejected(tmp_path: Path, bad: str) -> None:
    with pytest.raises(ValueError, match="package_name"):
        generate(tmp_path / "p", "library_cli", package_name=bad)


def test_coverage_floor_must_be_a_percentage(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="min_coverage"):
        generate(tmp_path / "p", "library_cli", min_coverage=150)


def test_new_feature_script_creates_the_planning_docs(projects: dict[str, Path]) -> None:
    project = projects["library_cli"]
    subprocess.run(["scripts/new_feature.sh", "user-auth"], cwd=project, check=True)
    feature = project / "dev/active/user-auth"
    assert sorted(p.name for p in feature.iterdir()) == [
        "user-auth-context.md",
        "user-auth-plan.md",
        "user-auth-tasks.md",
    ]
    assert "__FEATURE__" not in (feature / "user-auth-plan.md").read_text()
    again = subprocess.run(["scripts/new_feature.sh", "user-auth"], cwd=project)
    assert again.returncode != 0


def git(cwd: Path, *args: str) -> None:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.com",
    }
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        env=env,
    )


@pytest.mark.update
def test_copier_update_pulls_in_template_changes(tmp_path: Path) -> None:
    template = tmp_path / "template_repo"
    shutil.copytree(
        REPO,
        template,
        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".*_cache", "uv.lock"),
    )
    git(template, "init", "-q", "-b", "main")
    git(template, "add", "-A")
    git(template, "commit", "-q", "-m", "v1")
    git(template, "tag", "v0.1.0")

    project = tmp_path / "project"
    run_copy(
        str(template),
        project,
        data=answers("library_cli"),
        defaults=True,
        skip_tasks=True,
        quiet=True,
        vcs_ref="v0.1.0",
    )
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "scaffold")

    check_sh = template / "template/scripts/check.sh"
    check_sh.write_text(check_sh.read_text() + "# improved in v0.2.0\n")
    git(template, "commit", "-q", "-am", "v2")
    git(template, "tag", "v0.2.0")

    # `copier update` insists on trust for any template that declares tasks, even when skipped.
    run_update(project, defaults=True, overwrite=True, skip_tasks=True, unsafe=True, quiet=True)

    assert "# improved in v0.2.0" in (project / "scripts/check.sh").read_text()
    recorded = yaml.safe_load((project / ".copier-answers.yml").read_text())
    assert recorded["_commit"] == "v0.2.0"
    assert recorded["flavor"] == "library_cli"


@pytest.mark.gate
@pytest.mark.parametrize("flavor", FLAVORS)
def test_generated_project_passes_its_own_gate(
    flavor: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)  # let uv use the generated project's venv
    project = tmp_path / "project"
    # Runs the real post-generation tasks too: git init, uv sync, nbstripout (datascience).
    run_copy(str(REPO), project, data=answers(flavor), defaults=True, unsafe=True, quiet=True)

    result = subprocess.run(
        ["scripts/check.sh"], cwd=project, capture_output=True, text=True, check=False
    )

    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-3000:]
