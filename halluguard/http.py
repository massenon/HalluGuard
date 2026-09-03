"""Minimal HTTP abstraction so that verification stages can be tested offline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import requests


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    payload: Any | None


class HttpClient(Protocol):
    def get(self, url: str, params: dict[str, str] | None = None) -> HttpResponse: ...
    def post(self, url: str, json: dict[str, Any]) -> HttpResponse: ...


class RequestsClient:
    """Production client backed by ``requests`` with a hard timeout and no retries.

    Any transport-level failure raises ``ConnectionError`` so that callers can
    map it to an explicit *indeterminate* outcome instead of a silent pass.
    """

    def __init__(self, timeout_s: float) -> None:
        self._timeout = timeout_s
        self._session = requests.Session()

    def _wrap(self, response: requests.Response) -> HttpResponse:
        try:
            payload = response.json() if response.content else None
        except ValueError:
            payload = None
        return HttpResponse(response.status_code, payload)

    def get(self, url: str, params: dict[str, str] | None = None) -> HttpResponse:
        try:
            return self._wrap(self._session.get(url, params=params, timeout=self._timeout))
        except requests.RequestException as exc:
            raise ConnectionError(str(exc)) from exc

    def post(self, url: str, json: dict[str, Any]) -> HttpResponse:
        try:
            return self._wrap(self._session.post(url, json=json, timeout=self._timeout))
        except requests.RequestException as exc:
            raise ConnectionError(str(exc)) from exc
