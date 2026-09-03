"""V_secure: composite security score.

    S_final = max(0, w_vuln * S_vuln + w_rep * S_rep - w_typo * S_typo)
    V_secure(d) = True  iff  S_final >= tau_secure

Every sub-score may be *indeterminate* when its data source is unreachable.
An indeterminate sub-score never passes silently: the overall verdict is
``None`` and the caller must escalate to human review (fail-indeterminate).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

import Levenshtein

from halluguard.config import SecurityWeights
from halluguard.extractor import Dependency
from halluguard.http import HttpClient


class VulnSeverity(Enum):
    NONE = "none"
    HIGH = "high"
    CRITICAL = "critical"
    INDETERMINATE = "indeterminate"


_VULN_SCORE = {VulnSeverity.NONE: 1.0, VulnSeverity.HIGH: 0.5, VulnSeverity.CRITICAL: 0.0}


@dataclass(frozen=True)
class SecurityScoreResult:
    dependency: Dependency
    s_vuln: float | None
    s_rep: float | None
    s_typo: float
    s_final: float | None
    passed: bool | None              # None => indeterminate, escalate to review
    severity: VulnSeverity


def combine(weights: SecurityWeights, s_vuln: float, s_rep: float, s_typo: float) -> float:
    """Pure scoring function (Equation for S_final), clamped to [0, 1]."""
    raw = weights.vuln * s_vuln + weights.rep * s_rep - weights.typo * s_typo
    return round(min(1.0, max(0.0, raw)), 4)


def typosquat_similarity(name: str, reference_names: Sequence[str]) -> float:
    """Maximum normalised Levenshtein similarity to a *different* reference name."""
    best = 0.0
    for ref in reference_names:
        if ref == name:
            continue
        denom = max(len(name), len(ref))
        if denom == 0:
            continue
        best = max(best, 1.0 - Levenshtein.distance(name, ref) / denom)
    return round(best, 4)


def reputation_score(age_days: float, downloads: float,
                     age_median: float = 730.0, downloads_median: float = 50_000.0) -> float:
    """Log-normalised reputation in [0, 1] relative to ecosystem medians."""
    age_term = math.log1p(max(age_days, 0.0)) / math.log1p(age_median)
    dl_term = math.log1p(max(downloads, 0.0)) / math.log1p(downloads_median)
    return round(min(1.0, 0.5 * age_term + 0.5 * dl_term), 4)


class SecurityScorer:
    def __init__(self, http: HttpClient, weights: SecurityWeights, tau_secure: float,
                 osv_url: str, libraries_io_url: str, reference_names: Sequence[str],
                 libraries_io_api_key: str | None = None) -> None:
        self._http = http
        self._weights = weights
        self._tau = tau_secure
        self._osv_url = osv_url
        self._lib_url = libraries_io_url
        self._reference_names = tuple(reference_names)
        self._lib_key = libraries_io_api_key

    def query_severity(self, dep: Dependency) -> VulnSeverity:
        payload: dict = {"package": {"name": dep.package_name, "ecosystem": "PyPI"}}
        if dep.version_specifier:
            payload["version"] = dep.version_specifier
        try:
            response = self._http.post(self._osv_url, json=payload)
        except ConnectionError:
            return VulnSeverity.INDETERMINATE
        if response.status_code != 200 or not isinstance(response.payload, dict):
            return VulnSeverity.INDETERMINATE
        severities = {
            str(s.get("score", s)).upper() if isinstance(s, dict) else str(s).upper()
            for vuln in response.payload.get("vulns", [])
            for s in vuln.get("severity", [])
        }
        if any("CRITICAL" in s for s in severities):
            return VulnSeverity.CRITICAL
        if any("HIGH" in s for s in severities):
            return VulnSeverity.HIGH
        return VulnSeverity.NONE

    def query_reputation(self, dep: Dependency) -> float | None:
        params = {"api_key": self._lib_key} if self._lib_key else None
        try:
            response = self._http.get(self._lib_url.format(package=dep.package_name), params)
        except ConnectionError:
            return None
        if response.status_code != 200 or not isinstance(response.payload, dict):
            return None
        data = response.payload
        return reputation_score(
            float(data.get("age_days", 0) or 0),
            float(data.get("downloads", 0) or 0),
        )

    def score(self, dep: Dependency) -> SecurityScoreResult:
        severity = self.query_severity(dep)
        s_vuln = _VULN_SCORE.get(severity)
        s_rep = self.query_reputation(dep)
        s_typo = typosquat_similarity(dep.package_name, self._reference_names)

        if s_vuln is None or s_rep is None:
            return SecurityScoreResult(dep, s_vuln, s_rep, s_typo, None, None, severity)

        s_final = combine(self._weights, s_vuln, s_rep, s_typo)
        return SecurityScoreResult(dep, s_vuln, s_rep, s_typo, s_final,
                                   s_final >= self._tau, severity)
