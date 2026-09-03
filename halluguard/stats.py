"""Statistical helpers shared by all experiment scripts (single implementation)."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy import stats as sps


def wilson_interval(successes: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion, returned as fractions."""
    if n <= 0:
        raise ValueError("n must be positive")
    z = sps.norm.ppf(1 - (1 - confidence) / 2)
    p = successes / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return centre - half, centre + half


@dataclass(frozen=True)
class ConfusionMatrix:
    tp: int
    fp: int
    tn: int
    fn: int

    @property
    def detection_rate(self) -> float:
        return self.tp / (self.tp + self.fn)

    @property
    def false_positive_rate(self) -> float:
        return self.fp / (self.fp + self.tn)

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp)

    @property
    def f1(self) -> float:
        p, r = self.precision, self.detection_rate
        return 2 * p * r / (p + r)


def cohens_d(a: Sequence[float], b: Sequence[float]) -> float:
    """Cohen's d with pooled standard deviation (independent-samples form)."""
    a_arr, b_arr = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    na, nb = len(a_arr), len(b_arr)
    pooled = math.sqrt(((na - 1) * a_arr.var(ddof=1) + (nb - 1) * b_arr.var(ddof=1)) / (na + nb - 2))
    return float((a_arr.mean() - b_arr.mean()) / pooled) if pooled > 0 else 0.0


def interpret_d(d: float) -> str:
    mag = abs(d)
    if mag < 0.2:
        return "negligible"
    if mag < 0.5:
        return "small"
    if mag < 0.8:
        return "medium"
    return "large"


def mean_ci_t(values: Sequence[float], confidence: float = 0.95) -> tuple[float, float, float]:
    """Mean and t-based CI of the mean (df = n - 1)."""
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    mean, sd = float(arr.mean()), float(arr.std(ddof=1))
    half = sps.t.ppf(1 - (1 - confidence) / 2, n - 1) * sd / math.sqrt(n)
    return mean, mean - half, mean + half


def cohens_kappa(labels_a: Sequence[str], labels_b: Sequence[str]) -> float:
    if len(labels_a) != len(labels_b) or not labels_a:
        raise ValueError("label sequences must be non-empty and equal length")
    categories = sorted(set(labels_a) | set(labels_b))
    n = len(labels_a)
    po = sum(a == b for a, b in zip(labels_a, labels_b)) / n
    pe = sum((sum(a == c for a in labels_a) / n) * (sum(b == c for b in labels_b) / n)
             for c in categories)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0
