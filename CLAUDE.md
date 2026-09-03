# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Two artifacts for one paper — *"Vibe Coding at Risk: A CoV-RAG Framework for Mitigating
Slopsquatting Attacks in AI-Generated Code"* (Massenon, Gambo, Okegbile, Agarwal, Pak):

1. **The replication package** — `halluguard/` (framework), `data/` (record-level evaluation
   files), `experiments/` (recompute every reported metric), `results/expected/`, `tests/`,
   `docker/sandbox/`, `figures/`.
2. **The manuscript source** — `Vibe_Coding_at_Risk__.../revised_manuscript_v4.tex` (1,669 lines)
   plus `reference.bib` and `figures/`. The `.zip` at the repo root is the same bundle; the
   root `Revised_...pdf` is the 41-page pdfTeX compile of that `.tex`. Edit the `.tex`; the
   zip and PDF are outputs.

Not a git repository. There is no CI.

## Commands

```bash
python -m venv .venv && source .venv/bin/activate   # PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev,figures]"

python -m pytest                                    # 25 offline tests; the integrity check
python -m pytest tests/test_datasets.py -q          # one file
python -m pytest tests/test_verifier.py::test_nonexistent_package_is_repaired
ruff check .                                        # line-length 100, target py310

python -m experiments.rq1_prevalence                # per-model PHR/UDR summary
python -m experiments.rq2_detection_repair          # DR, FPR, kappa, ARR, SCR, adversarial P/R/F1
python -m experiments.rq3_latency                   # per-stage latency summary
python -m experiments.rq4_ablation                  # paired t-tests, Bonferroni, Cohen's d
python -m experiments.grid_search                   # selects w=(0.6,0.2,0.2), tau=0.70
python figures/plot_results.py                      # 300 DPI PNGs -> results/generated/figures/

sha256sum -c data/checksums.sha256                  # all 14 files currently verify OK
```

Network-dependent (optional, never needed to reproduce a reported number):
`python -m experiments.rq3_latency --live 50`, `python -m experiments.rq1_prevalence --corpus-dir DIR`.

Sandbox: `cd docker/sandbox && docker compose build && docker compose run --rm sandbox`
(build context is the repo root; runs `network_mode: none`, read-only FS, all caps dropped).

**Environment caveat:** dependencies are hard-pinned (`numpy==1.26.4`, `scipy==1.13.1`) and only
resolve on Python 3.10–3.12; the paper environment is 3.11.9. The machine this repo sits on has
Python 3.14 with none of the dependencies installed, so `pytest` and the experiment scripts will
not run until a 3.11/3.12 venv exists.

## Framework architecture

`HalluGuardVerifier.verify_and_mitigate(prompt)` (`halluguard/verifier.py`) is the whole system:
generate → extract dependencies → run the short-circuiting chain → on failure, build a structured
correction prompt and regenerate, up to `k = 3` attempts.

The chain is `V_exist` → `V_secure` → `V_relevant`, evaluated per dependency, stopping at the
first failure (`_first_failure`). Four terminal outcomes: `VERIFIED`, `FAILED` (attempts
exhausted), `INDETERMINATE`, `UNPARSEABLE`.

Invariants that the design turns on — preserve them in any change:

* **Tri-state, fail-indeterminate.** Every stage returns `True` / `False` / `None`, and `None`
  (unreachable PyPI, unreachable OSV or libraries.io, unparseable judge output) escalates to
  `Outcome.INDETERMINATE` rather than passing. `RequestsClient` converts every
  `requests.RequestException` into `ConnectionError` specifically so callers can map it to `None`;
  `SecurityScorer.score` returns `passed=None` whenever `s_vuln` or `s_rep` is missing. A change
  that lets a missing data source resolve to "pass" is a security regression, and
  `test_network_failure_is_indeterminate_not_pass` guards it.
* **Everything external is injected.** `HttpClient` and `Completer` are `Protocol`s
  (`http.py`, `llm.py`); `tests/conftest.py` supplies a `FakeHttp` whose unknown URLs raise
  `ConnectionError`. No test touches the network — keep it that way.
* **Scoring is a pure function.** `security_score.combine()` implements
  `S_final = clamp(0.6·S_vuln + 0.2·S_rep − 0.2·S_typo)` and is shared by the runtime scorer and
  by `experiments/grid_search.py`, which is what makes the grid search a real re-derivation of
  the shipped weights rather than a restatement.
* **Judge ≠ generator.** `Settings.__post_init__` raises if `judge_model == generator_model`;
  cross-model decoupling is an architectural claim of the paper, not a preference.
