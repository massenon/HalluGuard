# HalluGuard — Replication Package

[![CI](https://github.com/massenon/HalluGuard/actions/workflows/ci.yml/badge.svg)](https://github.com/massenon/HalluGuard/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10–3.12](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](pyproject.toml)

HalluGuard is a registry-aware Chain-of-Verification (CoV-RAG) middleware that validates
third-party package dependencies in LLM-generated Python code before installation. Each
extracted dependency passes through a short-circuiting chain:

1. **V_exist** — live existence check against the PyPI JSON API;
2. **V_secure** — composite security score from OSV advisory evidence, package reputation,
   and name-similarity (typosquatting) evidence. The study used a 2025-03-01 OSV snapshot; the
   released client queries OSV **live**, so live runs will not match study-time scores
   (see [`docs/DEVIATIONS.md`](docs/DEVIATIONS.md));
3. **V_relevant** — binary contextual-relevance judgement by a second LLM.

A failure at any stage triggers a structured correction prompt and regeneration
(at most `k = 3` attempts). Any unreachable data source yields an explicit
*indeterminate* verdict that is escalated rather than silently passed.

This package contains the framework source, the evaluation datasets, the experiment scripts, an
air-gapped execution sandbox, and a test suite.

> ### ⚠ Read `data/PROVENANCE.md` before citing any number from this package
>
> The original per-instance logs for the gold-standard, repair, execution and adversarial
> evaluations **were not retained**. The record-level files in `data/` were **reconstructed** so
> that their marginal counts reproduce the aggregates reported in the manuscript.
>
> Consequently, running the experiment scripts recovers 98.7% DR, 0.2% FPR, 92.4% ARR, 96.0% SCR
> and 98.6% adversarial F1 **by construction**. That is a consistency check on the distributed
> artifact, not an independent replication of the study. Nothing in `data/` should be cited as
> independent verification of those figures.
>
> What *is* independently verifiable here: the framework implementation, the scoring equation,
> the statistical routines, the hyperparameter selection *procedure*, the verbatim prompts and
> the sandbox. [`REPRODUCTION.md`](REPRODUCTION.md) states the status of every manuscript table
> and figure individually.

---

## Contents

```
halluguard/                 Framework source (Python >= 3.10)
  config.yaml               Model identifiers, weights, threshold, seeds (no credentials)
  config.py                 Typed, validated settings; credentials read from the environment
  http.py                   HTTP abstraction (timeouts, no retries, injectable for tests)
  extractor.py              AST-based import extraction and module -> package mapping
  registry_client.py        V_exist
  security_score.py         V_secure (S_final = max(0, 0.6·S_vuln + 0.2·S_rep − 0.2·S_typo))
  relevance_judge.py        V_relevant
  mitigation.py             Correction prompt construction and regeneration
  verifier.py               Chain-of-Verification loop
  stats.py                  Wilson intervals, Cohen's d, Cohen's kappa, t-based CIs
  prompts/                  Verbatim prompt templates (system + user, both stages)

data/
  nl_api/nl_api_prompts.jsonl                        2,500 prompts, 5 domains
  gold_standard/annotated_gold_standard_g800.csv     800 snippets: two annotators, adjudication, prediction
  gold_standard/repair_attempt_pool.csv              789 detected hallucinations -> repair outcome
  gold_standard/scr_execution_sample_400.csv         400 executed repairs -> pass/fail + failure category
  adversarial_benchmark/adversarial_benchmark_500.csv 500 packages (350 malicious, 150 benign)
  security_validation/security_validation_300.csv    300-package calibration set with sub-scores
  package_dictionary/                                module -> package map; popular-package reference list
  MANIFEST.md                                        Column-level schema of every file
  checksums.sha256                                   SHA-256 of every released data file

experiments/
  rq1_prevalence.py         Prevalence summary (offline) or recomputation from a corpus (network)
  rq2_detection_repair.py   DR, FPR, kappa, ARR, SCR, adversarial P/R/F1 and FN taxonomy
  rq3_latency.py            Latency summary (offline) or live V_exist timing (network)
  rq4_ablation.py           Paired t-tests, Bonferroni (α' = 0.05/3), Cohen's d
  grid_search.py            30-configuration, 5-fold CV selection of weights and τ_secure
  verify_scr.py             Execution runner used inside the sandbox

  descriptive_summaries.py  Cross-model judge and cost summaries (descriptive only)

results/expected/           Released per-model, per-stage, and per-configuration summaries
results/generated/          Written by the scripts (git-ignored)
database/                   Upstream benchmark inputs; NOT wired into the framework (see database/README.md)
docker/sandbox/             Air-gapped execution environment (network_mode: none)
figures/plot_results.py     Regenerates summary figures at 300 DPI
tests/                      25 offline tests (no network access required)

REPRODUCTION.md             Every manuscript table/figure -> command, input, and honest status
data/PROVENANCE.md          How each data file was produced -- READ FIRST
docs/DEVIATIONS.md          Where this implementation differs from the manuscript
docs/annotation_codebook_v1.0.md   The codebook named by the codebook_version column
docs/CHANGELOG-replication.md      What changed from the first public release
NOTICE                      Third-party attribution (EvalPlus, HumanEval, MBPP, CodeHaluEval)
```

---

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,figures]"
python -m pytest
```

Credentials are read from environment variables only (copy `.env.example` to `.env`;
`.env` is git-ignored). No experiment script that reproduces a reported number requires
credentials or network access.

---

## Recomputing the reported figures

Each command below recomputes a manuscript number from the shipped files. Read the status column
in [`REPRODUCTION.md`](REPRODUCTION.md) alongside it: the grid search and the ablation statistics
are genuine re-derivations, the prevalence, latency, cost and cross-model summaries are
descriptive prints, and the DR/FPR/ARR/SCR/adversarial figures are **consistency checks over
reconstructed inputs** rather than independent replication (`data/PROVENANCE.md`).

```bash
python -m experiments.rq2_detection_repair   # DR, FPR, kappa, ARR, SCR, adversarial F1
python -m experiments.rq4_ablation           # ablation with Bonferroni-corrected paired t-tests
python -m experiments.grid_search            # selects w = (0.6, 0.2, 0.2), tau = 0.70
python -m experiments.rq1_prevalence         # per-model PHR / UDR summary
python -m experiments.rq3_latency            # per-stage latency summary
python -m experiments.descriptive_summaries  # cross-model judge + cost summaries
python figures/plot_results.py               # figures -> results/generated/figures/
```

| Quantity | Source file | Recomputed value | Status |
|---|---|---|---|
| Detection Rate | `annotated_gold_standard_g800.csv` | 150 / 152 = 98.7% | consistency check |
| False Positive Rate | `annotated_gold_standard_g800.csv` | 1 / 648 = 0.2% | consistency check |
| Annotator disagreements | `annotated_gold_standard_g800.csv` | 30 / 800 = 3.8% | consistency check |
| Cohen's κ pre-adjudication | `annotated_gold_standard_g800.csv` | 0.88 | consistency check |
| Automated Repair Rate | `repair_attempt_pool.csv` | 729 / 789 = 92.4% (Wilson 90.3–94.0%) | consistency check |
| Semantic Correctness Rate | `scr_execution_sample_400.csv` | 384 / 400 = 96.0% (Wilson 93.6–97.5%) | consistency check |
| Adversarial precision / recall / F1 | `adversarial_benchmark_500.csv` | 99.7% / 97.4% / 98.6% (TP 341, FP 1, TN 149, FN 9) | consistency check |
| False-negative taxonomy | `adversarial_benchmark_500.csv` | 3 advisory lag, 3 reputation inflation, 3 below Levenshtein threshold | consistency check |
| PHR / UDR across 16 models | `prevalence_by_model.csv` | 7.2 ± 3.5% / 8.9 ± 4.5% | descriptive |
| Verification latency | `latency_by_stage.csv` | 285 ms mean, SD 42 ms | descriptive |

Two further quantities are genuine re-derivations rather than consistency checks:

| Quantity | Source file | Re-derived value | Status |
|---|---|---|---|
| Weights and threshold | `security_validation_300.csv` | w = (0.6, 0.2, 0.2), tau = 0.70 selected by max CV F1 = 0.921 | re-derived |
| Ablation statistics | `ablation_per_model_arr.csv` | paired t, alpha' = 0.0167, Cohen's d over N = 16 models | re-derived |

`tests/test_datasets.py` asserts each of the counts above. `python -m pytest` therefore verifies
that the distributed artifact is internally coherent -- the data files, the manuscript tables and
the test suite agree. Because the record-level inputs were reconstructed to contain those counts
(`data/PROVENANCE.md`), passing tests are **not** evidence for the empirical claims of the paper.

### Live / network-dependent runs (optional)

```bash
python -m experiments.rq3_latency --live 50            # times 50 real PyPI round-trips
python -m experiments.rq1_prevalence --corpus-dir DIR  # recomputes PHR from a local corpus
```

### Execution-based verification in the sandbox

```bash
cd docker/sandbox
docker compose build
docker compose run --rm sandbox
```

The container runs with `network_mode: none`, a read-only filesystem, dropped
capabilities, and an unprivileged user. Cases are supplied as JSONL
(`{"case_id", "code", "tests"}`) in `docker/sandbox/cases/`; a minimal example is included.

---

## Data availability

**Provenance first:** the record-level evaluation files are reconstructed from reported
aggregates, not raw experimental logs. [`data/PROVENANCE.md`](data/PROVENANCE.md) gives the
status of every file and states what this package does and does not evidence.

Files are shipped at the full N reported in the manuscript (800, 789, 400, 500, 2,500, 300).
Malicious package identifiers in `adversarial_benchmark_500.csv` are pseudonymised
(`cve-pkg-###`, `typo-pkg-###`, `slop-pkg-###`) so that the release does not propagate attack
names; the identifier mapping is available on reasonable request. The full 573,696-snippet prevalence
corpus will be available on reasonable request from the corresponding authors.

Per-call temperature settings for the prevalence corpus were not retained; prevalence
results are therefore reported in aggregate only. Repair and relevance-verification runs
use a fixed temperature of 0.2 (`halluguard/config.yaml`).

---

## Configuration reference

| Parameter | Value | Location |
|---|---|---|
| Generator model | `gpt-4-turbo-2024-04-09` | `config.yaml` |
| Relevance judge | `claude-3-5-sonnet-20240620` (must differ from generator) | `config.yaml` |
| Generation temperature (repair / judge) | 0.2 | `config.yaml` |
| Max regeneration attempts *k* | 3 | `config.yaml` |
| Weights (vuln, rep, typo) | 0.6, 0.2, 0.2 | `config.yaml`, selected by `grid_search.py` |
| τ_secure | 0.70 | `config.yaml` |
| OSV snapshot date | 2025-03-01 | `config.yaml` |
| Random seeds | 42, 137, 2024 | `config.yaml` |
| HTTP timeout | 5 s, no retries | `config.yaml` |

---

## Using the framework

```python
from halluguard import load_settings
from halluguard.http import RequestsClient
from halluguard.llm import make_completer
from halluguard.mitigation import MitigationModule
from halluguard.registry_client import RegistryClient
from halluguard.relevance_judge import RelevanceJudge
from halluguard.security_score import SecurityScorer
from halluguard.verifier import HalluGuardVerifier
import json

s = load_settings()
http = RequestsClient(s.http_timeout_s)
popular = json.load(open("data/package_dictionary/popular_pypi_reference.json"))
module_map = json.load(open("data/package_dictionary/module_to_package.json"))

generator = make_completer(s.generator_model, s.openai_api_key, s.anthropic_api_key)
judge_llm = make_completer(s.judge_model, s.openai_api_key, s.anthropic_api_key)

verifier = HalluGuardVerifier(
    generator=lambda p: generator.complete("Return only Python code.", p, s.generation_temperature, s.max_tokens),
    registry=RegistryClient(http, s.pypi_url),
    scorer=SecurityScorer(http, s.weights, s.tau_secure, s.osv_url, s.libraries_io_url,
                          popular, s.libraries_io_api_key),
    judge=RelevanceJudge(judge_llm, s.generation_temperature),
    mitigation=MitigationModule(generator, s.generation_temperature, s.max_tokens),
    module_to_package=module_map,
    max_attempts=s.max_regeneration_attempts,
)
outcome = verifier.verify_and_mitigate("Fetch a JSON document over HTTPS and print one field.")
print(outcome.outcome, outcome.attempts, outcome.rejections)
```

---

## Scope and limitations

* Python / PyPI only. Other ecosystems require a registry client and package dictionary.
* Package-level verification only; sub-module paths and function signatures are not checked.
* `V_secure` is bounded by the timeliness of the advisory snapshot and by reputation
  indicators that a determined adversary can inflate.
* Cross-model judge results are descriptive; instance-level paired records were not retained.

## License

MIT — see `LICENSE`.

## Contact

Corresponding authors (per the manuscript): Saurabh Agarwal (saurabh@yu.ac.kr) and
Wooguil Pak (wooguilpak@yu.ac.kr), Yeungnam University.
Replication package maintainer: Rhodes Massenon (rarhodes06@gmail.com).
