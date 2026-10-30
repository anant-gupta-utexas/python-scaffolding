"""Project directories. Data lives under ``data/`` (gitignored) and is created on demand."""

from __future__ import annotations

from pathlib import Path

# src/<package>/paths.py -> repository root (valid for a source checkout / editable install).
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
STAGES = ("raw", "interim", "processed")


def data_path(stage: str, *parts: str, create: bool = False) -> Path:
    """Return ``data/<stage>/<parts...>``; with ``create=True`` the stage directory is made."""
    if stage not in STAGES:
        raise ValueError(f"unknown data stage {stage!r}; expected one of {STAGES}")
    stage_dir = DATA_DIR / stage
    if create:
        stage_dir.mkdir(parents=True, exist_ok=True)
    return stage_dir.joinpath(*parts)
