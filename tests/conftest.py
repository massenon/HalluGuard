"""Offline HTTP doubles so no test touches the network."""

from __future__ import annotations

import pytest

from halluguard.http import HttpResponse


class FakeHttp:
    """Scripted responses keyed by URL substring; unknown URLs raise ConnectionError."""

    def __init__(self, routes: dict[str, HttpResponse]) -> None:
        self.routes = routes
        self.calls: list[str] = []

    def _find(self, url: str) -> HttpResponse:
        self.calls.append(url)
        for key, resp in self.routes.items():
            if key in url:
                return resp
        raise ConnectionError(f"no route for {url}")

    def get(self, url, params=None):
        return self._find(url)

    def post(self, url, json):
        return self._find(url)


@pytest.fixture
def fake_http():
    return FakeHttp
