#!/usr/bin/env bash
# Local quality gate: must pass before every commit (CI runs this same script).
# ruff (lint + format), mypy --strict, size limits, secret scan, pytest with the coverage
# floor from pyproject.toml. Run from anywhere; it cds to the repo root.
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n==> %s\n' "$1"; }

step "ruff check"
uv run ruff check src tests scripts

step "ruff format --check"
uv run ruff format --check src tests scripts

step "mypy --strict"
uv run mypy

step "size limits (files <= 800 lines, functions <= 50 lines)"
uv run python scripts/check_sizes.py

step "secret-material scan"
uv run python scripts/check_secrets.py

step "pytest (not live) with coverage floor"
uv run pytest --cov --cov-report=term-missing

printf '\nAll checks passed.\n'
