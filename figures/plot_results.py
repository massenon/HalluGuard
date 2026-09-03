"""Regenerate summary figures from results/expected (300 DPI PNG, Okabe-Ito palette)."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "results" / "expected"
OUT = ROOT / "results" / "generated" / "figures"
OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]


def read(name: str) -> list[dict]:
    with open(EXPECTED / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def prevalence() -> None:
    rows = sorted(read("prevalence_by_model.csv"), key=lambda r: float(r["udr_pct"]))
    providers = sorted({r["provider"] for r in rows})
    colour = {p: OKABE_ITO[i % len(OKABE_ITO)] for i, p in enumerate(providers)}
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh([r["model"] for r in rows], [float(r["udr_pct"]) for r in rows],
            color=[colour[r["provider"]] for r in rows], label="UDR")
    ax.scatter([float(r["phr_pct"]) for r in rows], range(len(rows)), color="black", zorder=3, s=18, label="PHR")
    ax.set_xlabel("Rate (%)")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=colour[p]) for p in providers] + [ax.collections[0]],
              labels=providers + ["PHR (existence-based)"], fontsize=8, loc="lower right")
    ax.set_title("Unsafe Dependency Rate and Package Hallucination Rate by model")
    fig.tight_layout()
    fig.savefig(OUT / "prevalence_by_model.png", dpi=300)
    plt.close(fig)


def latency() -> None:
    rows = [r for r in read("latency_by_stage.csv") if r["stage"] != "per_mitigation_iteration"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([r["stage"] for r in rows], [float(r["mean_ms"]) for r in rows],
           yerr=[float(r["sd_ms"]) for r in rows], capsize=6, color=OKABE_ITO[:len(rows)])
    ax.set_ylabel("Latency (ms), error bars = ±1 SD")
    ax.set_title("Verification latency by stage")
    fig.tight_layout()
    fig.savefig(OUT / "latency_by_stage.png", dpi=300)
    plt.close(fig)


def ablation() -> None:
    rows = read("ablation_per_model_arr.csv")
    cfgs = ["simple_rag_arr", "secure_rag_arr", "full_halluguard_arr"]
    labels = ["Simple RAG", "Secure RAG", "Full HalluGuard"]
    means = [sum(float(r[c]) for r in rows) / len(rows) for c in cfgs]
    sds = [(sum((float(r[c]) - m) ** 2 for r in rows) / (len(rows) - 1)) ** 0.5 for c, m in zip(cfgs, means)]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(labels, means, yerr=sds, capsize=6, color=OKABE_ITO[:3])
    ax.set_ylim(60, 100)
    ax.set_ylabel("Automated Repair Rate (%), error bars = ±1 SD across 16 models")
    ax.set_title("Ablation: contribution of each verification stage")
    fig.tight_layout()
    fig.savefig(OUT / "ablation_arr.png", dpi=300)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    prevalence()
    latency()
    ablation()
    print(f"figures written to {OUT}")


if __name__ == "__main__":
    main()
