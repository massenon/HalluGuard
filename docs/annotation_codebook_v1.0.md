# Human annotation codebook, version 1.0

This is the codebook referenced by the `codebook_version` column of
`data/gold_standard/annotated_gold_standard_g800.csv`. It reproduces Appendix E of the
manuscript so that the value in that column resolves to something readable.

**Provenance caveat.** The gold-standard file is reconstructed from reported aggregates; the
original annotation sheets were not retained (`data/PROVENANCE.md`). This codebook documents the
protocol as specified and applied during the study. It is not itself derived from the shipped
CSV, and the shipped CSV is not evidence that the protocol was followed on any particular row.

## 1. Hallucination labelling

Annotators independently labelled each snippet as containing a **hallucination** if any imported
dependency referenced a package that was not resolvable on the canonical registry (PyPI) at the
time of annotation.

Resolution was verified by a live registry query performed **independently of the HalluGuard
pipeline under evaluation**. This independence is the point of Tier B: reusing HalluGuard's own
`V_exist` result as the label would measure self-consistency rather than validity.

Label values: `hallucination`, `no_hallucination`.

Recorded in columns `annotator_a_label`, `annotator_b_label`.

## 2. Semantic correctness rubric

A repaired snippet was labelled **semantically correct** if, when executed against the original
task's reference test suite (HumanEval+, MBPP or CodeHaluEval), all tests passed **without any
modification to the test harness**.

Recorded in `data/gold_standard/scr_execution_sample_400.csv` as `unit_tests_passed`
(`True` / `False`) with `result_category` in {`pass`, `fail-import`, `fail-param`,
`fail-logic`, `timeout`}. The categories are assigned by `experiments/verify_scr.py::classify`:

| Category | Assigned when the captured output contains |
|---|---|
| `fail-import` | `ModuleNotFoundError` or `ImportError` |
| `fail-param` | `TypeError` or `ValueError` |
| `fail-logic` | any other non-zero exit |
| `timeout` | the process exceeded the per-case wall-clock limit (default 10 s) |

## 3. Disagreement resolution

Snippets receiving discordant labels from the two primary annotators were adjudicated by a
third, independent annotator, whose label was final.

* `adjudicated` = `yes` marks the rows where annotator A and annotator B disagreed
  (30 of 800 = 3.8%; this count is what reproduces the reported κ = 0.88).
* `annotator_c_label` carries the adjudicator's label and is populated on adjudicated rows only.
* `final_label` is the ground truth: the agreed label where A = B, otherwise the adjudicator's.

Inter-rater agreement before adjudication was Cohen's κ = 0.88, computed by
`halluguard.stats.cohens_kappa` over the two primary annotators' label sequences and reported by
`experiments/rq2_detection_repair.py`.

## 4. Sampling

800 snippets, stratified as 50 per model across the 16 evaluated models, drawn from the primary
prevalence corpus. The `dataset_tier` column records the source benchmark (MBPP, HumanEval+ or
CodeHaluEval) for each snippet.

## 5. What the labels are compared against

`halluguard_prediction` (`flagged` / `not_flagged`) is HalluGuard's verdict for the snippet.
Detection Rate is TP/(TP+FN) over the positive class (`final_label == hallucination`, N = 152);
False Positive Rate is FP/(FP+TN) over the negative class (N = 648).
