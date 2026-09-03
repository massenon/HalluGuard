"""RQ2 — detection, repair, semantic correctness, and adversarial security metrics.

Recomputes every RQ2 metric from the released record-level files:
  data/gold_standard/annotated_gold_standard_g800.csv   -> DR, FPR, kappa
  data/gold_standard/repair_attempt_pool.csv            -> ARR
  data/gold_standard/scr_execution_sample_400.csv       -> SCR + failure taxonomy
  data/adversarial_benchmark/adversarial_benchmark_500.csv -> precision, recall, F1, FN taxonomy
"""

from __future__ import annotations

from collections import Counter

from experiments.common import DATA, GENERATED, pct, read_csv, write_csv
from halluguard.stats import ConfusionMatrix, cohens_kappa, wilson_interval


def confusion(rows: list[dict], label_key: str, positive: str, pred_key: str) -> ConfusionMatrix:
    tp = fp = tn = fn = 0
    for r in rows:
        actual, flagged = r[label_key] == positive, r[pred_key] == "flagged"
        if actual and flagged:
            tp += 1
        elif actual:
            fn += 1
        elif flagged:
            fp += 1
        else:
            tn += 1
    return ConfusionMatrix(tp, fp, tn, fn)


def main() -> None:
    results: list[dict] = []

    g800 = read_csv(DATA / "gold_standard/annotated_gold_standard_g800.csv")
    cm = confusion(g800, "final_label", "hallucination", "halluguard_prediction")
    dr_ci = wilson_interval(cm.tp, cm.tp + cm.fn)
    fpr_ci = wilson_interval(cm.fp, cm.fp + cm.tn)
    kappa = cohens_kappa([r["annotator_a_label"] for r in g800], [r["annotator_b_label"] for r in g800])
    disagreements = sum(r["adjudicated"] == "yes" for r in g800)
    results += [
        {"metric": "DR", "count": f"{cm.tp}/{cm.tp + cm.fn}", "value": pct(cm.detection_rate),
         "ci_low": pct(dr_ci[0]), "ci_high": pct(dr_ci[1])},
        {"metric": "FPR", "count": f"{cm.fp}/{cm.fp + cm.tn}", "value": pct(cm.false_positive_rate),
         "ci_low": pct(fpr_ci[0]), "ci_high": pct(fpr_ci[1])},
        {"metric": "annotator_disagreements", "count": f"{disagreements}/{len(g800)}",
         "value": pct(disagreements / len(g800)), "ci_low": "", "ci_high": ""},
        {"metric": "cohens_kappa_pre_adjudication", "count": "", "value": f"{kappa:.3f}", "ci_low": "", "ci_high": ""},
    ]

    pool = read_csv(DATA / "gold_standard/repair_attempt_pool.csv")
    repaired = sum(r["repaired_all_checks_pass"] == "yes" for r in pool)
    arr_ci = wilson_interval(repaired, len(pool))
    results.append({"metric": "ARR", "count": f"{repaired}/{len(pool)}", "value": pct(repaired / len(pool)),
                    "ci_low": pct(arr_ci[0]), "ci_high": pct(arr_ci[1])})

    scr = read_csv(DATA / "gold_standard/scr_execution_sample_400.csv")
    passed = sum(r["unit_tests_passed"] == "True" for r in scr)
    scr_ci = wilson_interval(passed, len(scr))
    results.append({"metric": "SCR", "count": f"{passed}/{len(scr)}", "value": pct(passed / len(scr)),
                    "ci_low": pct(scr_ci[0]), "ci_high": pct(scr_ci[1])})
    for cat, n in sorted(Counter(r["result_category"] for r in scr if r["result_category"] != "pass").items()):
        results.append({"metric": f"SCR_failure:{cat}", "count": str(n), "value": "", "ci_low": "", "ci_high": ""})

    adv = read_csv(DATA / "adversarial_benchmark/adversarial_benchmark_500.csv")
    acm = confusion(adv, "true_label", "malicious", "halluguard_prediction")
    results += [
        {"metric": "adversarial_TP/FP/TN/FN", "count": f"{acm.tp}/{acm.fp}/{acm.tn}/{acm.fn}", "value": "", "ci_low": "", "ci_high": ""},
        {"metric": "adversarial_precision", "count": "", "value": pct(acm.precision), "ci_low": "", "ci_high": ""},
        {"metric": "adversarial_recall", "count": "", "value": pct(acm.detection_rate), "ci_low": "", "ci_high": ""},
        {"metric": "adversarial_F1", "count": "", "value": pct(acm.f1), "ci_low": "", "ci_high": ""},
    ]
    for cat, n in sorted(Counter(r["false_negative_category"] for r in adv if r["false_negative_category"]).items()):
        results.append({"metric": f"adversarial_FN:{cat}", "count": str(n), "value": "", "ci_low": "", "ci_high": ""})

    for r in results:
        print(f"{r['metric']:<40} {r['count']:<14} {r['value']:<8} {r['ci_low']:<8} {r['ci_high']}")
    write_csv(GENERATED / "rq2_metrics.csv", results, ["metric", "count", "value", "ci_low", "ci_high"])


if __name__ == "__main__":
    main()