* **`halluguard/stats.py` is the single statistics implementation.** Wilson intervals,
  `ConfusionMatrix`, Cohen's d, Cohen's kappa, t-based CIs. Experiment scripts import from it;
  don't inline a second copy.
* **Prompts live in `halluguard/prompts/*.txt`**, loaded verbatim at import. The same four
  templates are reproduced in the README and in manuscript Appendix A
  (`revised_manuscript_v4.tex`, `\section{Verbatim Prompt Templates}`, ~line 1478). Editing one
  means editing all three.

Credentials come only from the environment (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`,
`LIBRARIES_IO_API_KEY`); `config.yaml` holds no secrets.

## The numbers contract

**The record-level files in `data/` are reconstructed from reported aggregates, not raw
experimental logs** — the original per-instance annotation, repair, execution and adversarial
records were not retained. `data/PROVENANCE.md` states this per file and is the document to
point any reader at. The practical consequence: recomputing 98.7% DR from
`annotated_gold_standard_g800.csv` is circular, and `pytest` is an artifact self-consistency
check, not evidence. Never describe a script's output as independent replication, and never
reintroduce that framing into the README.

Subject to that, the files are the operative source of truth for every headline figure, and
three places restate them: `tests/test_datasets.py` (hard-coded counts), the README
reproduction table, and the manuscript's results tables. They currently agree exactly —
G800 gives TP/FN/FP/TN = 150/2/1/647 (DR 98.7%, FPR 0.2%), ARR 729/789, SCR 384/400,
adversarial 341/1/149/9 (F1 98.6%), `ablation_per_model_arr.csv` means 0.0 / 75.40 / 89.10 / 92.50
across 16 models, PHR mean 7.2%.

So touching any file under `data/` or `results/expected/` means updating, in the same change:
the assertion in `tests/test_datasets.py`, the README table, `data/MANIFEST.md` (column-level
schema), `data/checksums.sha256`, and the corresponding manuscript table.

## Paper ↔ code divergences

Real, and worth knowing before "fixing" either side:

* **Dependency extraction.** The paper (§4.3) specifies the `tree-sitter` incremental parser and
  a module→package dictionary built from the top 20,000 PyPI packages with a registry-search
  fallback. `halluguard/extractor.py` uses the stdlib `ast` module, and
  `data/package_dictionary/module_to_package.json` holds 17 entries with a fall-through to the
  module name itself.
* **Typosquat reference list.** `config.yaml` sets `typosquat_list_size: 5000` and the paper says
  "top 5,000 PyPI packages"; `popular_pypi_reference.json` ships 159 names. The config key is
  never read by any code — nor are `osv_snapshot_date` or `seeds`; all three are loaded into
  `Settings` for documentation only.
* **Manuscript internal inconsistency.** The abstract states "the source code and study datasets
  are not publicly released", §5.5 gives a public GitHub URL, and §5.3 says the G800
  confusion-matrix cells "were not preserved" — while `annotated_gold_standard_g800.csv` ships
  per-row predictions from which those cells recompute exactly. If asked to reconcile the paper
  with the package, this is the substantive issue, not a typo.
* **Stale paths in the manuscript.** It cites `data/gold_standard/g800/` and
  `experiments/rq2/rq2_detection_repair.py`; the real paths are
  `data/gold_standard/annotated_gold_standard_g800.csv` and `experiments/rq2_detection_repair.py`.

## Unwired directories

* `database/` — HumanEval/MBPP loaders vendored from EvalPlus (`humaneval.py`, `mbpp.py` import
  `evalplus`, which is not in `pyproject.toml`) plus ~68 MB of benchmark JSON
  (`data_compliance_hallucination.json`, `external_source_hallucination.json`,
  `sanitized-mbpp.json`, `HumanEval.jsonl.gz`). Nothing in `halluguard/`, `experiments/`, or
  `tests/` references it, and it is absent from the README, `data/MANIFEST.md`, and
  `checksums.sha256`. Treat it as a staging area for the prevalence corpus, not as wired code.
* `scripts/` — empty.
* `results/generated/` — git-ignored output; scripts create it.

## Editing the manuscript

`revised_manuscript_v4.tex` is a standalone `article` (10pt letterpaper) using `algorithm2e`,
`tcolorbox` (a `findingbox` environment for per-RQ finding boxes), `booktabs`, and `authblk`.
Notation is fixed by macros defined in the preamble — use `\vexist`, `\vsecure`, `\vrelevant`,
`\sfinal`, `\tausec` rather than writing the math inline. Figures are referenced as
`figures/figN_*.png` relative to the manuscript directory. Note that the preamble declares
`\newtheorem{definition}{Définition}`, so every `\begin{definition}` block in §4.1 renders with a
French label.
