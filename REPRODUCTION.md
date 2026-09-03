# Reproduction map

Every quantitative claim in the manuscript, mapped to the command that produces it, the file it
reads, and — critically — **what that command actually demonstrates**.

Read [`data/PROVENANCE.md`](data/PROVENANCE.md) first. The record-level evaluation files are
reconstructed from reported aggregates, so most rows below are marked *consistency check*: they
verify that the shipped tables, the manuscript and the test suite agree, not that the underlying
study result is correct.

## Status legend

| Marker | Meaning |
|---|---|
| **Re-derived** | The computation is performed from inputs, and a different input would give a different answer. Genuine verification of the procedure. |
| **Consistency check** | Recomputes a manuscript number from a file that was reconstructed to contain it. Confirms internal agreement only; circular as evidence. |
| **Descriptive** | A retained aggregate summary is printed. Nothing is computed; no inferential claim is attached in the manuscript either. |
| **Not in package** | Requires data that was not retained or is not distributed. |

## Manuscript tables

| Manuscript label | Content | Command | Reads | Status |
|---|---|---|---|---|
| `tab:grid_search` | Security hyperparameter grid search, 5 informative rows | `python -m experiments.grid_search` | `data/security_validation/security_validation_300.csv` | **Re-derived** — 30 configurations × 5-fold CV; w = (0.6, 0.2, 0.2), τ = 0.70 is selected by maximum CV F1, not asserted. Provenance of the input file is pending (see PROVENANCE) |
| `tab:grid_search_full` | Full 30-configuration appendix table | `python -m experiments.grid_search` | same | **Re-derived**; full grid written to `results/generated/grid_search_30_configs.csv` |
| `tab:hallucination_rates` | PHR / UDR per model, 16 models | `python -m experiments.rq1_prevalence` | `results/expected/prevalence_by_model.csv` | **Descriptive** — prints mean/SD/range of the retained per-model summary |
| `tab:mitigation_effectiveness` | DR, FPR, ARR, SCR | `python -m experiments.rq2_detection_repair` | `data/gold_standard/*.csv` | **Consistency check** |
| `tab:fn_taxonomy` | 9 `V_secure` false negatives, 3/3/3 | `python -m experiments.rq2_detection_repair` | `data/adversarial_benchmark/adversarial_benchmark_500.csv` | **Consistency check** |
| `tab:adversarial_results` | Adversarial precision / recall / F1 | `python -m experiments.rq2_detection_repair` | same | **Consistency check** |
| `tab:crossmodel_results` | Five generator–judge pairings | `python -m experiments.descriptive_summaries` | `results/expected/crossmodel_judge_summary.csv` | **Descriptive** — the manuscript itself claims no significance here; instance-level records were not retained |
| `tab:latency` | Per-stage latency | `python -m experiments.rq3_latency` | `results/expected/latency_by_stage.csv` | **Descriptive** |
| `tab:financial_overhead` | Cost per snippet / per 1,000 | `python -m experiments.descriptive_summaries` | `results/expected/cost_estimate.csv` | **Descriptive** — figures are stated lower bounds; they exclude judge calls, failed requests and retries |
| `tab:ablation` | ARR by configuration, paired *t*, Bonferroni, *d* | `python -m experiments.rq4_ablation` | `results/expected/ablation_per_model_arr.csv` | **Re-derived** — the *t*-statistics, α′ = 0.0167 and Cohen's *d* are computed from the 16 model-level observations |
| `tab:judge_pairs` | Cross-model pairings evaluated | — | — | Narrative; no computation |
| `tab:nlapi_distribution` | NL-API domain distribution | `python -m pytest tests/test_datasets.py::test_nl_api_size_and_domains` | `data/nl_api/nl_api_prompts.jsonl` | **Consistency check** — asserts 2,500 records and the 700/650/400/300/450 split |
| `tab:comparison_frameworks`, `tab:dataset_composition`, `tab:sampling_params`, `tab:evaluation_metrics`, `tab:llms_evaluated`, `tab:experimental_params`, `tab:adversarial_benchmark`, `tab:crossmodel_config` | Design and configuration tables | — | `halluguard/config.yaml` for the parameter values | Narrative; parameters are machine-readable in the config |

## Manuscript figures

| Figure | Command | Status |
|---|---|---|
| `fig:hallucination_rates` (fig8) | `python figures/plot_results.py` | Regenerated at 300 DPI → `results/generated/figures/prevalence_by_model.png` |
| `fig:latency_overhead` (fig7) | `python figures/plot_results.py` | Regenerated → `latency_by_stage.png` |
| `fig:ablation_study` (fig9) | `python figures/plot_results.py` | Regenerated → `ablation_arr.png` |
| `fig:architecture`, `fig:vexist_flow`, `fig:vsecure_pipeline`, `fig:vrelevant_flow`, `fig:mitigation_module`, `fig:slopsquatting_lifecycle`, `fig:nlapi_sequence`, `fig:annotation_protocol`, `fig:crossmodel_judge`, case studies 1–2 | — | Hand-authored diagrams; **not in package** as regenerable artifacts |

## Formal specifications, verifiable by reading

| Manuscript element | Implementation |
|---|---|
| Eq. `eq:composite_verification` — short-circuit chain | `halluguard/verifier.py::HalluGuardVerifier._first_failure` |
| `S_final` equation | `halluguard/security_score.py::combine` |
| `S_vuln` severity mapping (0.0 / 0.5 / 1.0) | `halluguard/security_score.py::_VULN_SCORE` |
| `S_rep` log-normalised reputation | `halluguard/security_score.py::reputation_score` |
| `S_typo` normalised Levenshtein | `halluguard/security_score.py::typosquat_similarity` |
| Alg. `alg:cov_process` (`VerifyAndMitigate`) | `halluguard/verifier.py::verify_and_mitigate` |
| Alg. `alg:security_score` | `halluguard/security_score.py::SecurityScorer.score` |
| Alg. `alg:scr_verification` | `experiments/verify_scr.py` |
| App. A — `V_relevant` prompt, verbatim | `halluguard/prompts/relevance_{system,user}.txt` |
| App. A — mitigation prompt, verbatim | `halluguard/prompts/mitigation_{system,user}.txt` |
| App. B — Bonferroni α′ = 0.05/3 | `experiments/rq4_ablation.py::ALPHA_ADJ` |
| App. B — Wilson intervals | `halluguard/stats.py::wilson_interval`, checked against a textbook value in `tests/test_stats.py` |
| App. E — annotation codebook v1.0 | `docs/annotation_codebook_v1.0.md` |

## Not reproducible from this package

| Claim | Reason |
|---|---|
| PHR/UDR over 573,696 snippets | Corpus not distributed; available on reasonable request. `--corpus-dir` re-runs the computation over a local corpus |
| Per-call temperature analysis | Schedules not retained; manuscript reports prevalence in aggregate only and claims no temperature effect |
| Cross-model judge significance | Instance-level paired records not retained; manuscript reports the 2.0 pp F1 difference descriptively and explicitly claims no significance |
| Study-time `V_secure` scores | The 2025-03-01 OSV snapshot is not distributed and the client queries OSV live — see `docs/DEVIATIONS.md` §2 |
| DR / FPR as independent evidence | Original annotation logs not retained — see `data/PROVENANCE.md` |

## One-command check

```bash
python -m pytest          # 25 offline tests: implementation behaviour + artifact self-consistency
```

This verifies that the distributed artifact is internally coherent. It is not evidence for the
empirical claims of the paper; see the legend above.
