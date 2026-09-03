"""Descriptive summaries: cross-model judge pairings and financial cost.

Both tables are printed from retained aggregate summaries. Neither supports an
inferential claim, and the manuscript does not make one:

  * Cross-model judge — instance-level paired records were not retained, so the
    2.0 pp F1 difference between the same-model and cross-model configurations is
    reported descriptively. No significance test is defensible on these data.
  * Financial cost — the recorded figures are generator-side lower bounds. They
    exclude judge calls, failed requests and regeneration retries.

Every other shipped summary already has an entry point; this script exists so that
no file in results/expected/ is left without one.
"""

from __future__ import annotations

from experiments.common import EXPECTED, read_csv

BANNER = "  [descriptive only - no inferential claim is supported by this table]"


def crossmodel() -> None:
    print("Cross-model judge pairings (results/expected/crossmodel_judge_summary.csv)")
    print(BANNER)
    print(f"  {'generator':<12} {'judge':<22} {'P':>6} {'R':>6} {'F1':>6}  {'dF1':>6}  note")
    for r in read_csv(EXPECTED / "crossmodel_judge_summary.csv"):
        print(f"  {r['generator']:<12} {r['judge']:<22} {r['precision']:>6} {r['recall']:>6} "
              f"{r['f1']:>6}  {r['delta_f1_vs_reference'] or '':>6}  {r['note']}")
    print("  Instance-level paired records were not retained; see data/PROVENANCE.md.")


def cost() -> None:
    print("\nFinancial overhead (results/expected/cost_estimate.csv)")
    print(BANNER)
    for r in read_csv(EXPECTED / "cost_estimate.csv"):
        print(f"  {r['metric']:<48} ${r['value_usd']:>10}  ({r['note']})")
    print("  Generator-side lower bounds; judge calls, failed requests and retries excluded.")


def main() -> None:
    crossmodel()
    cost()


if __name__ == "__main__":
    main()
