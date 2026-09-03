"""Shared I/O helpers for experiment scripts."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXPECTED = ROOT / "results" / "expected"
GENERATED = ROOT / "results" / "generated"


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: Iterable[dict], fieldnames: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def pct(x: float, digits: int = 1) -> str:
    return f"{x * 100:.{digits}f}%"
