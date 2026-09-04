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
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

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


def save(fig, filename: str) -> None:
    for d in OUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        fig.savefig(d / filename, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {filename} to {len(OUT_DIRS)} directories")


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
def case_study_1() -> None:
    """Path analogy hallucination: caught at V_relevant, not at a sub-module stage."""
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    ax.text(1.95, 5.85, "LLM generated candidate", ha="center", fontsize=11, fontweight="bold")
    ax.text(6.25, 5.85, "HalluGuard verification chain", ha="center", fontsize=11, fontweight="bold")
    ax.text(10.55, 5.85, "Verified repair", ha="center", fontsize=11, fontweight="bold")

    ax.add_patch(FancyBboxPatch((0.15, 2.15), 3.6, 3.4,
                                boxstyle="round,pad=0.01,rounding_size=0.04",
                                facecolor="#fdecea", edgecolor=RED, linewidth=1.3))
    ax.text(0.32, 5.28, "from langchain_milvus.retrievers import \\\n"
                        "    MilvusCollectionHybridSearchRetriever",
            fontsize=7.4, family="monospace", va="top", color="#8a1c10")
    ax.text(0.32, 4.35, "retriever = MilvusCollectionHybrid\\\n"
                        "    SearchRetriever(\n"
                        "        collection=collection,\n"
                        "        anns_fields=[\"dense\", \"sparse\"],\n"
                        "        top_k=5)",
            fontsize=7.4, family="monospace", va="top", color="#333333")
    ax.text(1.95, 2.42, "sub-module .retrievers does not exist",
            fontsize=8, style="italic", ha="center", color=RED)

    stages = [
        ("$V_{exist}$", "PyPI: HTTP 200\nparent registered", "PASS", GREEN, "#e8f6ef"),
        ("$V_{secure}$", "no advisory,\nestablished package", "PASS", GREEN, "#e8f6ef"),
        ("$V_{relevant}$", "cannot satisfy\nthe stated request", "FAIL", RED, "#fdecea"),
    ]
    y = 4.55
    for name, detail, verdict, colour, face in stages:
        box(ax, 4.55, y, 3.4, 0.88, "", face=face, edge=colour)
        ax.text(4.75, y + 0.58, name, fontsize=10, fontweight="bold", va="center")
        ax.text(4.75, y + 0.27, detail, fontsize=7.6, va="center", color="#333333")
        ax.text(7.72, y + 0.44, verdict, fontsize=9, fontweight="bold",
                color=colour, ha="right", va="center")
        if y > 2.8:
            arrow(ax, (6.25, y), (6.25, y - 0.27), colour=GREY)
        y -= 1.15

    box(ax, 4.55, 1.28, 3.4, 0.72, "Mitigation module\nstructured correction prompt",
        face="#fff4e2", edge=ORANGE, fontsize=8.5)
    arrow(ax, (6.25, 2.25), (6.25, 2.03), colour=RED)

    ax.add_patch(FancyBboxPatch((4.55, 0.30), 3.4, 0.72,
                                boxstyle="round,pad=0.01,rounding_size=0.03",
                                facecolor="#f4f4f4", edgecolor="#bbbbbb",
                                linestyle="--", linewidth=1.1))
    ax.text(6.25, 0.66, "sub-module resolution ($V_{path}$)\nout of scope, future work",
            fontsize=7.8, ha="center", va="center", style="italic", color=GREY)

    ax.add_patch(FancyBboxPatch((8.75, 2.15), 3.6, 3.4,
                                boxstyle="round,pad=0.01,rounding_size=0.04",
                                facecolor="#e8f6ef", edgecolor=GREEN, linewidth=1.3))
    ax.text(8.92, 5.28, "from langchain_milvus import Milvus\n"
                        "from langchain_milvus.function \\\n"
                        "    import BM25BuiltInFunction",
            fontsize=7.4, family="monospace", va="top", color="#0b5c3f")
    ax.text(8.92, 4.20, "store = Milvus(\n"
                        "    builtin_function=\n"
                        "        BM25BuiltInFunction(),\n"
                        "    vector_field=[\"dense\",\n"
                        "                  \"sparse\"])",
            fontsize=7.4, family="monospace", va="top", color="#333333")
    ax.text(10.55, 2.42, "all symbols resolved against PyPI",
            fontsize=8, style="italic", ha="center", color=GREEN)

    arrow(ax, (3.75, 3.9), (4.55, 3.9), colour=GREY)
    arrow(ax, (7.95, 1.64), (8.60, 1.64), colour=ORANGE)
    arrow(ax, (8.60, 1.64), (8.60, 3.85), colour=ORANGE)
    arrow(ax, (8.60, 3.85), (8.75, 3.85), colour=ORANGE)
    ax.text(8.00, 1.36, "regenerate", fontsize=7.8, color=ORANGE)

    save(fig, "fig10_casestudy1.png")


# --------------------------------------------------------------- Figure 11
def case_study_2() -> None:
    """Temporal version extrapolation with a correctly ordered version axis."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.4),
                                   gridspec_kw={"width_ratios": [1.05, 1]})

    # Official releases: newer version implies younger package, all mature.
    official = [("v60", 365), ("v65", 270), ("v70", 180), ("v72", 95)]
    versions = [v for v, _ in official] + ["v80"]
    ypos = {v: i for i, v in enumerate(versions)}

    ax1.scatter([age for _, age in official], [ypos[v] for v, _ in official],
                s=95, color=GREEN, zorder=3, label="Official stable release")
    for v, age in official:
        ax1.annotate(v, (age, ypos[v]), textcoords="offset points",
                     xytext=(10, -15), fontsize=9, color="#0b5c3f", fontweight="bold")

    ax1.scatter([3], [ypos["v80"]], s=150, marker="X", color=RED, zorder=3,
                label="Speculative package (attacker)")
    ax1.annotate("v80\nage < 72 h", (3, ypos["v80"]), textcoords="offset points",
                 xytext=(12, -4), fontsize=9, color="#8a1c10", fontweight="bold")

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

    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis("off")
    box(ax2, 0.6, 8.2, 8.8, 1.0, 'import "github.com/stripe/stripe-go/v80"',
        face="#fdecea", edge=RED, fontsize=9)
    box(ax2, 1.5, 6.3, 7.0, 1.0, "$V_{exist}$   HTTP 200, attacker repository active",
        face="#e8f6ef", edge=GREEN, fontsize=9)
    ax2.text(9.0, 6.8, "PASS", fontsize=9.5, fontweight="bold", color=GREEN,
             ha="right", va="center")
    box(ax2, 1.5, 4.4, 7.0, 1.0,
        "$V_{secure}$   age < 72 h, zero downloads,\nsignature mismatch",
        face="#fdecea", edge=RED, fontsize=9)
    ax2.text(9.0, 4.9, "FAIL", fontsize=9.5, fontweight="bold", color=RED,
             ha="right", va="center")
    box(ax2, 2.3, 2.9, 5.4, 0.85,
        "$S_{final} = 0.08 \\; < \\; \\tau_{secure} = 0.70$",
        face="#ffffff", edge=INK, fontsize=9.5, weight="bold")
    box(ax2, 1.5, 1.0, 7.0, 1.0,
        "Mitigation   revert import to verified v72", face="#fff4e2",
        edge=ORANGE, fontsize=9)

    for y0, y1, col in [(8.2, 7.3, GREY), (6.3, 5.4, RED), (4.4, 3.75, RED),
                        (2.9, 2.0, ORANGE)]:
        arrow(ax2, (5.0, y0), (5.0, y1), colour=col)
    ax2.set_title("(b) Verification path, blocked before installation", fontsize=10.5)

    fig.tight_layout()
    save(fig, "fig11_casestudy2.png")


def main() -> None:
    print("Regenerating schematic manuscript figures at 300 DPI")
    annotation_protocol()
    case_study_1()
    case_study_2()
    print("\nTargets:")
    for d in OUT_DIRS:
        print(f"  {d}")


if __name__ == "__main__":
    main()
