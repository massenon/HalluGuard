"""Self-consistency guards for the released data files.

These assertions check that the shipped record-level files still contain the counts
reported in the manuscript, so that an accidental edit to a CSV is caught immediately.

They are NOT evidence for those counts. The files were reconstructed from the reported
aggregates (see data/PROVENANCE.md), so recovering the aggregates from them is circular
by construction. Read REPRODUCTION.md for what each number does and does not demonstrate.
"""

import csv
import json
from pathlib import Path

from halluguard.stats import ConfusionMatrix, cohens_kappa

DATA = Path(__file__).resolve().parents[1] / "data"


def rows(rel):
    with open(DATA / rel, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def cm(rs, label_key, positive, pred_key):
    tp = sum(r[label_key] == positive and r[pred_key] == "flagged" for r in rs)
    fn = sum(r[label_key] == positive and r[pred_key] != "flagged" for r in rs)
    fp = sum(r[label_key] != positive and r[pred_key] == "flagged" for r in rs)
    tn = sum(r[label_key] != positive and r[pred_key] != "flagged" for r in rs)
    return ConfusionMatrix(tp, fp, tn, fn)


def test_nl_api_size_and_domains():
    lines = (DATA / "nl_api/nl_api_prompts.jsonl").read_text().splitlines()
    recs = [json.loads(line) for line in lines]
    assert len(recs) == 2500
    counts = {d: sum(r["domain"] == d for r in recs) for d in ("langchain", "boto3", "stripe", "kubernetes", "other")}
    assert counts == {"langchain": 700, "boto3": 650, "stripe": 400, "kubernetes": 300, "other": 450}
    assert all(r["min_third_party_imports"] >= 3 for r in recs)


def test_g800_detection_and_fpr():
    g = rows("gold_standard/annotated_gold_standard_g800.csv")
    assert len(g) == 800
    c = cm(g, "final_label", "hallucination", "halluguard_prediction")
    assert round(c.detection_rate * 100, 1) == 98.7
    assert round(c.false_positive_rate * 100, 1) == 0.2
    assert sum(r["adjudicated"] == "yes" for r in g) == 30
    # kappa is a published headline value; guard it so a data edit cannot silently
    # drift the annotator columns away from it again.
    kappa = cohens_kappa([r["annotator_a_label"] for r in g], [r["annotator_b_label"] for r in g])
    assert round(kappa, 2) == 0.88, kappa


def test_repair_pool_arr():
    p = rows("gold_standard/repair_attempt_pool.csv")
    assert len(p) == 789
    assert sum(r["repaired_all_checks_pass"] == "yes" for r in p) == 729


def test_scr_sample():
    s = rows("gold_standard/scr_execution_sample_400.csv")
    assert len(s) == 400
    assert sum(r["unit_tests_passed"] == "True" for r in s) == 384
    cats = {c: sum(r["result_category"] == c for r in s) for c in ("fail-import", "fail-param", "timeout")}
    assert cats == {"fail-import": 7, "fail-param": 6, "timeout": 3}


def test_adversarial_benchmark():
    a = rows("adversarial_benchmark/adversarial_benchmark_500.csv")
    assert len(a) == 500
    c = cm(a, "true_label", "malicious", "halluguard_prediction")
    assert (c.tp, c.fp, c.tn, c.fn) == (341, 1, 149, 9)
    assert round(c.f1 * 100, 1) == 98.6
    fn_cats = [r["false_negative_category"] for r in a if r["false_negative_category"]]
    assert sorted(fn_cats) == sorted(["osv_database_lag"] * 3 + ["reputation_inflation"] * 3 + ["below_levenshtein_threshold"] * 3)


def test_security_validation_size():
    v = rows("security_validation/security_validation_300.csv")
    assert len(v) == 300
    assert all(v_["stratum"] in {"benign", "malicious", "ambiguous"} for v_ in v)
