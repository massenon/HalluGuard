import math

import pytest

from halluguard.stats import ConfusionMatrix, cohens_d, cohens_kappa, interpret_d, wilson_interval


def test_wilson_matches_known_value():
    lo, hi = wilson_interval(384, 400)
    assert (round(lo, 3), round(hi, 3)) == (0.936, 0.975)


def test_wilson_rejects_zero_n():
    with pytest.raises(ValueError):
        wilson_interval(0, 0)


def test_confusion_matrix_metrics():
    cm = ConfusionMatrix(tp=341, fp=1, tn=149, fn=9)
    assert round(cm.precision, 3) == 0.997
    assert round(cm.detection_rate, 3) == 0.974
    assert round(cm.f1, 3) == 0.986
    assert math.isclose(cm.false_positive_rate, 1 / 150)


def test_cohens_d_and_interpretation():
    assert cohens_d([1, 2, 3], [1, 2, 3]) == 0.0
    assert interpret_d(0.41) == "small"
    assert interpret_d(1.12) == "large"


def test_kappa_perfect_and_chance():
    assert cohens_kappa(["a", "b", "a"], ["a", "b", "a"]) == 1.0
    assert abs(cohens_kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"])) < 1e-9
