"""Security-score hyperparameter selection: 30 configurations, 5-fold CV.

Configurations: 6 weight triples x 5 thresholds. Folds are a deterministic
shuffle of data/security_validation/security_validation_300.csv (seed 42).
The selection criterion is maximum cross-validated F1.
"""

from __future__ import annotations

import argparse
import random
import statistics

from experiments.common import DATA, GENERATED, read_csv, write_csv
from halluguard.config import SecurityWeights
from halluguard.security_score import combine
from halluguard.stats import ConfusionMatrix

WEIGHT_TRIPLES = [(0.50, 0.25, 0.25), (0.55, 0.25, 0.20), (0.60, 0.20, 0.20),
                  (0.65, 0.20, 0.15), (0.70, 0.15, 0.15), (0.60, 0.25, 0.15)]
THRESHOLDS = [0.55, 0.60, 0.65, 0.70, 0.75]


def evaluate(rows: list[dict], weights: SecurityWeights, tau: float) -> ConfusionMatrix:
    tp = fp = tn = fn = 0
    for r in rows:
        safe = combine(weights, float(r["s_vuln"]), float(r["s_rep"]), float(r["s_typo"])) >= tau
        benign = r["label"] == "benign"
        if benign and safe:
            tn += 1
        elif benign:
            fp += 1
        elif not safe:
            tp += 1
        else:
            fn += 1
    return ConfusionMatrix(tp, fp, tn, fn)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rows = read_csv(DATA / "security_validation/security_validation_300.csv")
    random.Random(args.seed).shuffle(rows)
    size = len(rows) // args.folds
    folds = [rows[i * size:(i + 1) * size] for i in range(args.folds)]

    out = []
    for wv, wr, wt in WEIGHT_TRIPLES:
        weights = SecurityWeights(wv, wr, wt)
        for tau in THRESHOLDS:
            cms = [evaluate(fold, weights, tau) for fold in folds]
            out.append({"w_vuln": wv, "w_rep": wr, "w_typo": wt, "tau": tau,
                        "cv_precision": round(statistics.mean(c.precision for c in cms), 3),
                        "cv_recall": round(statistics.mean(c.detection_rate for c in cms), 3),
                        "cv_f1": round(statistics.mean(c.f1 for c in cms), 3),
                        "cv_fpr": round(statistics.mean(c.false_positive_rate for c in cms), 3),
                        "selected": ""})
    best = max(out, key=lambda r: r["cv_f1"])
    best["selected"] = "yes"
    print(f"selected: w=({best['w_vuln']},{best['w_rep']},{best['w_typo']}) tau={best['tau']} "
          f"cv_f1={best['cv_f1']} cv_fpr={best['cv_fpr']}")
    write_csv(GENERATED / "grid_search_30_configs.csv", out, list(out[0].keys()))


if __name__ == "__main__":
    main()
