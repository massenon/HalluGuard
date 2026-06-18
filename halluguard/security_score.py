"""
security_score.py
------------------
Implements V_secure: the composite security posture verification
described in Section 3.4.2 and formalised in Algorithm 2
(CalculateSecurityScore).

S_final = (w_vuln * S_vuln) + (w_rep * S_rep) - (w_typo * S_typo)
V_secure(d_i) = True  iff  S_final >= tau_secure
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional

import requests
import Levenshtein

logger = logging.getLogger("halluguard.security_score")

# Optimal weights and threshold derived via grid search (Appendix C)
W_VULN = 0.6
W_REP = 0.2
W_TYPO = 0.2
TAU_SECURE = 0.70

OSV_API = "https://api.osv.dev/v1/query"
LIBRARIES_IO_API = "https://libraries.io/api/{ecosystem}/{package}"


@dataclass
class SecurityScoreResult:
    package_name: str
    s_vuln: float
    s_rep: float
    s_typo: float
    s_final: float
    passed: bool
    severity_detail: Optional[str] = None


def query_vulnerability_db(package_name: str, version: Optional[str],
                            api_key: Optional[str] = None) -> tuple[float, str]:
    """
    S_vuln component. Queries the OSV database (and optionally the
    GitHub Advisory Database). Returns 0 for critical CVEs, 0.5 for
    high-severity, 1 otherwise (Section 3.4.2).
    """
    payload = {"package": {"name": package_name, "ecosystem": "PyPI"}}
    if version:
        payload["version"] = version
    try:
        resp = requests.post(OSV_API, json=payload, timeout=5.0)
        resp.raise_for_status()
        vulns = resp.json().get("vulns", [])
        if not vulns:
            return 1.0, "no_known_vulnerabilities"
        severities = [v.get("severity", []) for v in vulns]
        flat = [s for sub in severities for s in sub]
        if any("CRITICAL" in str(s) for s in flat):
            return 0.0, "critical_cve_found"
        if any("HIGH" in str(s) for s in flat):
            return 0.5, "high_severity_cve_found"
        return 1.0, "low_or_unrated_only"
    except requests.RequestException as exc:
        logger.warning("OSV query failed for %s: %s", package_name, exc)
        return 1.0, "query_failed_defaulted_safe"  # documented limitation


def analyze_reputation(package_name: str, ecosystem: str = "pypi",
                        api_key: Optional[str] = None) -> float:
    """
    S_rep component. Queries libraries.io for project age and download
    velocity, log-normalised to [0,1] relative to ecosystem benchmarks.
    """
    try:
        url = LIBRARIES_IO_API.format(ecosystem=ecosystem, package=package_name)
        resp = requests.get(url, params={"api_key": api_key}, timeout=5.0)
        resp.raise_for_status()
        data = resp.json()
        # Simplified log-normalisation; full implementation in paper Sec 3.4.2
        import math
        age_days = data.get("latest_release_published_at_days", 0)
        downloads = data.get("rank", 0)
        age_score = min(1.0, math.log1p(age_days) / math.log1p(3650))
        rank_score = min(1.0, downloads / 1000.0) if downloads else 0.0
        return round(0.5 * age_score + 0.5 * rank_score, 3)
    except requests.RequestException as exc:
        logger.warning("libraries.io query failed for %s: %s", package_name, exc)
        return 0.3  # conservative default for unknown packages


def detect_typosquatting(package_name: str, popular_packages: list[str]) -> float:
    """
    S_typo component. Computes the maximum normalised Levenshtein
    similarity between `package_name` and the curated top-5,000 list
    of popular packages (Equation: Lev_norm in Section 3.4.2).
    """
    best = 0.0
    for ref in popular_packages:
        if ref == package_name:
            continue  # exact match handled by V_exist, not typosquat detection
        dist = Levenshtein.distance(package_name, ref)
        norm_sim = 1 - (dist / max(len(package_name), len(ref)))
        best = max(best, norm_sim)
    return round(best, 3)


def calculate_security_score(package_name: str, version: Optional[str],
                              popular_packages: list[str],
                              api_key: Optional[str] = None) -> SecurityScoreResult:
    """
    Algorithm 2: CalculateSecurityScore — full composite computation.
    """
    s_vuln, severity_detail = query_vulnerability_db(package_name, version, api_key)
    s_rep = analyze_reputation(package_name, api_key=api_key)
    s_typo = detect_typosquatting(package_name, popular_packages)

    s_final = (W_VULN * s_vuln) + (W_REP * s_rep) - (W_TYPO * s_typo)
    s_final = max(0.0, s_final)  # clamp non-negative

    return SecurityScoreResult(
        package_name=package_name,
        s_vuln=s_vuln, s_rep=s_rep, s_typo=s_typo,
        s_final=round(s_final, 3),
        passed=s_final >= TAU_SECURE,
        severity_detail=severity_detail,
    )


if __name__ == "__main__":
    result = calculate_security_score("requests", "2.31.0", popular_packages=["requests", "numpy"])
    print(result)
