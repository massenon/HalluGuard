"""Verbatim prompt templates loaded from the adjacent text files."""

from pathlib import Path

_DIR = Path(__file__).parent


def load(name: str) -> str:
    return (_DIR / f"{name}.txt").read_text(encoding="utf-8")


RELEVANCE_SYSTEM = load("relevance_system")
RELEVANCE_USER = load("relevance_user")
MITIGATION_SYSTEM = load("mitigation_system")
MITIGATION_USER = load("mitigation_user")
