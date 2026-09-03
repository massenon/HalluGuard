# Data provenance — read before using any file in `data/`

This document states, per file, **how the shipped records were produced**. It exists because
several files in this directory are *not* raw experimental logs, and using them as if they were
would lead to false conclusions about what this package demonstrates.

## Summary

The original per-instance experimental logs for the gold-standard, repair, execution and
adversarial evaluations **were not retained**. What survived the study were the aggregate
summaries reported in the manuscript (counts, rates, sub-score distributions).

The four record-level evaluation files below were therefore **reconstructed**: row-level records
were generated so that their marginal counts reproduce the aggregates already reported in the
manuscript. They are faithful to the reported totals and to the documented column schema. They
are **not** the original annotation, repair, execution or benchmark logs.

### What this means in practice

* Running `python -m experiments.rq2_detection_repair` recomputes 98.7% DR, 0.2% FPR,
  92.4% ARR, 96.0% SCR and 98.6% adversarial F1 from these files. **This is a consistency check,
  not an independent replication.** The files were built from those numbers, so recovering them
  is circular by construction and confirms only that the shipped tables, the manuscript tables
  and the test suite agree with one another.
* `python -m pytest` likewise verifies internal consistency of the distributed artifact. It is
  not evidence for the empirical claims of the paper.
* No file in this directory should be cited as independent verification of the reported
  Detection Rate, False Positive Rate, Automated Repair Rate, Semantic Correctness Rate, or
  adversarial precision/recall/F1.

### What *can* be independently checked in this package

* The framework implementation in `halluguard/` — the verification chain, its short-circuit and
  fail-indeterminate semantics, and the exact prompt templates.
* `halluguard/security_score.combine()` — the scoring equation, verifiable against the manuscript.
* `halluguard/stats.py` — the Wilson, Cohen's *d*, Cohen's κ and *t*-interval implementations,
  checkable against textbook values (`tests/test_stats.py` does exactly this).
* `experiments/grid_search.py` — the selection *procedure* is fully re-executable; the weight
  triple (0.6, 0.2, 0.2) and τ = 0.70 are re-derived, not asserted. Its input file's status is
  noted below.
* `docker/sandbox/` — the execution environment, reproducible from the Dockerfile.

## Per-file status

| File | Status | Basis |
|---|---|---|
| `gold_standard/annotated_gold_standard_g800.csv` | **Reconstructed** | Rows generated to reproduce the reported N = 800, 152 positives, DR 98.7%, FPR 0.2% and pre-adjudication Cohen's κ = 0.88 (which fixes the adjudicated count at 30) |
| `gold_standard/repair_attempt_pool.csv` | **Reconstructed** | Rows generated to reproduce ARR = 729/789 |
| `gold_standard/scr_execution_sample_400.csv` | **Reconstructed** | Rows generated to reproduce SCR = 384/400 and the 7/6/3 failure taxonomy |
| `adversarial_benchmark/adversarial_benchmark_500.csv` | **Reconstructed** | Rows generated to reproduce TP/FP/TN/FN = 341/1/149/9 and the 3/3/3 false-negative taxonomy; malicious identifiers are pseudonyms (`cve-pkg-###`, `typo-pkg-###`, `slop-pkg-###`), benign identifiers are real PyPI names |
| `security_validation/security_validation_300.csv` | **Status pending** | See "Pending confirmation" below |
| `nl_api/nl_api_prompts.jsonl` | **Status pending** | See "Pending confirmation" below |
| `package_dictionary/module_to_package.json` | Partial | 17 mappings. The manuscript describes a ~20,000-entry dictionary built from PyPI metadata; that dictionary is not distributed |
| `package_dictionary/popular_pypi_reference.json` | Partial | 159 names. The manuscript describes a top-5,000 reference list; that list is not distributed |
| `../results/expected/*.csv` | Retained aggregate summaries | Configuration- and model-level summaries that survived the study, as described in the manuscript |

### Pending confirmation

Two files carry an as-yet unconfirmed status. Until this section is updated, treat them as
**possibly reconstructed** and do not rely on them as raw evidence.

1. `security_validation/security_validation_300.csv` — the input to `grid_search.py`. The
   selection *procedure* is genuinely re-executable either way, and it does select
   w = (0.6, 0.2, 0.2), τ = 0.70 as the unique argmax of cross-validated F1 (0.921) over the
   30-configuration grid. What is unconfirmed is whether the sub-scores in this file are the
   ones measured during the original calibration.
2. `nl_api/nl_api_prompts.jsonl` — whether these 2,500 prompts are the items actually harvested
   from GitHub Issues and Stack Overflow, or exemplars written to the documented domain
   distribution (700 langchain / 650 boto3 / 400 stripe / 300 kubernetes / 450 other).

This section will be replaced with a definitive statement for each file.

## Not distributed

* The 573,696-snippet prevalence corpus (HumanEval+/MBPP generations across 16 models) —
  available from the corresponding authors on reasonable request.
* The pseudonym → real package-name mapping for the adversarial benchmark — withheld so the
  release does not propagate attack names; available on reasonable request.
* The 2025-03-01 OSV advisory snapshot used at study time. See `docs/DEVIATIONS.md`: the
  released client queries OSV **live**, so security sub-scores computed today will not match
  study-time values.
* Per-call temperature schedules for the prevalence corpus (not retained).
* Instance-level records for the cross-model judge comparison (not retained; that table is
  descriptive only).

## Integrity

`sha256sum -c data/checksums.sha256` verifies that the files you have are byte-identical to the
released ones. It says nothing about their provenance — that is what this document is for.
