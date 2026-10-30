"""Fail when tracked, staged, or untracked-but-not-ignored files contain key material.

Detects PEM blocks and cloud service-account key JSON. Run from the repo root:

    uv run python scripts/check_secrets.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Built from pieces so this file does not match itself.
PATTERNS = {
    "PEM block": re.compile("-----" + "BEGIN"),
    "service-account key JSON": re.compile(r'"type"\s*:\s*"service' + '_account"'),
}
# Markdown may *describe* the markers (plans, runbooks); only real key material fails there.
PROSE_PATTERNS = {
    "PEM private key": re.compile("-----" + r"BEGIN [A-Z ]*PRIVATE KEY-----"),
    "service-account key JSON": re.compile(r'"private_key"\s*:\s*"-----'),
}
SKIP = {Path("scripts/check_secrets.py")}
MAX_BYTES = 5 * 1024 * 1024


def candidate_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        check=True,
        capture_output=True,
    ).stdout.decode()
    return [Path(p) for p in out.split("\0") if p]


def scan(path: Path) -> list[str]:
    if path in SKIP or not path.is_file() or path.stat().st_size > MAX_BYTES:
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    patterns = PROSE_PATTERNS if path.suffix.lower() == ".md" else PATTERNS
    return [f"{path}: contains {label}" for label, rx in patterns.items() if rx.search(text)]


def main() -> int:
    findings = [msg for path in candidate_files() for msg in scan(path)]
    for msg in findings:
        print(f"error: {msg}", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
