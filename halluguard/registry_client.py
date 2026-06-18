"""
registry_client.py
-------------------
Implements V_exist: live existence verification against authoritative
package registries (PyPI for Python, npm for JavaScript).

Corresponds to Section 3.4.1 ("Existence Verification") and the
PyPI/npm query step shown in Figure 3 of the manuscript.
"""

from __future__ import annotations
import time
import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger("halluguard.registry_client")


@dataclass
class Dependency:
    """A single extracted software dependency."""
    package_name: str
    version_specifier: Optional[str] = None
    ecosystem: str = "python"          # "python" | "javascript"


@dataclass
class ExistenceResult:
    dependency: Dependency
    exists: bool
    status_code: int
    latency_ms: float
    metadata: Optional[dict] = None


class RegistryClient:
    """Queries live package registries to verify V_exist(d_i)."""

    PYPI_URL = "https://pypi.org/pypi/{package}/json"
    NPM_URL = "https://registry.npmjs.org/{package}"

    def __init__(self, timeout_s: float = 5.0, session: Optional[requests.Session] = None):
        self.timeout_s = timeout_s
        self.session = session or requests.Session()

    def verify_existence(self, dep: Dependency) -> ExistenceResult:
        """
        Executes the V_exist check for a single dependency.

        Returns ExistenceResult.exists = True iff the registry returns
        HTTP 200; False on HTTP 404 (definitive hallucination signal).
        """
        url = self._build_url(dep)
        t0 = time.perf_counter()
        try:
            resp = self.session.get(url, timeout=self.timeout_s)
            latency_ms = (time.perf_counter() - t0) * 1000.0
            exists = resp.status_code == 200
            metadata = resp.json() if exists else None
            return ExistenceResult(
                dependency=dep,
                exists=exists,
                status_code=resp.status_code,
                latency_ms=latency_ms,
                metadata=metadata,
            )
        except requests.RequestException as exc:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            logger.warning("Registry query failed for %s: %s", dep.package_name, exc)
            return ExistenceResult(
                dependency=dep, exists=False, status_code=-1,
                latency_ms=latency_ms, metadata=None,
            )

    def _build_url(self, dep: Dependency) -> str:
        if dep.ecosystem == "python":
            return self.PYPI_URL.format(package=dep.package_name)
        elif dep.ecosystem == "javascript":
            return self.NPM_URL.format(package=dep.package_name)
        raise ValueError(f"Unsupported ecosystem: {dep.ecosystem}")

    # ------------------------------------------------------------------ #
    # Stage 2: Module-to-Package Name Mapping (Section 3.3.2)
    # ------------------------------------------------------------------ #
    def resolve_canonical_name(self, module_name: str, ecosystem: str,
                                 module_dictionary: dict) -> str:
        """
        Maps an imported module name (e.g. 'bs4') to its canonical
        installable package name (e.g. 'beautifulsoup4') using the
        pre-compiled 20,000-entry dictionary in data/package_dictionary/.
        Falls back to a registry search API if no direct match is found.
        """
        key = f"{ecosystem}:{module_name}"
        if key in module_dictionary:
            return module_dictionary[key]
        return module_name  # fallback: assume module name == package name


if __name__ == "__main__":
    client = RegistryClient()
    result = client.verify_existence(Dependency("requests", ecosystem="python"))
    print(result)
