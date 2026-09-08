"""Regenerate the schematic manuscript figures that carry study numbers.

Covers the annotation protocol (Figure A) and the two case studies (Figures 10
and 11). These were previously hand-drawn and had drifted from the data:

  fig_annotation_protocol  conflict rate read 14.3%, which is incompatible with
                           the reported Cohen's kappa of 0.88; the value is 3.8%
                           (30 of 800).
  fig10_casestudy1         showed a "V_path" stage that the framework does not
                           implement, and omitted V_secure. The chain is
                           V_exist, V_secure, V_relevant.
  fig11_casestudy2         version axis was unordered (v80 appeared twice, v65
                           below v60) and point labels did not match the axis.

Drawing them here keeps them consistent with data/ and with the manuscript.
Output goes to every directory in OUT_DIRS at 300 DPI.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import (  # noqa: E402
    FancyArrowPatch, FancyBboxPatch, Rectangle,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

OUT_DIRS = [
    ROOT / "results" / "generated" / "figures",
    ROOT / "figures",
    ROOT / "Vibe_Coding_at_Risk__A_CoV_RAG_Framework_for_Mitigating_"
           "Slopsquatting_Attacks_in_AI_Generated_Code" / "figures",
]

BLUE, ORANGE, GREEN, PINK, RED, GREY = (
    "#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00", "#666666",
)
INK = "#1a1a1a"

# Computer Modern mathtext so V_exist and friends match the LaTeX body font.
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["font.family"] = "DejaVu Sans"


def save(fig, filename: str, also_pdf: bool = False) -> None:
    """Write at 300 DPI to every target, optionally alongside a vector PDF."""
    for d in OUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        fig.savefig(d / filename, dpi=300, bbox_inches="tight", facecolor="white")
        if also_pdf:
            fig.savefig(d / filename.replace(".png", ".pdf"),
                        bbox_inches="tight", facecolor="white")
    plt.close(fig)
    suffix = " (+ vector PDF)" if also_pdf else ""
    print(f"  wrote {filename} to {len(OUT_DIRS)} directories{suffix}")


def box(ax, x, y, w, h, text, face="#ffffff", edge=INK, fontsize=9,
        weight="normal", radius=0.02):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0.008,rounding_size={radius}",
        facecolor=face, edgecolor=edge, linewidth=1.3, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight, color=INK, zorder=3)


def arrow(ax, xy_from, xy_to, colour=INK, style="-|>", lw=1.4, rad=0.0):
    ax.add_patch(FancyArrowPatch(
        xy_from, xy_to, arrowstyle=style, mutation_scale=13, linewidth=lw,
        color=colour, zorder=4,
        connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))


# ---------------------------------------------------------------- Figure A
def annotation_protocol() -> None:
    """Two independent annotators, consensus check, expert adjudication."""
    rows = list(csv.DictReader(
        open(DATA / "gold_standard/annotated_gold_standard_g800.csv", encoding="utf-8")))
    n = len(rows)
    conflicts = sum(r["adjudicated"] == "yes" for r in rows)
    pct = 100.0 * conflicts / n

    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.6)
    ax.axis("off")

    for x, w, title in [(0.15, 3.4, "Phase 1\nIndependent blind labelling"),
                        (3.75, 2.7, "Phase 2\nConsensus check"),
                        (6.65, 4.2, "Phase 3\nExpert adjudication")]:
        ax.add_patch(FancyBboxPatch((x, 0.35), w, 4.75,
                                    boxstyle="round,pad=0.01,rounding_size=0.04",
                                    facecolor="#f4f4f4", edgecolor="#cccccc", zorder=1))
        ax.text(x + w / 2, 4.78, title, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color=INK, zorder=3)

    box(ax, 0.35, 3.45, 1.35, 0.62, "Annotator A")
    box(ax, 0.35, 2.45, 1.35, 0.62, "Annotator B")
    box(ax, 0.35, 0.75, 1.35, 0.62, f"{n} snippets\n(50 per model)", face="#eaf2fb", fontsize=8.5)
    box(ax, 2.05, 2.45, 1.35, 1.62, "Blind\nlabelling\ninterface", face="#ffffff")
    arrow(ax, (1.70, 3.76), (2.05, 3.55))
    arrow(ax, (1.70, 2.76), (2.05, 2.95))
    arrow(ax, (1.03, 1.37), (1.03, 2.45), rad=0.0)
    ax.text(1.12, 1.95, "sampled", fontsize=7.5, color=GREY, rotation=90, va="center")

    box(ax, 4.05, 2.85, 2.1, 0.75, "Labels agree?", face="#fdf0ea", edge=RED)
    arrow(ax, (3.40, 3.26), (4.05, 3.23))

    box(ax, 7.05, 3.55, 2.35, 0.72, f"Consensus label\n({n - conflicts} of {n})",
        face="#e8f6ef", edge=GREEN, fontsize=9)
    box(ax, 7.05, 1.75, 2.35, 0.72, "Senior adjudicator\nlabel is final",
        face="#fdf0ea", edge=RED, fontsize=9)
    box(ax, 9.75, 2.55, 1.1, 1.35,
        f"Gold\nstandard\n$G_{{{n}}}$\n$\\kappa=0.88$", face="#f6f0fa", edge=PINK, fontsize=8.5)

    arrow(ax, (6.15, 3.35), (7.05, 3.91), colour=GREEN, rad=0.12)
    ax.text(6.30, 3.95, "agree", fontsize=8.5, color=GREEN, fontweight="bold")
    arrow(ax, (6.15, 3.10), (7.05, 2.11), colour=RED, rad=-0.12)
    ax.text(6.28, 2.66, f"disagree\n{conflicts} of {n} ({pct:.1f}%)",
            fontsize=8.5, color=RED, fontweight="bold", ha="left", va="bottom")

    arrow(ax, (9.40, 3.91), (9.75, 3.45), colour=GREY)
    arrow(ax, (9.40, 2.11), (9.75, 2.85), colour=GREY)

    ax.set_title("Human annotation and adjudication protocol", fontsize=12,
                 fontweight="bold", pad=8)
    save(fig, "fig_annotation_protocol.png")


# --------------------------------------------------------------- Figure 10
DIFF_RED_BG, DIFF_RED_INK = "#ffeef0", "#82071e"
DIFF_GRN_BG, DIFF_GRN_INK = "#e6ffed", "#04663b"
NODE_BG, NODE_EDGE = "#eef2f7", "#43607e"


def _code_block(ax, x, y_top, lines, width, mono=7.6, line_h=0.255):
    """Render git-diff style code: '-' lines on red, '+' on green, context plain."""
    y = y_top
    for marker, text in lines:
        if marker in "-+":
            bg = DIFF_RED_BG if marker == "-" else DIFF_GRN_BG
            ink = DIFF_RED_INK if marker == "-" else DIFF_GRN_INK
            ax.add_patch(Rectangle((x, y - line_h * 0.78), width, line_h,
                                   facecolor=bg, edgecolor="none", zorder=2))
        else:
            ink = "#3a3f45"
        ax.text(x + 0.10, y - line_h * 0.30, marker, fontsize=mono, family="monospace",
                color=ink, va="center", zorder=3, fontweight="bold")
        ax.text(x + 0.34, y - line_h * 0.30, text, fontsize=mono, family="monospace",
                color=ink, va="center", zorder=3)
        y -= line_h


def case_study_1() -> None:
    """Detection to repair: the chain is V_exist, V_secure, V_relevant."""
    fig, ax = plt.subplots(figsize=(13.2, 6.6))
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 6.6)
    ax.axis("off")

    for cx, title in [(2.15, "LLM generated snippet"),
                      (6.6, "Verification workflow"),
                      (11.05, "Verified repair")]:
        ax.text(cx, 6.28, title, ha="center", fontsize=11.5, fontweight="bold", color=INK)

    # ---- left: flawed snippet -------------------------------------------
    ax.add_patch(FancyBboxPatch((0.25, 2.30), 3.8, 3.68,
                                boxstyle="round,pad=0.012,rounding_size=0.05",
                                facecolor="#ffffff", edgecolor=DIFF_RED_INK, linewidth=1.4))
    _code_block(ax, 0.35, 5.80, [
        ("-", "from langchain_milvus.retrievers \\"),
        ("-", "     import MilvusCollectionHybrid \\"),
        ("-", "           SearchRetriever"),
        (" ", ""),
        (" ", "retriever = MilvusCollection \\"),
        (" ", "    HybridSearchRetriever("),
        (" ", "    collection=collection,"),
        (" ", "    anns_fields=[\"dense\",\"sparse\"],"),
        (" ", "    top_k=5)"),
    ], width=3.60)
    ax.text(2.15, 2.52, "sub-module .retrievers absent from the distribution",
            fontsize=7.9, style="italic", ha="center", color=DIFF_RED_INK)

    # ---- centre: verification workflow ----------------------------------
    stages = [
        (r"$V_{\mathit{exist}}$", "PyPI JSON API, HTTP 200\nparent distribution registered",
         "PASS", GREEN),
        (r"$V_{\mathit{secure}}$", "no advisory, established\nreputation, low name similarity",
         "PASS", GREEN),
        (r"$V_{\mathit{relevant}}$", "package cannot satisfy\nthe stated request",
         "FAIL", DIFF_RED_INK),
    ]
    y = 5.42
    for name, detail, verdict, colour in stages:
        face = "#e8f6ef" if verdict == "PASS" else DIFF_RED_BG
        ax.add_patch(FancyBboxPatch((4.70, y), 3.80, 0.86,
                                    boxstyle="round,pad=0.010,rounding_size=0.04",
                                    facecolor=face, edgecolor=colour, linewidth=1.4, zorder=2))
        ax.text(4.92, y + 0.58, name, fontsize=11, va="center", zorder=3)
        ax.text(4.92, y + 0.25, detail, fontsize=7.4, va="center", color="#3a3f45", zorder=3)
        ax.text(8.30, y + 0.43, verdict, fontsize=9.5, fontweight="bold",
                color=colour, ha="right", va="center", zorder=3)
        if y > 3.4:
            arrow(ax, (6.60, y), (6.60, y - 0.36), colour=NODE_EDGE)
        y -= 1.22

    ax.add_patch(FancyBboxPatch((4.70, 2.02), 3.80, 0.80,
                                boxstyle="round,pad=0.010,rounding_size=0.04",
                                facecolor="#fff4e2", edgecolor=ORANGE, linewidth=1.4, zorder=2))
    ax.text(6.60, 2.42, "Mitigation module\nstructured correction prompt",
            fontsize=8.6, ha="center", va="center", zorder=3)
    arrow(ax, (6.60, 2.98), (6.60, 2.86), colour=DIFF_RED_INK)

    ax.add_patch(FancyBboxPatch((4.70, 1.02), 3.80, 0.68,
                                boxstyle="round,pad=0.010,rounding_size=0.03",
                                facecolor="#f6f7f8", edgecolor="#c3c8ce",
                                linestyle="--", linewidth=1.1))
    ax.text(6.60, 1.36, r"sub-module resolution ($V_{\mathit{path}}$)"
                        "\nnot implemented, future work",
            fontsize=7.8, ha="center", va="center", style="italic", color=GREY)

    # ---- right: verified repair -----------------------------------------
    ax.add_patch(FancyBboxPatch((9.15, 2.30), 3.8, 3.68,
                                boxstyle="round,pad=0.012,rounding_size=0.05",
                                facecolor="#ffffff", edgecolor=DIFF_GRN_INK, linewidth=1.4))
    _code_block(ax, 9.25, 5.80, [
        ("+", "from langchain_milvus import Milvus"),
        ("+", "from langchain_milvus.function \\"),
        ("+", "     import BM25BuiltInFunction"),
        (" ", ""),
        ("+", "store = Milvus("),
        ("+", "    builtin_function="),
        ("+", "        BM25BuiltInFunction(),"),
        ("+", "    vector_field=[\"dense\","),
        ("+", "                  \"sparse\"])"),
    ], width=3.60)
    ax.text(11.05, 2.52, "every symbol resolves against PyPI",
            fontsize=7.9, style="italic", ha="center", color=DIFF_GRN_INK)

    # ---- orthogonal connectors ------------------------------------------
    arrow(ax, (4.05, 4.16), (4.70, 4.16), colour=NODE_EDGE)
    ax.text(4.38, 4.28, "extract", fontsize=7.4, ha="center", color=NODE_EDGE)

    # detection to repair: mitigation feeds the regenerated snippet forward
    arrow(ax, (8.50, 2.42), (8.85, 2.42), colour=ORANGE)
    arrow(ax, (8.85, 2.42), (8.85, 4.16), colour=ORANGE)
    arrow(ax, (8.85, 4.16), (9.15, 4.16), colour=ORANGE)
    ax.text(8.99, 4.34, "regenerate", fontsize=7.6, color=ORANGE, ha="left", va="bottom")

    # feedback loop back to the generator
    ax.add_patch(FancyArrowPatch((4.70, 2.42), (2.15, 2.30), arrowstyle="-|>",
                                 mutation_scale=13, linewidth=1.3, color=ORANGE,
                                 linestyle=(0, (4, 2)),
                                 connectionstyle="angle,angleA=180,angleB=90,rad=6"))
    ax.text(3.30, 1.88, "correction prompt to generator", fontsize=7.4,
            ha="center", color=ORANGE, style="italic")

    save(fig, "fig10_casestudy1.png", also_pdf=True)


# --------------------------------------------------------------- Figure 11
def case_study_2() -> None:
    """Temporal version extrapolation, and the security stage that rejects it."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.4, 5.8),
                                   gridspec_kw={"width_ratios": [1.02, 1]})

    # Official releases: newer version implies younger package, all mature.
    official = [("v60", 365), ("v65", 270), ("v70", 180), ("v72", 95)]
    versions = [v for v, _ in official] + ["v80"]
    ypos = {v: i for i, v in enumerate(versions)}

    ax1.scatter([age for _, age in official], [ypos[v] for v, _ in official],
                s=95, color=GREEN, zorder=3, label="Official stable release")
    for v, age in official:
        ax1.annotate(v, (age, ypos[v]), textcoords="offset points",
                     xytext=(10, -15), fontsize=9, color="#0b5c3f", fontweight="bold")

    ax1.scatter([3], [ypos["v80"]], s=175, marker="X", color=DIFF_RED_INK, zorder=3,
                label="Speculative package (attacker)")
    ax1.annotate("v80\nage < 72 h", (3, ypos["v80"]), textcoords="offset points",
                 xytext=(12, -4), fontsize=9, color=DIFF_RED_INK, fontweight="bold")

    ax1.annotate("", xy=(3, ypos["v80"]), xytext=(95, ypos["v72"]),
                 arrowprops={"arrowstyle": "-|>", "color": ORANGE, "linewidth": 2})
    ax1.text(170, 3.62, "temporal extrapolation\nv72 to v80", fontsize=8.5,
             color=ORANGE, fontweight="bold", ha="center")

    ax1.set_yticks(range(len(versions)))
    ax1.set_yticklabels(versions)
    ax1.set_ylim(-0.6, len(versions) - 0.4)
    ax1.invert_xaxis()
    ax1.set_xlabel("Package age at resolution time (days, newer to the right)")
    ax1.set_ylabel("Stripe-Go major version")
    ax1.set_title("(a) Release trajectory and the speculative namespace", fontsize=10.5)
    ax1.grid(alpha=0.3, zorder=0)
    ax1.legend(fontsize=8.5, loc="upper left", framealpha=0.95)

    ax2.set_xlim(0, 10.6)
    ax2.set_ylim(0, 10.6)
    ax2.axis("off")

    box(ax2, 1.15, 9.15, 7.3, 0.86, 'import "github.com/stripe/stripe-go/v80"',
        face=DIFF_RED_BG, edge=DIFF_RED_INK, fontsize=9.2)

    box(ax2, 1.15, 7.30, 7.3, 0.92,
        r"$V_{\mathit{exist}}$    HTTP 200, attacker repository resolves",
        face="#e8f6ef", edge=GREEN, fontsize=9.2)
    ax2.text(8.62, 7.76, "PASS", fontsize=10, fontweight="bold", color=GREEN,
             ha="left", va="center")

    box(ax2, 1.15, 5.25, 7.3, 1.16,
        r"$V_{\mathit{secure}}$    age $<$ 72 h, zero downloads," "\n"
        "signature mismatch, no advisory history",
        face=DIFF_RED_BG, edge=DIFF_RED_INK, fontsize=9.2)
    ax2.text(8.62, 5.83, "FAIL", fontsize=10, fontweight="bold", color=DIFF_RED_INK,
             ha="left", va="center")

    box(ax2, 1.95, 3.75, 5.7, 0.92,
        r"composite score $S_{\mathit{final}} = 0.08$" "\n"
        r"below threshold $\tau_{\mathit{secure}} = 0.70$",
        face="#ffffff", edge=INK, fontsize=9.4)

    ax2.text(8.62, 4.21, r"$V_{\mathit{relevant}}$ never runs" "\n" "(chain short-circuits)",
             fontsize=7.6, color=GREY, style="italic", ha="left", va="center")

    box(ax2, 1.15, 2.10, 7.3, 0.92,
        "Mitigation module    structured correction prompt",
        face="#fff4e2", edge=ORANGE, fontsize=9.2)

    box(ax2, 1.15, 0.35, 7.3, 0.86, "LLM generator",
        face="#eef2f7", edge=NODE_EDGE, fontsize=9.2)

    for y0, y1, col in [(9.15, 8.22, NODE_EDGE), (7.30, 6.41, DIFF_RED_INK),
                        (5.25, 4.67, DIFF_RED_INK), (3.75, 3.02, ORANGE)]:
        arrow(ax2, (4.80, y0), (4.80, y1), colour=col)

    # bold revert directive back to the generator
    ax2.add_patch(FancyArrowPatch((4.80, 2.10), (4.80, 1.21), arrowstyle="-|>",
                                  mutation_scale=20, linewidth=2.6,
                                  color=DIFF_RED_INK, zorder=5))
    ax2.text(5.05, 1.66, "directive: revert to v72", fontsize=9, fontweight="bold",
             color=DIFF_RED_INK, ha="left", va="center")

    ax2.set_title("(b) Verification path, blocked before installation", fontsize=11)

    fig.tight_layout()
    save(fig, "fig11_casestudy2.png", also_pdf=True)


