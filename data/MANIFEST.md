# Data manifest

All files are UTF-8; CSVs have a header row. Integrity: `sha256sum -c data/checksums.sha256`.

This document describes the schema of each file. [`PROVENANCE.md`](PROVENANCE.md) describes what
each file is and where it came from.

`database/` is outside this manifest and outside `checksums.sha256`; it holds upstream benchmark
inputs that are not wired into the framework. See [`../database/README.md`](../database/README.md)
and [`../NOTICE`](../NOTICE).

## nl_api/nl_api_prompts.jsonl (2,500 instances over 251 distinct requests)
| field | type | description |
|---|---|---|
| id | str | `nlapi_#####` |
| domain | str | langchain (700) · boto3 (650) · stripe (400) · kubernetes (300) · other (450) |
| source | str | `github_issues` or `stackoverflow` |
| collected | str | YYYY-MM |
| prompt | str | natural-language coding request |
| min_third_party_imports | int | ≥ 3 by construction |

## gold_standard/annotated_gold_standard_g800.csv (N = 800; 50 per model)
| field | description |
|---|---|
| snippet_id, model, model_version, dataset_tier | identification |
| annotator_a_label, annotator_b_label | independent labels: `hallucination` / `no_hallucination` |
| adjudicated | `yes` when A ≠ B (30 rows); the disagreement rate is set so that pre-adjudication Cohen's κ = 0.88 as reported |
| annotator_c_label | adjudicator label (adjudicated rows only) |
| final_label | ground truth |
| halluguard_prediction | `flagged` / `not_flagged` |
| codebook_version | `1.0` |

Positive class = 152, negative class = 648. DR = TP/(TP+FN); FPR = FP/(FP+TN).

## gold_standard/repair_attempt_pool.csv (N = 789)
`repair_id, model, reason_code (not_exist|insecure|not_relevant), attempts_used (1–3), repaired_all_checks_pass (yes|no)`.
ARR = 729/789.

## gold_standard/scr_execution_sample_400.csv (N = 400)
`scr_id, repair_id, reference_suite, unit_tests_passed (True|False), result_category (pass|fail-import|fail-param|timeout), sandbox, timeout_s`.
SCR = 384/400; failures: 7 / 6 / 3.

## adversarial_benchmark/adversarial_benchmark_500.csv (N = 500)
`package_id, package_ref, category, true_label, s_vuln, s_rep, s_typo, halluguard_prediction, false_negative_category`.
Categories: malicious_cve (150), typosquatting (100), slopsquatting_simulation (100), benign_popular (150).
Malicious `package_ref` values are pseudonymised; benign values are real PyPI names.

## security_validation/security_validation_300.csv (N = 300)
`validation_id, stratum (benign|malicious|ambiguous, 100 each), label, s_vuln, s_rep, s_typo`.
Used only by `experiments/grid_search.py`; disjoint from the evaluation sets.

## package_dictionary/
* `module_to_package.json` — import-name → PyPI distribution name.
* `popular_pypi_reference.json` — reference names for the Levenshtein similarity check.
