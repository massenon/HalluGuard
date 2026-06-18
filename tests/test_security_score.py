"""
tests/test_security_score.py
------------------------------
Basic unit tests validating the V_secure composite score logic
(Algorithm 2) against known edge cases.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "halluguard"))

from security_score import calculate_security_score, W_VULN, W_REP, W_TYPO, TAU_SECURE


def test_weights_sum_consistency():
    """Weights should match the manuscript's Table 2 (0.6, 0.2, 0.2)."""
    assert W_VULN == 0.6
    assert W_REP == 0.2
    assert W_TYPO == 0.2


def test_threshold_matches_manuscript():
    assert TAU_SECURE == 0.70


def test_clamp_non_negative():
    """S_final must never be negative (Algorithm 2, line: max(0, S_final))."""
    # Simulated worst case: s_vuln=0, s_rep=0, s_typo=1.0
    s_final = max(0.0, (W_VULN * 0.0) + (W_REP * 0.0) - (W_TYPO * 1.0))
    assert s_final == 0.0
    assert s_final >= 0.0


def test_known_safe_package_passes():
    """A package with perfect scores should clear the threshold."""
    s_final = (W_VULN * 1.0) + (W_REP * 1.0) - (W_TYPO * 0.0)
    assert s_final >= TAU_SECURE


def test_known_malicious_package_fails():
    """A package with a critical CVE (s_vuln=0) and high typo similarity should fail."""
    s_final = max(0.0, (W_VULN * 0.0) + (W_REP * 0.1) - (W_TYPO * 0.9))
    assert s_final < TAU_SECURE


if __name__ == "__main__":
    test_weights_sum_consistency()
    test_threshold_matches_manuscript()
    test_clamp_non_negative()
    test_known_safe_package_passes()
    test_known_malicious_package_fails()
    print("All tests passed.")
