"""V_exist: existence verification against the live PyPI JSON API."""

from __future__ import annotations

import time
from dataclasses import dataclass

from halluguard.extractor import Dependency
from halluguard.http import HttpClient


@dataclass(frozen=True)
class ExistenceResult:
    dependency: Dependency
    exists: bool | None      # None => indeterminate (transport failure)
    status_code: int | None
    latency_ms: float


class RegistryClient:
    def __init__(self, http: HttpClient, pypi_url: str) -> None:
        self._http = http
        self._pypi_url = pypi_url

    def verify_existence(self, dep: Dependency) -> ExistenceResult:
        url = self._pypi_url.format(package=dep.package_name)
        start = time.perf_counter()
        try:
            response = self._http.get(url)
        except ConnectionError:
            return ExistenceResult(dep, None, None, _elapsed_ms(start))
        exists = response.status_code == 200
        if response.status_code not in (200, 404):
            exists = None
        return ExistenceResult(dep, exists, response.status_code, _elapsed_ms(start))


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000.0, 1)
