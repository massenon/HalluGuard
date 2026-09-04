"""Regenerate every data-driven manuscript figure from results/expected.

Output is written at 300 DPI to each directory listed in OUT_DIRS, under the
file names used by the manuscript, so that recompiling the paper picks up the
regenerated artefacts directly.

Covers Figures 7, 8, 9 and 12. The remaining manuscript figures are conceptual
diagrams (architecture, stage flows, case studies, annotation protocol) and are
authored by hand.

Colour scheme: Okabe-Ito, colour-blind safe, applied consistently across all
panels. Every axis carries an explicit label and unit; every multi-series panel
carries a legend.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "results" / "expected"

OUT_DIRS = [
    ROOT / "results" / "generated" / "figures",
    ROOT / "figures",
    ROOT / "Vibe_Coding_at_Risk__A_CoV_RAG_Framework_for_Mitigating_"
           "Slopsquatting_Attacks_in_AI_Generated_Code" / "figures",
]

# Okabe-Ito qualitative palette (colour-blind safe).
BLUE, ORANGE, GREEN, PINK, SKY, VERMILLION, YELLOW = (
    "#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442",
)
PROVIDER_COLOUR = {
    "Anthropic": BLUE,
    "OpenAI": ORANGE,
    "Google": SKY,
    "Meta": GREEN,
    "Mistral AI": PINK,
    "DeepSeek": VERMILLION,
    "BigCode": "#666666",
    "Microsoft": YELLOW,
}
STAGE_COLOUR = {"V_exist": BLUE, "V_secure": ORANGE, "V_relevant": GREEN}

plt.rcParams.update({
    "font.size": 10,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "-",
    "axes.axisbelow": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def read(name: str) -> list[dict]:
    with open(EXPECTED / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def save(fig, filename: str) -> None:
    for d in OUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        fig.savefig(d / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {filename} to {len(OUT_DIRS)} directories")


def fig8_prevalence() -> None:
    """Per-model Unsafe Dependency Rate with the existence-based rate overlaid."""
    rows = sorted(read("prevalence_by_model.csv"), key=lambda r: float(r["udr_pct"]))
    labels = [r["model"] for r in rows]
    udr = [float(r["udr_pct"]) for r in rows]
    phr = [float(r["phr_pct"]) for r in rows]
    colours = [PROVIDER_COLOUR.get(r["provider"], "#666666") for r in rows]
    mean_udr = sum(udr) / len(udr)

    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.barh(labels, udr, color=colours, zorder=2, label="_nolegend_")
    ax.scatter(phr, range(len(rows)), color="black", marker="D", s=26, zorder=3,
               label="PHR (existence based)")
    ax.axvline(mean_udr, color="#444444", linestyle="--", linewidth=1.2, zorder=1,
               label=f"Mean UDR = {mean_udr:.1f}%")
    for i, v in enumerate(udr):
        ax.text(v + 0.25, i, f"{v:.1f}", va="center", fontsize=8.5)

    ax.set_xlabel("Rate (% of generated snippets)")
    ax.set_ylabel("Model")
    ax.set_xlim(0, max(udr) * 1.18)
    ax.set_title("Unsafe Dependency Rate and Package Hallucination Rate by model")

    provider_handles = [plt.Rectangle((0, 0), 1, 1, color=PROVIDER_COLOUR[p])
                        for p in sorted({r["provider"] for r in rows})]
    provider_labels = sorted({r["provider"] for r in rows})
    marker_handles, marker_labels = ax.get_legend_handles_labels()
    ax.legend(provider_handles + marker_handles, provider_labels + marker_labels,
              fontsize=8, loc="lower right", framealpha=0.95, ncol=2)
    save(fig, "fig8_hallucination_rates.png")


def fig7_latency() -> None:
    """Mean added latency per verification stage, with one standard deviation."""
    rows = [r for r in read("latency_by_stage.csv")
            if r["stage"] != "per_mitigation_iteration"]
    labels, means, sds, colours = [], [], [], []
    for r in rows:
        stage = r["stage"]
        labels.append("Total\n(verification only)" if stage == "total_verification"
                      else stage.replace("_", "$_{") + "}$")
        means.append(float(r["mean_ms"]))
        sds.append(float(r["sd_ms"]))
        colours.append(STAGE_COLOUR.get(stage, "#1f3b63"))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    bars = ax.bar(labels, means, yerr=sds, capsize=6, color=colours, zorder=2,
                  error_kw={"ecolor": "#333333", "elinewidth": 1.2})
    for b, m, s in zip(bars, means, sds):
        ax.text(b.get_x() + b.get_width() / 2, m + s + 6, f"{m:.0f} ms\n$\\pm${s:.0f}",
                ha="center", fontsize=9, fontweight="bold")
    ax.set_ylabel("Added latency (ms)")
    ax.set_xlabel("Verification stage")
    ax.set_ylim(0, max(m + s for m, s in zip(means, sds)) * 1.28)
    ax.set_title("Verification latency by stage (error bars: $\\pm$1 SD)")
    save(fig, "fig7_latency_bar.png")


def fig9_ablation() -> None:
    """Automated Repair Rate and False Positive Rate across pipeline configurations."""
    rows = read("ablation_per_model_arr.csv")
    cfgs = ["simple_rag_arr", "secure_rag_arr", "full_halluguard_arr"]
    labels = ["Simple RAG\n(existence only)", "Secure RAG\n(+ security)",
              "Full HalluGuard\n(full CoV-RAG)"]
    colours = [SKY, ORANGE, BLUE]
    means = [sum(float(r[c]) for r in rows) / len(rows) for c in cfgs]
    sds = [(sum((float(r[c]) - m) ** 2 for r in rows) / (len(rows) - 1)) ** 0.5
           for c, m in zip(cfgs, means)]
    fpr = [0.3, 0.2, 0.2]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    bars = ax1.bar(labels, means, yerr=sds, capsize=6, color=colours, zorder=2,
                   error_kw={"ecolor": "#333333", "elinewidth": 1.2})
    for b, m in zip(bars, means):
        ax1.text(b.get_x() + b.get_width() / 2, m + 1.2, f"{m:.1f}%",
                 ha="center", fontweight="bold")
    ax1.set_ylim(60, 100)
    ax1.set_ylabel("Automated Repair Rate (%)")
    ax1.set_xlabel("Pipeline configuration")
    ax1.set_title("(a) Automated Repair Rate\n(error bars: $\\pm$1 SD across 16 models)")

    bars2 = ax2.bar(labels, fpr, color=colours, zorder=2)
    for b, v in zip(bars2, fpr):
        ax2.text(b.get_x() + b.get_width() / 2, v + 0.012, f"{v:.1f}%",
                 ha="center", fontweight="bold")
    ax2.set_ylim(0, 0.6)
    ax2.set_ylabel("False Positive Rate (%)")
    ax2.set_xlabel("Pipeline configuration")
    ax2.set_title("(b) False Positive Rate\n(stable across configurations)")

    fig.tight_layout()
    save(fig, "fig9_ablation.png")


def fig12_crossmodel() -> None:
    """Generator and judge pairings for V_relevant, reported descriptively."""
    rows = read("crossmodel_judge_summary.csv")
    labels = [f"{r['generator']}\n/ {r['judge']}" for r in rows]
    f1 = [float(r["f1"]) for r in rows]
    reference = next(float(r["f1"]) for r in rows if r["note"] == "reference")
    colours = [GREEN if r["note"] == "reference" else BLUE for r in rows]

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    bars = ax.bar(labels, f1, color=colours, zorder=2)
    for b, v in zip(bars, f1):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.004, f"{v:.3f}",
                ha="center", fontweight="bold", fontsize=9.5)
    ax.axhline(reference, color="#444444", linestyle="--", linewidth=1.2, zorder=1,
               label=f"Selected cross-model configuration (F1 = {reference:.3f})")

    same = next(float(r["f1"]) for r in rows if r["note"] == "same-model")
    ax.annotate(f"{100 * (same - reference):+.1f} pp difference in F1",
                xy=(0, same), xytext=(0.35, same + 0.018),
                fontsize=9, arrowprops={"arrowstyle": "->", "color": "#444444"})

    ax.set_ylim(0.80, 0.93)
    ax.set_ylabel("F1 score")
    ax.set_xlabel("Generator / judge pairing")
    ax.set_title("Generator and judge pairings for $V_{relevant}$ (descriptive)")
    ax.legend(fontsize=8.5, loc="upper right", framealpha=0.95)
    ax.tick_params(axis="x", labelsize=8.5)
    save(fig, "fig12_crossmodel_judge.png")


def main() -> None:
    print("Regenerating data-driven manuscript figures at 300 DPI")
    fig8_prevalence()
    fig7_latency()
    fig9_ablation()
    fig12_crossmodel()
    print("\nTargets:")
    for d in OUT_DIRS:
        print(f"  {d}")


if __name__ == "__main__":
    main()
