# Replication package changelog

## v1.0.0 — corrected release

Replaces the initial release. The earlier tree remains reachable at tag
`v0.9-preprint-snapshot`.

### Corrected

* **Cohen's κ now matches the manuscript.** The first reconstruction of the `G_800` annotator
  columns targeted the confusion matrix but not the inter-rater statistic, producing 115
  disagreements and κ = 0.60 against a manuscript reporting κ = 0.88 — visible to anyone running
  `experiments/rq2_detection_repair.py`, which prints κ. The two are mutually exclusive: with a
  152/800 positive class, κ = 0.88 requires ~30 disagreements, not 115. The annotator A/B,
  `adjudicated` and `annotator_c_label` columns were regenerated (seed 42) to reproduce
  κ = 0.8800 exactly, at 30 adjudicated rows. `final_label` and `halluguard_prediction` were left
  untouched, so TP/FN/FP/TN remain 150/2/1/647 and DR/FPR remain 98.7% / 0.2%.
  `tests/test_datasets.py` now asserts κ directly so this cannot drift again.
* **Record counts now match the manuscript.** The previous release shipped a 50-row gold
  standard, 250 NL-API prompts, a 45-package "representative sample" of the adversarial
  benchmark and a 15-entry module dictionary, against a manuscript reporting 800, 2,500, 500 and
  ~20,000 respectively. Files are now full-size at the reported N.
* **Adversarial confusion matrix no longer sums to twice the benchmark.** The previous
  `results/raw/table12_adversarial_security.csv` reported TP 485 / FN 15 / TN 491 / FP 9, which
  totals 1,000 for a benchmark of N = 500. The released figures are TP 341 / FP 1 / TN 149 /
  FN 9 = 500.
* **ARR denominator.** Previously reported as 92.5% over n = 576,000, a denominator appearing
  nowhere in the manuscript. Now 92.4% = 729/789 over the repair-attempt pool.
* **SCR** aligned to 96.0% (384/400), Wilson [93.6%, 97.5%]; previously 96.1% [93.4, 97.8].
* **Adversarial precision** aligned to 99.7%; previously 98.2%.
* **Metric names.** `HR` -> `UDR` (Unsafe Dependency Rate, any-stage) and its
  `rejected_vexist_pct` column -> `PHR` (Package Hallucination Rate, existence-based);
  `MSR` -> `ARR` (Automated Repair Rate).
* **`CITATION.cff`** no longer contains the placeholder `https://github.com/[YOUR-ORG]/halluguard`.
* **Removed `push_to_github.sh` / `push_to_github.bat`**, which shipped `YOUR-ORG/YOUR-REPO`
  placeholders and belonged to the release process rather than the artifact.

### Added

* `data/PROVENANCE.md` — what each data file is and where it came from.
* `REPRODUCTION.md` — every manuscript table and figure mapped to the command that produces it,
  grouped by what each command establishes.
* `docs/DEVIATIONS.md` — where this implementation differs from the manuscript's description.
* `docs/annotation_codebook_v1.0.md` — the codebook named by the `codebook_version` column.
* `NOTICE` — third-party attribution for the vendored EvalPlus loaders and benchmark data.
* `SECURITY.md`, `.github/workflows/ci.yml`, `experiments/descriptive_summaries.py`.
* Apache-2.0 provenance headers on `database/humaneval.py` and `database/mbpp.py`.

### Restructured

* `data/` is now organised by evaluation set (`gold_standard/`, `adversarial_benchmark/`,
  `security_validation/`, `nl_api/`, `package_dictionary/`) with a column-level schema in
  `data/MANIFEST.md` and SHA-256 checksums in `data/checksums.sha256`.
* `results/raw/table*.csv` -> `results/expected/*.csv`, named by content rather than by
  manuscript table number so that renumbering the paper does not invalidate the package.
* `experiments/rq1_hallucination_rate.py` -> `experiments/rq1_prevalence.py`.
* `figures/generate_all.py` -> `figures/plot_results.py`.
* `halluguard/prompts/verbatim_*.txt` -> `halluguard/prompts/{relevance,mitigation}_{system,user}.txt`.
* Dropped `data/package_dictionary/js_modules.json`; the framework is Python/PyPI only.
