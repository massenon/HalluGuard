# Known deviations between the manuscript and this reference implementation

The manuscript describes the system as operated during the study. This repository is the
released reference implementation. Where the two differ, the difference is recorded here rather
than being left for a reader to discover. Each entry states what the paper says, what the code
does, and why it matters.

## 1. Dependency extraction uses `ast`, not `tree-sitter`

* **Manuscript** (§4.3, Stage 1): extraction uses the `tree-sitter` incremental parser to build
  a concrete syntax tree, with language-specific traversal queries.
* **This repository**: `halluguard/extractor.py` uses the Python standard-library `ast` module.
* **Why it matters**: for the Python/PyPI scope of this work the two are equivalent in output —
  both handle aliased imports, multi-line import blocks and conditional imports correctly, and
  `ast` is the reference parser for the language. `tree-sitter` matters only for the
  multi-language extension discussed as future work. The released implementation has one fewer
  dependency and no build step.

## 2. `V_secure` queries OSV live, not a dated snapshot

* **Manuscript** (§4.4 Step 2, Table 6): `S_vuln` is computed against a fixed-date snapshot of
  the OSV database, dated 2025-03-01.
* **This repository**: `SecurityScorer.query_severity()` POSTs to `https://api.osv.dev/v1/query`
  and reads whatever the live database returns. `config.yaml` records
  `osv_snapshot_date: "2025-03-01"` for documentation, but **no code reads that key**, and the
  snapshot itself is not distributed.
* **Why it matters**: this is the deviation with real consequences. Security sub-scores computed
  by running this code today will not equal study-time values, because advisories have been
  added to OSV since 2025-03-01. In particular, the three "OSV database lag" false negatives in
  the reported taxonomy would likely now be detected. Any live re-run is a measurement of the
  framework against today's OSV, not a reproduction of the reported figures.

## 3. Reference lists are reduced

* **Manuscript**: a ~20,000-entry module→package dictionary built from PyPI metadata (§4.3
  Stage 2), and a top-5,000-package reference list for the Levenshtein check (Table 6,
  `typosquat_list_size`).
* **This repository**: `module_to_package.json` ships 17 mappings and
  `popular_pypi_reference.json` ships 159 names.
* **Why it matters**: `typosquat_similarity()` takes the maximum similarity over the reference
  list, so a shorter list yields systematically *lower* `S_typo` and therefore *higher*
  `S_final`. Live runs of this code are more permissive than the study configuration. The
  full lists are not distributed.

## 4. Configuration keys that no code reads

`halluguard/config.py` loads `typosquat_list_size`, `osv_snapshot_date` and `seeds` into
`Settings`, but nothing in `halluguard/` or `experiments/` consumes them. They are retained as
machine-readable documentation of the study configuration. `SecurityScorer` receives its
reference list directly as a constructor argument, and `grid_search.py` takes its own `--seed`
(default 42).

## 5. Figure regeneration is partial

`figures/plot_results.py` regenerates three figures from `results/expected/`: prevalence by
model, latency by stage, and the ablation bar chart. The remaining manuscript figures
(architecture and flow diagrams, the two case studies, the cross-model judge chart, the NL-API
sequence diagram and the annotation-protocol diagram) were authored by hand and are not
regenerable from this repository.

## 6. Metric names were renamed after the first release

The initial public release used `HR` (hallucination rate) and `MSR` (mitigation success rate).
The manuscript and this release use **PHR** (Package Hallucination Rate, existence-based),
**UDR** (Unsafe Dependency Rate, any-stage) and **ARR** (Automated Repair Rate). `HR` maps to
UDR, and the old `rejected_vexist_pct` column maps to PHR. See
`docs/CHANGELOG-replication.md`.

## 7. Data provenance

The record-level evaluation files are reconstructed from reported aggregates, not raw logs.
This is documented separately and in full in [`data/PROVENANCE.md`](../data/PROVENANCE.md).
Read that before drawing any conclusion from a script's output.
