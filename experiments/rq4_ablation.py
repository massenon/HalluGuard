"""RQ4 — ablation of verification stages (paired t-tests, Bonferroni, Cohen's d).

Reads results/expected/ablation_per_model_arr.csv (one row per model).
"""

from __future__ import annotations

from scipy import stats as sps

from experiments.common import EXPECTED, GENERATED, read_csv, write_csv
from halluguard.stats import cohens_d, interpret_d, mean_ci_t

CONFIGS = ["no_guard_arr", "simple_rag_arr", "secure_rag_arr", "full_halluguard_arr"]
N_COMPARISONS = 3
ALPHA_ADJ = 0.05 / N_COMPARISONS


def main() -> None:
    rows = read_csv(EXPECTED / "ablation_per_model_arr.csv")
    series = {c: [float(r[c]) for r in rows] for c in CONFIGS}
    full = series["full_halluguard_arr"]
    out = []
    for cfg in CONFIGS[:-1]:
        base = series[cfg]
        t_stat, p_val = sps.ttest_rel(full, base)
        mean, lo, hi = mean_ci_t(base)
        d = cohens_d(full, base)
        out.append({"comparison": f"{cfg} vs full_halluguard", "baseline_mean": f"{mean:.1f}",
                    "baseline_ci95_low": f"{lo:.2f}", "baseline_ci95_high": f"{hi:.2f}",
                    "t": f"{t_stat:.2f}", "p": f"{p_val:.2e}",
                    "significant_bonferroni": str(p_val < ALPHA_ADJ), "alpha_adj": f"{ALPHA_ADJ:.4f}",
                    "cohens_d": f"{d:.2f}", "effect": interpret_d(d)})
        print(out[-1])
    mean, lo, hi = mean_ci_t(full)
    print(f"full_halluguard mean {mean:.1f} (95% CI {lo:.2f}–{hi:.2f}), n={len(full)} models")
    write_csv(GENERATED / "rq4_ablation.csv", out, list(out[0].keys()))


if __name__ == "__main__":
    main()
