# Data

This directory holds the evaluation data, the calibration inputs and the reference dictionaries
used by the framework. `MANIFEST.md` gives the column-level schema for every file; this document
describes what each file is and where it came from.

## What can be checked directly

Four results in this package are computed from their inputs rather than reported, so a different
input gives a different answer:

| Result | Command | Input |
|---|---|---|
| Weights and threshold, w = (0.6, 0.2, 0.2) and τ = 0.70 | `python -m experiments.grid_search` | `security_validation/security_validation_300.csv` |
| Ablation statistics: paired *t*, Bonferroni α′ = 0.0167, Cohen's *d* | `python -m experiments.rq4_ablation` | `../results/expected/ablation_per_model_arr.csv` |
| Wilson, Cohen's *d*, Cohen's κ and *t* interval implementations | `python -m pytest tests/test_stats.py` | textbook reference values |
| Chain semantics: short-circuit order and fail-indeterminate behaviour | `python -m pytest tests/test_verifier.py` | scripted HTTP doubles |

The grid search is the substantive one. It runs on the study's own calibration measurements: the
300 packages in `security_validation_300.csv` carry the `S_vuln`, `S_rep` and `S_typo` values
recorded during calibration, with their stratum and label. The script evaluates all thirty
configurations under 5-fold cross-validation with a seeded fold assignment and selects by maximum
mean F1. The published configuration is the unique maximum at F1 = 0.921. Selecting the
hyperparameters is therefore a full re-derivation on the original data rather than a restatement:
change the input file and the selected configuration changes with it.

## Evaluation records

| File | N | Contents |
|---|---|---|
| `gold_standard/annotated_gold_standard_g800.csv` | 800 | Two independent annotator labels, adjudication flag, adjudicator label, final label, framework prediction |
| `gold_standard/repair_attempt_pool.csv` | 789 | Reason code, attempts used, repair outcome |
| `gold_standard/scr_execution_sample_400.csv` | 400 | Execution outcome and failure category |
| `adversarial_benchmark/adversarial_benchmark_500.csv` | 500 | Category, true label, the three sub-scores, prediction, false-negative category |

These four files are derived from the study's retained aggregate summaries rather than from
original per-instance logs, and are distributed so that the published counts, rates and
taxonomies can be inspected and recomputed at row level.

Malicious package identifiers in the adversarial benchmark are pseudonymised (`cve-pkg-###`,
`typo-pkg-###`, `slop-pkg-###`) so that publication does not propagate attack names. Benign
identifiers are real PyPI names. The mapping is available from the authors on request, as is the
full prevalence corpus.

## Calibration and reference inputs

| File | N | Contents |
|---|---|---|
| `security_validation/security_validation_300.csv` | 300 | The calibration set used in the study, stratified as benign, malicious and ambiguous (100 each), carrying the `S_vuln`, `S_rep` and `S_typo` values measured for each package. Input to the grid search |
| `nl_api/nl_api_prompts.jsonl` | 2,500 | Evaluation instances drawn from 251 distinct natural-language requests, domain-annotated across five ecosystems, each requiring at least three third-party imports. Instance counts describe generation volume; the 251 distinct requests bound the diversity of developer intents probed |
| `package_dictionary/module_to_package.json` | 17 | Import name to PyPI distribution name, for names where the two differ |
| `package_dictionary/popular_pypi_reference.json` | 159 | Reference names for the Levenshtein similarity check |

The two package dictionaries are reduced working sets rather than the full study-time lists.
Because `S_typo` is a maximum over the reference list, a live run against the shorter list yields
lower similarity scores than the evaluated configuration.

## Aggregate summaries

`../results/expected/` holds the configuration-level and model-level summaries retained from the
study: per-model prevalence, per-stage latency, per-configuration ablation, cross-model judge
results and cost estimates. The analysis scripts read these directly.

## Integrity

```bash
sha256sum -c data/checksums.sha256
```

Fifteen files, verified on every commit by the continuous-integration workflow.
