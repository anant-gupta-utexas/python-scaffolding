"""Enforce the AGENTS.md size limits on ``src/``: files <= 800 lines, functions <= 50 lines.

Files over 400 lines are reported as warnings. Run from the repo root:

    uv run python scripts/check_sizes.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

FILE_WARN = 400
FILE_MAX = 800
FUNC_MAX = 50
ROOT = Path("src")


def function_lengths(tree: ast.AST) -> list[tuple[str, int, int]]:
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            length = (node.end_lineno or node.lineno) - node.lineno + 1
            found.append((node.name, node.lineno, length))
    return found


def check_file(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    source = path.read_text(encoding="utf-8")
    lines = source.count("\n") + 1
    if lines > FILE_MAX:
        errors.append(f"{path}: {lines} lines (max {FILE_MAX})")
    elif lines > FILE_WARN:
        warnings.append(f"{path}: {lines} lines (target < {FILE_WARN})")
    for name, lineno, length in function_lengths(ast.parse(source)):
        if length > FUNC_MAX:
            errors.append(f"{path}:{lineno}: function {name} is {length} lines (max {FUNC_MAX})")
    return errors, warnings


def main() -> int:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.py")):
        file_errors, file_warnings = check_file(path)
        errors += file_errors
        for warning in file_warnings:
            print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
