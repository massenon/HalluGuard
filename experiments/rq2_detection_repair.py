"""
rq2_detection_repair.py
-------------------------
Replicates RQ2: "How effectively can the HalluGuard framework detect
and repair these hallucinations?"

Computes Detection Rate (DR), Automated Repair Rate (ARR), Semantic
Correctness Rate (SCR), and False Positive Rate (FPR) against the
human-annotated gold standard (data/annotated_gold_standard.csv),
NOT against the automated 576k corpus alone — this resolves the
circular ground-truth concern raised by Review_Paper1 (Major
Comment #1).

Usage:
    python experiments/rq2_detection_repair.py --gold data/annotated_gold_standard.csv
"""

import argparse
import csv
import logging
import sys
from pathlib import Path

import numpy as np
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rq2")


def wilson_ci(successes: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """95% Wilson confidence interval for a proportion."""
    if n == 0:
        return (0.0, 0.0)
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p_hat = successes / n
    denom = 1 + z**2 / n
    centre = p_hat + z**2 / (2 * n)
    margin = z * np.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n)
    return ((centre - margin) / denom, (centre + margin) / denom)


def load_gold_standard(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def compute_metrics(gold_rows: list[dict]) -> dict:
    """
    Expects gold_rows with columns:
      snippet_id, final_label (hallucination/no_hallucination),
      halluguard_prediction (flagged/not_flagged), repaired_correctly (yes/no/na)
    """
    tp = fp = tn = fn = 0
    repaired_total = repaired_success = 0

    for row in gold_rows:
        actual = row["final_label"] == "hallucination"
        predicted = row["halluguard_prediction"] == "flagged"

        if actual and predicted:
            tp += 1
            repaired_total += 1
            if row.get("repaired_correctly") == "yes":
                repaired_success += 1
        elif actual and not predicted:
            fn += 1
        elif not actual and predicted:
            fp += 1
        else:
            tn += 1

    dr = tp / max(tp + fn, 1)
    fpr = fp / max(fp + tn, 1)
    arr = repaired_success / max(repaired_total, 1)

    dr_ci = wilson_ci(tp, tp + fn)
    fpr_ci = wilson_ci(fp, fp + tn)
    arr_ci = wilson_ci(repaired_success, repaired_total)

    return {
        "n_gold_standard": len(gold_rows),
        "detection_rate_pct": round(dr * 100, 1),
        "detection_rate_ci": tuple(round(x * 100, 1) for x in dr_ci),
        "false_positive_rate_pct": round(fpr * 100, 2),
        "false_positive_rate_ci": tuple(round(x * 100, 2) for x in fpr_ci),
        "automated_repair_rate_pct": round(arr * 100, 1),
        "automated_repair_rate_ci": tuple(round(x * 100, 1) for x in arr_ci),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
    }


def compute_scr_from_sandbox(sandbox_results_path: Path) -> dict:
    """
    Reads execution-based SCR results from the Docker sandbox
    (see docker/sandbox/ and experiments/verify_scr.py).
    Expects a CSV with columns: snippet_id, unit_tests_passed (bool).
    """
    if not sandbox_results_path.exists():
        logger.warning("Sandbox results not found at %s; run docker/sandbox first.",
                        sandbox_results_path)
        return {"scr_pct": None, "scr_ci": None}

    with open(sandbox_results_path, newline="") as f:
        rows = list(csv.DictReader(f))
    n = len(rows)
    passed = sum(1 for r in rows if r["unit_tests_passed"].lower() == "true")
    scr = passed / max(n, 1)
    ci = wilson_ci(passed, n)
    return {
        "n_sandbox_sample": n,
        "scr_pct": round(scr * 100, 1),
        "scr_ci": tuple(round(x * 100, 1) for x in ci),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replicate RQ2 detection/repair metrics.")
    parser.add_argument("--gold", type=Path, default=Path("data/annotated_gold_standard.csv"))
    parser.add_argument("--sandbox-results", type=Path,
                         default=Path("results/raw/scr_sandbox_results.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/raw/rq2_metrics.csv"))
    args = parser.parse_args()

    gold_rows = load_gold_standard(args.gold)
    metrics = compute_metrics(gold_rows)
    scr_metrics = compute_scr_from_sandbox(args.sandbox_results)
    metrics.update(scr_metrics)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics.keys()))
        writer.writeheader()
        writer.writerow(metrics)

    logger.info("RQ2 metrics: %s", metrics)