def nlapi_sequence() -> None:
    """NL-API curation, with counts read from the released corpus."""
    recs = [json.loads(line) for line in
            io.open(DATA / "nl_api/nl_api_prompts.jsonl", encoding="utf-8")]
    n_inst = len(recs)
    n_distinct = len({r["prompt"] for r in recs})
    n_src = len({r["source"] for r in recs})

    fig, ax = plt.subplots(figsize=(11.5, 5.4))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 5.4)
    ax.axis("off")

    lanes = [(0.9, "Practitioner"), (3.5, f"Source APIs\n({n_src} sources)"),
             (6.6, "Cleaning module"), (9.9, "NL-API corpus")]
    for x, label in lanes:
        box(ax, x - 1.0, 4.35, 2.0, 0.68, label, face="#eaf2fb", edge=BLUE, fontsize=9)
        ax.plot([x, x], [0.55, 4.35], color="#bbbbbb", linewidth=1.0, zorder=0)

    steps = [
        (0.9, 3.5, 3.85, "CurateNicheDataset()"),
        (3.5, 6.6, 3.15, "raw issues and questions"),
    ]
    for x0, x1, y, label in steps:
        arrow(ax, (x0, y), (x1, y), colour=INK)
        ax.text((x0 + x1) / 2, y + 0.12, label, ha="center", fontsize=8.2)

    for y, label in [(2.55, "DeduplicateMinHash (Jaccard 0.85)"),
                     (1.95, "FilterComplexity (min_imports $\\geq$ 3)")]:
        ax.add_patch(FancyBboxPatch((6.75, y - 0.16), 3.0, 0.34,
                                    boxstyle="round,pad=0.006,rounding_size=0.02",
                                    facecolor="#ffffff", edgecolor=GREY, linewidth=1.0))
        ax.text(8.25, y, label, ha="center", va="center", fontsize=7.8)
    ax.text(6.72, 2.25, f"{n_distinct} distinct\nrequests", ha="right", va="center",
            fontsize=8.2, color=GREEN, fontweight="bold")

    arrow(ax, (6.6, 1.35), (9.9, 1.35), colour=GREEN)
    ax.text(8.25, 1.47, f"{n_inst:,} evaluation instances", ha="center",
            fontsize=8.5, fontweight="bold", color="#0b5c3f")

    box(ax, 8.9, 0.35, 2.0, 0.62,
        f"{n_inst:,} instances\n{n_distinct} distinct", face="#e8f6ef", edge=GREEN, fontsize=8.2)

    ax.set_title("NL-API dataset curation", fontsize=12, fontweight="bold", pad=6)
    save(fig, "fig_nlapi_sequence.png")


def main() -> None:
    print("Regenerating schematic manuscript figures at 300 DPI")
    annotation_protocol()
    case_study_1()
    case_study_2()
    nlapi_sequence()
    print("\nTargets:")
    for d in OUT_DIRS:
        print(f"  {d}")


if __name__ == "__main__":
    main()
