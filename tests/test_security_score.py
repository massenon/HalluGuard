from halluguard.config import SecurityWeights
from halluguard.extractor import Dependency
from halluguard.http import HttpResponse
from halluguard.security_score import (
    SecurityScorer,
    VulnSeverity,
    combine,
    reputation_score,
    typosquat_similarity,
)

W = SecurityWeights(0.6, 0.2, 0.2)


def make_scorer(http):
    return SecurityScorer(http, W, 0.70, "https://osv.example/query",
                          "https://lib.example/{package}", ["requests", "numpy"])


def test_combine_is_clamped_and_weighted():
    assert combine(W, 1.0, 1.0, 0.0) == 0.8
    assert combine(W, 0.0, 0.0, 1.0) == 0.0


def test_typosquat_ignores_exact_match():
    assert typosquat_similarity("requests", ["requests", "numpy"]) < 0.5
    assert typosquat_similarity("requesrs", ["requests"]) > 0.7


def test_reputation_bounded():
    assert 0.0 <= reputation_score(0, 0) <= reputation_score(5000, 1e9) <= 1.0


def test_clean_popular_package_passes(fake_http):
    http = fake_http({"osv.example": HttpResponse(200, {"vulns": []}),
                      "lib.example": HttpResponse(200, {"age_days": 3000, "downloads": 5_000_000})})
    res = make_scorer(http).score(Dependency("requests"))
    assert res.severity is VulnSeverity.NONE and res.passed is True


def test_critical_cve_fails(fake_http):
    http = fake_http({"osv.example": HttpResponse(200, {"vulns": [{"severity": [{"score": "CRITICAL"}]}]}),
                      "lib.example": HttpResponse(200, {"age_days": 3000, "downloads": 5_000_000})})
    res = make_scorer(http).score(Dependency("requests"))
    assert res.severity is VulnSeverity.CRITICAL and res.passed is False


def test_network_failure_is_indeterminate_not_pass(fake_http):
    http = fake_http({"lib.example": HttpResponse(200, {"age_days": 10, "downloads": 10})})
    res = make_scorer(http).score(Dependency("requests"))
    assert res.severity is VulnSeverity.INDETERMINATE and res.passed is None
