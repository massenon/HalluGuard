"""Dependency extraction from Python source using the standard-library AST.

Only top-level, third-party module roots are returned; standard-library
modules and relative imports are excluded.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass

_STDLIB = set(sys.stdlib_module_names)


@dataclass(frozen=True)
class Dependency:
    package_name: str
    version_specifier: str | None = None


def extract_module_roots(source: str) -> list[str]:
    """Return sorted, de-duplicated top-level module names imported by ``source``.

    Raises ``SyntaxError`` if the snippet cannot be parsed.
    """
    tree = ast.parse(source)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return sorted(r for r in roots if r not in _STDLIB)


def resolve_dependencies(source: str, module_to_package: dict[str, str]) -> list[Dependency]:
    """Map imported module roots to canonical PyPI package names."""
    return [Dependency(module_to_package.get(m, m)) for m in extract_module_roots(source)]
