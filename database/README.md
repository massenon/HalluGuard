# `database/` — upstream benchmark inputs

**This directory is not wired into the framework.** Nothing in `halluguard/`, `experiments/` or
`tests/` imports from it, and it is not part of any reported result. It holds the upstream
benchmark material from which the study's generation corpus was built, kept alongside the
package so the task sources are inspectable.

Attribution and licences for every file here are in [`../NOTICE`](../NOTICE).

## Contents

| File | Records | What it is |
|---|---|---|
| `HumanEval.jsonl.gz` | 164 | OpenAI HumanEval tasks (MIT) |
| `sanitized-mbpp.json` | 427 | MBPP sanitized subset (CC-BY-4.0) |
| `data_compliance_hallucination.json` | 941 | CodeHaluEval, data-compliance hallucination category |
| `external_source_hallucination.json` | 530 | CodeHaluEval, external-source hallucination category |
| `humaneval.py` | — | EvalPlus HumanEval+ loader, vendored verbatim (Apache-2.0) |
| `mbpp.py` | — | EvalPlus MBPP+ loader, vendored verbatim (Apache-2.0) |

## Caveats

* **The loaders do not run as shipped.** `humaneval.py` and `mbpp.py` import `evalplus` (and
  `mbpp.py` also imports `wget`), neither of which is a declared dependency in
  `pyproject.toml`. To use them: `pip install evalplus wget`. They download and cache upstream
  data on first call; this repository does not vendor the HumanEval+/MBPP+ *plus* files.
* **Counts do not match the manuscript's task counts.** The manuscript's primary corpus is
  664 tasks = HumanEval+ (164) + MBPP (500). The MBPP file here is the *sanitized* subset
  (427 tasks), not the 500-task set. The two CodeHaluEval files total 1,471 records, whereas the
  manuscript describes CodeHaluEval as 1,183 tasks — these are two of its categories, not the
  whole benchmark.
* **Not covered by `data/checksums.sha256`**, which scopes only the released evaluation data
  under `data/` and `results/expected/`. Verify these files against their upstream sources.
* `external_source_hallucination.json` is 48 MB, above GitHub's 50 MB warning threshold for a
  single file though below the 100 MB hard limit. If the repository is later mirrored somewhere
  with tighter limits, move this directory to Git LFS or drop it from the tree.
