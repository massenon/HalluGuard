# Reproduction

Every quantitative claim in the manuscript, mapped to the command that produces it and the file
it reads. Sections are ordered by how much each command establishes, strongest first.

```bash
pip install -e ".[dev,figures]"    # Python 3.10 to 3.12
python -m pytest                   # 25 offline tests, no network, no credentials
sha256sum -c data/checksums.sha256 # 15 released data files
```

Continuous integration runs both on every commit across Python 3.10, 3.11 and 3.12, and executes
every analysis script below.

## Re-derived from inputs

These four compute their results rather than restating them. Change the input and the answer
changes. The first runs on the calibration measurements recorded during the study, so the
published weights and threshold are re-derived from the original data rather than reported.

| Manuscript element | Command | Result |
|---|---|---|
| `tab:grid_search`, `tab:grid_search_full` | `python -m experiments.grid_search` | Runs on the study's own calibration measurements and selects w = (0.6, 0.2, 0.2), τ = 0.70 as the unique maximum of cross-validated F1 (0.921) over all thirty configurations, under a seeded 5-fold assignment |
| `tab:ablation` | `python -m experiments.rq4_ablation` | Paired *t* statistics, Bonferroni α′ = 0.05/3, and Cohen's *d* computed over the 16 model-level observations |
| App. B, Wilson and *t* intervals | `python -m pytest tests/test_stats.py` | Wilson, Cohen's *d*, Cohen's κ and *t* interval implementations checked against known values |
| Eq. `eq:composite_verification`, Alg. `alg:cov_process` | `python -m pytest tests/test_verifier.py` | Short-circuit order, four terminal outcomes, and the fail-indeterminate rule that an unreachable data source never resolves to a pass |

## Computed from released records

| Manuscript element | Command | Reads |
|---|---|---|
| `tab:mitigation_effectiveness` (DR, FPR, ARR, SCR) | `python -m experiments.rq2_detection_repair` | `data/gold_standard/*.csv` |
| `tab:adversarial_results`, `tab:fn_taxonomy` | `python -m experiments.rq2_detection_repair` | `data/adversarial_benchmark/adversarial_benchmark_500.csv` |
| `tab:nlapi_distribution` | `python -m pytest tests/test_datasets.py` | `data/nl_api/nl_api_prompts.jsonl` |

ARR (729/789) and SCR (384/400) carry Wilson intervals computed from their integer counts. DR and
FPR are reported as point estimates, consistent with Section 5.3 of the manuscript.

## Printed from retained summaries

| Manuscript element | Command | Reads |
|---|---|---|
| `tab:hallucination_rates` | `python -m experiments.rq1_prevalence` | `results/expected/prevalence_by_model.csv` |
| `tab:latency` | `python -m experiments.rq3_latency` | `results/expected/latency_by_stage.csv` |
| `tab:crossmodel_results`, `tab:financial_overhead` | `python -m experiments.descriptive_summaries` | `results/expected/crossmodel_judge_summary.csv`, `cost_estimate.csv` |

The cross-model judge comparison is descriptive by design, as the manuscript states: instance-level
paired records are not part of the retained summary, so no significance is claimed. Cost figures
are generator-side lower bounds that exclude judge calls, failed requests and retries.

## Figures

| Figure | Command |
|---|---|
| `fig:latency_overhead` (7), `fig:hallucination_rates` (8), `fig:ablation_study` (9), `fig:crossmodel_judge` (12) | `python figures/plot_results.py` |
| `fig:annotation_protocol`, `fig:casestudy1` (10), `fig:casestudy2` (11), `fig:nlapi_sequence` | `python figures/plot_diagrams.py` |

Both scripts write at 300 DPI to `results/generated/figures/`, to `figures/`, and to the
manuscript's own `figures/` directory. Two of them read their counts from the data at draw time:
the annotation-protocol figure takes its conflict count and κ from
`annotated_gold_standard_g800.csv`, and the NL-API sequence takes its instance and distinct-request
counts from `nl_api_prompts.jsonl`, so neither can drift from the corpus. The architecture and
stage-flow diagrams (Figures 1 to 6) are authored by hand.

## Specifications verifiable by reading

| Manuscript element | Implementation |
|---|---|
| `S_final` equation | `halluguard/security_score.py::combine` |
| `S_vuln` severity mapping | `halluguard/security_score.py::_VULN_SCORE` |
| `S_rep` log-normalised reputation | `halluguard/security_score.py::reputation_score` |
| `S_typo` normalised Levenshtein | `halluguard/security_score.py::typosquat_similarity` |
| Alg. `alg:cov_process` | `halluguard/verifier.py::verify_and_mitigate` |
| Alg. `alg:security_score` | `halluguard/security_score.py::SecurityScorer.score` |
| Alg. `alg:scr_verification` | `experiments/verify_scr.py` |
| App. A prompt templates, verbatim | `halluguard/prompts/*.txt` |
| App. E annotation codebook | `docs/annotation_codebook_v1.0.md` |

## Available on request

The full 573,696-snippet prevalence corpus and the pseudonym mapping for the adversarial benchmark
are available from the corresponding authors. See `data/PROVENANCE.md`.
