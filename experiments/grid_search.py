"""
grid_search.py
-----------------
Reproduces the security hyperparameter grid search (Section 3.4.2.4,
Appendix C, Table 3) that derives the optimal weights and threshold
tau_secure = 0.70 by maximising F1 on a 300-package validation set.

Usage:
    python experiments/grid_search.py --validation-set data/security_validation_300.json
"""

import argparse
import csv
import itertools
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("grid_search")


def evaluate_configuration(w_vuln: float, w_rep: float, w_typo: float,
                            tau: float, validation_set: list[dict]) -> dict:
    """
    validation_set: list of {"package": str, "s_vuln": float, "s_rep": float,
                              "s_typo": float, "label": "benign"|"malicious"}
    Pre-computed component scores are expected (see data/README.md for the
    300-package validation set schema).
    """
    tp = fp = tn = fn = 0
    for entry in validation_set:
        s_final = max(0.0, w_vuln * entry["s_vuln"] + w_rep * entry["s_rep"]
                      - w_typo * entry["s_typo"])
        predicted_safe = s_final >= tau
        actual_safe = entry["label"] == "benign"

        if not actual_safe and not predicted_safe:
            tp += 1   # correctly flagged malicious
        elif actual_safe and not predicted_safe:
            fp += 1   # benign incorrectly flagged
        elif actual_safe and predicted_safe:
            tn += 1
        else:
            fn += 1   # malicious missed

    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)
    fpr = fp / max(fp + tn, 1)

    return {
        "w_vuln": w_vuln, "w_rep": w_rep, "w_typo": w_typo, "tau_secure": tau,
        "precision": round(precision, 3), "recall": round(recall, 3),
        "f1": round(f1, 3), "fpr": round(fpr, 3),
    }


def run_grid_search(validation_set: list[dict]) -> list[dict]:
    weight_combos = [
        (0.5, 0.25, 0.25), (0.6, 0.20, 0.20), (0.7, 0.15, 0.15),
        (0.6, 0.20, 0.20), (0.5, 0.30, 0.20),
    ]
    taus = [0.60, 0.70, 0.80]

    all_results = []
    for (w_vuln, w_rep, w_typo) in weight_combos:
        for tau in taus:
            result = evaluate_configuration(w_vuln, w_rep, w_typo, tau, validation_set)
            all_results.append(result)

    best = max(all_results, key=lambda r: r["f1"])
    for r in all_results:
        r["selected"] = (r == best)

    logger.info("Optimal configuration: w_vuln=%.2f, w_rep=%.2f, w_typo=%.2f, "
                "tau=%.2f -> F1=%.3f", best["w_vuln"], best["w_rep"],
                best["w_typo"], best["tau_secure"], best["f1"])
    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reproduce security score grid search.")
    parser.add_argument("--validation-set", type=Path,
                         default=Path("data/security_validation_300.json"))
    parser.add_argument("--output", type=Path,
                         default=Path("results/raw/grid_search_results.csv"))
    args = parser.parse_args()

    if args.validation_set.exists():
        validation_set = json.loads(args.validation_set.read_text())
    else:
        logger.warning("Validation set not found at %s; using empty placeholder.",
                        args.validation_set)
        validation_set = []

    results = run_grid_search(validation_set)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
