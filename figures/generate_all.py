"""
HalluGuard Paper – Publication-Quality Figures
300 DPI · Okabe-Ito palette · Arial font · booktabs aesthetic
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ── Global style ──────────────────────────────────────────────────────────────
DPI      = 300
FONT     = 'DejaVu Sans'          # closest to Arial in most LaTeX setups
OKI      = dict(                   # Okabe-Ito
    blue   = '#0072B2',
    orange = '#E69F00',
    green  = '#009E73',
    red    = '#D55E00',
    purple = '#CC79A7',
    cyan   = '#56B4E9',
    yellow = '#F0E442',
    black  = '#000000',
)
GREY_BG  = '#F7F7F7'
GREY_BOR = '#D9D9D9'
NAVY     = '#1F3864'
AMBER    = '#E69F00'

plt.rcParams.update({
    'font.family'      : FONT,
    'font.size'        : 13,
    'axes.titlesize'   : 15,
    'axes.labelsize'   : 13,
    'xtick.labelsize'  : 12,
    'ytick.labelsize'  : 12,
    'legend.fontsize'  : 12,
    'figure.dpi'       : DPI,
    'savefig.dpi'      : DPI,
    'savefig.bbox'     : 'tight',
    'savefig.pad_inches': 0.15,
    'axes.spines.top'  : False,
    'axes.spines.right': False,
    'axes.grid'        : True,
    'grid.color'       : GREY_BOR,
    'grid.linewidth'   : 0.6,
    'axes.edgecolor'   : '#888888',
})

OUT = '/home/claude/figures'

# ═══════════════════════════════════════════════════════════════════════════════
# Helper: header-bar module box
# ═══════════════════════════════════════════════════════════════════════════════
def header_box(ax, x, y, w, h, title, body_lines, hdr_color=NAVY,
               body_color=GREY_BG, title_color='white', body_text_color='#222',
               fontsize=11, title_frac=0.28):
    """Draw a professional module box with coloured header bar."""
    hh = h * title_frac
    bh = h - hh
    # body
    ax.add_patch(FancyBboxPatch((x, y), w, bh, boxstyle='round,pad=0.01',
                                fc=body_color, ec=GREY_BOR, lw=1.0, zorder=2))
    # header
    ax.add_patch(FancyBboxPatch((x, y+bh), w, hh, boxstyle='round,pad=0.01',
                                fc=hdr_color, ec=hdr_color, lw=0, zorder=3))
    # title
    ax.text(x+w/2, y+bh+hh/2, title, ha='center', va='center',
            color=title_color, fontsize=fontsize, fontweight='bold', zorder=4)
    # body text
    n = len(body_lines)
    for i, line in enumerate(body_lines):
        yt = y + bh*(1 - (i+0.7)/max(n,1))
        ax.text(x+w/2, yt, line, ha='center', va='center',
                color=body_text_color, fontsize=fontsize-1, zorder=4)

def h_arrow(ax, x0, y, x1, color='#333', lw=2.0, label=None, fontsize=10):
    """Strictly horizontal arrow."""
    ax.annotate('', xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw))
    if label:
        xm = (x0+x1)/2
        ax.text(xm, y+0.025, label, ha='center', va='bottom',
                fontsize=fontsize, color=color)

def v_arrow(ax, x, y0, y1, color='#333', lw=2.0, label=None, fontsize=10):
    ax.annotate('', xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw))
    if label:
        ym = (y0+y1)/2
        ax.text(x+0.02, ym, label, ha='left', va='center',
                fontsize=fontsize, color=color)


# ═══════════════════════════════════════════════════════════════════════════════
# FIG 1 – Slopsquatting Lifecycle (System Diagram)
# ═══════════════════════════════════════════════════════════════════════════════
def fig1():
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 14); ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_facecolor('white')

    col_w = 3.8; gap = 0.7
    cols = [0.3, 0.3+col_w+gap, 0.3+2*(col_w+gap)]
    col_colors = [OKI['red'], OKI['orange'], OKI['green']]
    col_titles = ['ATTACKER', 'LLM (AI Code Generator)', 'DEVELOPER']

    # column header strips
    for cx, cc, ct in zip(cols, col_colors, col_titles):
        ax.add_patch(Rectangle((cx, 5.2), col_w, 0.6, fc=cc, alpha=0.85,
                                zorder=2, clip_on=False))
        ax.text(cx+col_w/2, 5.5, ct, ha='center', va='center',
                color='white', fontsize=13, fontweight='bold', zorder=3)

    # ── Column 1: ATTACKER ───────────────────────────────────────────────────
    c = cols[0]
    header_box(ax, c, 3.8, col_w, 1.1, 'Step 1 · Register',
               ['Registers hallucinated', 'package name on PyPI/npm',
                'with malicious payload'],
               hdr_color=OKI['red'])
    header_box(ax, c, 2.4, col_w, 1.1, 'Hallucinated Name',
               ['e.g.  starlette-reverse-proxy',
                'scipy-plotting  ·  http-fetch-plus'],
               hdr_color='#8B0000', fontsize=10)
    header_box(ax, c, 1.0, col_w, 1.1, 'Malicious Payload',
               ['Exfiltrates credentials',
                'Installs backdoor · Corrupts build'],
               hdr_color='#8B0000', fontsize=10)

    # ── Column 2: LLM ────────────────────────────────────────────────────────
    c = cols[1]
    header_box(ax, c, 3.8, col_w, 1.1, 'Step 2 · Hallucinate',
               ['LLM generates code with', 'high-confidence import of',
                'a non-existent package'],
               hdr_color=OKI['orange'])
    header_box(ax, c, 2.4, col_w, 1.1, 'Generated Code Snippet',
               ['import starlette-reverse-proxy',
                'Syntactically valid · Semantically wrong'],
               hdr_color='#7B5200', fontsize=10)
    header_box(ax, c, 1.0, col_w, 1.1, 'Slopsquatting Vector',
               ['Attacker pre-maps LLM probability',
                'distribution → predicts names'],
               hdr_color='#7B5200', fontsize=10)

    # ── Column 3: DEVELOPER ──────────────────────────────────────────────────
    c = cols[2]
    header_box(ax, c, 3.8, col_w, 1.1, 'Step 3 · Install',
               ['Developer blindly trusts AI output',
                'runs  pip install  ·  npm install'],
               hdr_color=OKI['green'])
    header_box(ax, c, 2.4, col_w, 1.1, 'System Compromised',
               ['Malicious package executes',
                'Credentials stolen · Supply chain broken'],
               hdr_color='#004D30', fontsize=10)
    header_box(ax, c, 1.0, col_w, 1.1, 'HalluGuard Intercept ✓',
               ['CoV-RAG detects hallucination',
                'Blocks install · Proposes safe alternative'],
               hdr_color=OKI['cyan'], body_color='#E8F8F5', fontsize=10)

    # ── Horizontal arrows ─────────────────────────────────────────────────────
    ax1_right = cols[0]+col_w; ax2_left = cols[1]; cx1 = ax1_right+gap/2
    ax2_right = cols[1]+col_w; ax3_left = cols[2]; cx2 = ax2_right+gap/2

    for yr, lbl, clr in [(4.35, 'Predicts hallucination\npattern', OKI['red']),
                          (2.95, 'Registers matching\npackage name', OKI['red'])]:
        h_arrow(ax, ax1_right+0.05, yr, ax2_left-0.05, color=clr, lw=2.2)
        ax.text(cx1, yr+0.12, lbl, ha='center', va='bottom',
                fontsize=9, color=clr, style='italic')

    for yr, lbl, clr in [(4.35, 'AI suggests package\n(hallucination)', OKI['orange']),
                          (2.95, 'pip install →\nmalware installed', OKI['red'])]:
        h_arrow(ax, ax2_right+0.05, yr, ax3_left-0.05, color=clr, lw=2.2)
        ax.text(cx2, yr+0.12, lbl, ha='center', va='bottom',
                fontsize=9, color=clr, style='italic')

    # Green interception arrow
    ax.annotate('', xy=(cols[2]+col_w/2, 1.55), xytext=(cols[2]+col_w/2, 1.0),
                arrowprops=dict(arrowstyle='->', color=OKI['green'], lw=2.5))

    # Title
    ax.text(7, 5.92,
            'Figure 1 · Slopsquatting Lifecycle in AI-Assisted (Vibe Coding) Environments',
            ha='center', va='center', fontsize=13, fontweight='bold', color=NAVY)
    ax.text(7, 5.72,
            'Subtitle: How package hallucination creates the slopsquatting attack surface',
            ha='center', va='center', fontsize=10, color='#555', style='italic')

    # Legend
    legend_els = [mpatches.Patch(fc=OKI['red'],    label='Attack stage (red)'),
                  mpatches.Patch(fc=OKI['orange'],  label='Vulnerability stage (amber)'),
                  mpatches.Patch(fc=OKI['green'],   label='Mitigation / HalluGuard (green)'),
                  mpatches.Patch(fc=OKI['cyan'],    label='HalluGuard interception')]
    ax.legend(handles=legend_els, loc='lower center', ncol=4,
              fontsize=9, frameon=True, framealpha=0.9,
              bbox_to_anchor=(0.5, -0.02))

    plt.tight_layout()
    plt.savefig(f'{OUT}/fig1_system_diagram.png', dpi=DPI, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print('✓ Fig 1 saved')

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 2 – HalluGuard Architecture Diagram
# ═══════════════════════════════════════════════════════════════════════════════
def fig2():
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_xlim(0, 15); ax.set_ylim(0, 8)
    ax.axis('off'); ax.set_facecolor('white')

    # Outer wrapper frame
    ax.add_patch(FancyBboxPatch((0.2, 0.3), 14.6, 7.4,
                                boxstyle='round,pad=0.1',
                                fc='#EEF4FB', ec=NAVY, lw=2, zorder=1))
    ax.text(7.5, 7.55, 'HalluGuard Middleware Wrapper', ha='center',
            fontsize=14, fontweight='bold', color=NAVY)

    # ── User Prompt (left) ───────────────────────────────────────────────────
    header_box(ax, 0.5, 3.0, 2.2, 1.6, 'User Prompt  P',
               ['Natural-language', 'coding request'],
               hdr_color=OKI['blue'], fontsize=11)

    # ── LLM Generator ────────────────────────────────────────────────────────
    header_box(ax, 3.2, 3.0, 2.5, 1.6, 'LLM Generator',
               ['gpt-4-turbo', 'Produces C_g'],
               hdr_color=OKI['blue'], fontsize=11)

    # ── CoV Core (3 stages) ──────────────────────────────────────────────────
    cov_x = 6.3; cov_y = 0.6; cov_w = 5.8; cov_h = 6.0
    ax.add_patch(FancyBboxPatch((cov_x, cov_y), cov_w, cov_h,
                                boxstyle='round,pad=0.1',
                                fc='#E8EBF4', ec=NAVY, lw=1.5, zorder=1))
    ax.text(cov_x+cov_w/2, cov_y+cov_h+0.15,
            'CoV Core  —  Chain-of-Verification',
            ha='center', fontsize=12, fontweight='bold', color=NAVY)

    stage_y = [5.0, 3.3, 1.6]
    stage_labels = ['V_exist  ·  Existence Verification',
                    'V_secure  ·  Security Posture',
                    'V_relevant  ·  Contextual Relevance']
    stage_bodies = [
        ['PyPI / npm  GET request', '200 OK → pass  ·  404 → fail'],
        ['OSV + S_rep + Levenshtein', 'S_final ≥ 0.70 → pass'],
        ['Cross-model LLM judge', 'Yes → pass  ·  No → fail'],
    ]
    stage_colors = [OKI['blue'], OKI['orange'], OKI['green']]
    for sy, sl, sb, sc in zip(stage_y, stage_labels, stage_bodies, stage_colors):
        header_box(ax, cov_x+0.3, sy, cov_w-0.6, 1.4, sl, sb,
                   hdr_color=sc, fontsize=10)

    # ── Cross-model judge box ─────────────────────────────────────────────────
    header_box(ax, 9.0, 2.0, 2.5, 1.0, 'Cross-Model Judge',
               ['Claude 3.5 Sonnet', '(generator ≠ judge)'],
               hdr_color=OKI['green'], body_color='#E8F8F5', fontsize=9)
    # dashed arrow from V_relevant to judge
    ax.annotate('', xy=(10.25, 2.4), xytext=(10.25, 1.6+0.5),
                arrowprops=dict(arrowstyle='<->', color=OKI['green'],
                                lw=1.5, linestyle='dashed'))

    # ── Mitigation Module ─────────────────────────────────────────────────────
    header_box(ax, 3.2, 0.6, 2.5, 1.6, 'Mitigation Module',
               ['Correction prompt', 'Triggers regeneration'],
               hdr_color=AMBER, body_color='#FFF8E7', fontsize=11)

    # ── Verified Output ───────────────────────────────────────────────────────
    header_box(ax, 12.4, 3.0, 2.2, 1.6, 'Verified C_f',
               ['All V checks pass', 'Safe code to developer'],
               hdr_color=OKI['green'], fontsize=11)

    # ── Arrows ────────────────────────────────────────────────────────────────
    # P → LLM
    h_arrow(ax, 2.7, 3.8, 3.2, color=OKI['blue'], lw=2.2, label='P', fontsize=10)
    # LLM → CoV
    h_arrow(ax, 5.7, 3.8, 6.3, color=OKI['blue'], lw=2.2, label='C_g', fontsize=10)
    # between CoV stages
    for y_from, y_to in [(5.0, 4.7), (3.3, 3.0)]:
        v_arrow(ax, 9.2, y_from, y_to, color=NAVY, lw=1.8, label='pass', fontsize=9)
    # CoV → output
    h_arrow(ax, 12.1, 3.8, 12.4, color=OKI['green'], lw=2.2, label='C_f', fontsize=10)
    # fail → mitigation
    ax.annotate('', xy=(4.45, 2.2), xytext=(6.3, 2.2),
                arrowprops=dict(arrowstyle='->', color=OKI['red'], lw=2.0))
    ax.text(5.4, 2.35, 'fail → mitigation', ha='center', fontsize=9,
            color=OKI['red'], style='italic')
    # mitigation → LLM (loop)
    ax.annotate('', xy=(4.45, 3.0), xytext=(4.45, 2.2),
                arrowprops=dict(arrowstyle='->', color=AMBER, lw=2.0))
    ax.text(3.9, 2.6, 'regenerate', ha='right', fontsize=9, color=AMBER, style='italic')

    # Legend
    legend_els = [mpatches.Patch(fc=OKI['blue'],   label='Generation (blue)'),
                  mpatches.Patch(fc=NAVY,           label='CoV Core (navy)'),
                  mpatches.Patch(fc=AMBER,          label='Mitigation Module (amber)'),
                  mpatches.Patch(fc=OKI['green'],   label='Cross-model Judge / Output (green)')]
    ax.legend(handles=legend_els, loc='lower center', ncol=4,
              fontsize=9, frameon=True, framealpha=0.9,
              bbox_to_anchor=(0.5, -0.02))

    ax.text(7.5, 7.85,
            'Figure 2 · HalluGuard System Architecture',
            ha='center', fontsize=14, fontweight='bold', color=NAVY)

    plt.tight_layout()
    plt.savefig(f'{OUT}/fig2_architecture.png', dpi=DPI, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print('✓ Fig 2 saved')

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 3 – V_exist Flow Diagram
# ═══════════════════════════════════════════════════════════════════════════════
def fig3():
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_xlim(0, 13); ax.set_ylim(0, 6)
    ax.axis('off'); ax.set_facecolor('white')

    ax.text(6.5, 5.75, 'Figure 3 · V_exist Existence Verification Process',
            ha='center', fontsize=14, fontweight='bold', color=NAVY)

    # boxes left-to-right
    boxes = [
        (0.3,  2.2, 2.0, 1.6, 'Dependency\nExtracted',
         ['d_i from AST', 'parser output'], OKI['blue']),
        (3.0,  2.2, 2.4, 1.6, 'Registry API\nRequest',
         ['GET /pypi/{pkg}/json', 'GET /npm/{pkg}'], OKI['blue']),
        (6.2,  2.2, 2.4, 1.6, 'Response\nHandler',
         ['Parse HTTP status', 'code and body'], OKI['orange']),
        (9.5,  3.6, 2.4, 1.4, '200 OK → PASS',
         ['Package exists', 'Proceed to V_secure'], OKI['green']),
        (9.5,  1.0, 2.4, 1.4, '404 Not Found → FAIL',
         ['Hallucination confirmed', 'Trigger Mitigation'], OKI['red']),
    ]

    for bx, by, bw, bh, title, body, bc in boxes:
        header_box(ax, bx, by, bw, bh, title, body, hdr_color=bc, fontsize=10)

    # horizontal arrows
    h_arrow(ax, 2.3, 3.0, 3.0, color=OKI['blue'], lw=2.0)
    h_arrow(ax, 5.4, 3.0, 6.2, color=OKI['blue'], lw=2.0)

    # decision arrow to pass
    ax.annotate('', xy=(9.5, 4.3), xytext=(8.6, 4.3),
                arrowprops=dict(arrowstyle='->', color=OKI['green'], lw=2.0))
    ax.text(9.05, 4.45, '200 OK', ha='center', fontsize=9, color=OKI['green'])

    # decision arrow to fail
    ax.annotate('', xy=(9.5, 1.7), xytext=(8.6, 1.7),
                arrowprops=dict(arrowstyle='->', color=OKI['red'], lw=2.0))
    ax.text(9.05, 1.85, '404', ha='center', fontsize=9, color=OKI['red'])

    # branching from response handler
    ax.annotate('', xy=(8.6, 4.3), xytext=(7.4, 4.3),
                arrowprops=dict(arrowstyle='->', color=OKI['green'], lw=1.5))
    ax.annotate('', xy=(7.4, 3.8), xytext=(7.4, 4.3),
                arrowprops=dict(arrowstyle='-', color='#555', lw=1.2))
    ax.annotate('', xy=(7.4, 1.7), xytext=(7.4, 2.2),
                arrowprops=dict(arrowstyle='->', color=OKI['red'], lw=1.5))
    ax.annotate('', xy=(7.4, 1.7), xytext=(8.6, 1.7),
                arrowprops=dict(arrowstyle='-', color='#555', lw=1.2))

    # Latency annotation
    ax.text(4.2, 1.4, '⏱  Avg. latency: 85 ms ± 18 ms',
            ha='center', fontsize=10, color='#555', style='italic',
            bbox=dict(boxstyle='round,pad=0.3', fc='#F0F8FF', ec=OKI['cyan'], lw=1))

    plt.tight_layout()
    plt.savefig(f'{OUT}/fig3_vexist_flow.png', dpi=DPI, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print('✓ Fig 3 saved')

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 4 – V_secure Composite Score Pipeline
# ═══════════════════════════════════════════════════════════════════════════════
def fig4():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14); ax.set_ylim(0, 7)
    ax.axis('off'); ax.set_facecolor('white')

    ax.text(7, 6.75, 'Figure 4 · V_secure Composite Security Score Pipeline',
            ha='center', fontsize=14, fontweight='bold', color=NAVY)

    # Input
    header_box(ax, 0.3, 2.8, 2.0, 1.4, 'Package  d_i',
               ['name + version', 'from V_exist'], hdr_color=OKI['blue'], fontsize=10)

    # 3 parallel branches
    branch_defs = [
        (4.0, 5.2, 'Vulnerability Scan\nS_vuln', ['Query OSV database', 'GitHub Advisory DB',
         'Score: 0 / 0.5 / 1'], OKI['red'], 'w = 0.6', 0.6),
        (4.0, 3.3, 'Reputation Analysis\nS_rep', ['Query libraries.io API', 'Age · Downloads',
         'Log-normalised [0,1]'], OKI['orange'], 'w = 0.2', 0.2),
        (4.0, 1.4, 'Typosquatting Detect.\nS_typo', ['Levenshtein vs top-5000', 'Similarity score [0,1]',
         'Subtracted (risk signal)'], OKI['purple'], 'w = 0.2', 0.2),
    ]

    for bx, by, title, body, bc, wlbl, wval in branch_defs:
        header_box(ax, bx, by, 3.2, 1.5, title, body, hdr_color=bc, fontsize=9)
        # weight badge
        ax.add_patch(FancyBboxPatch((bx+3.2, by+0.5), 0.7, 0.5,
                                    boxstyle='round,pad=0.05',
                                    fc=bc, ec='none', alpha=0.85, zorder=3))
        ax.text(bx+3.55, by+0.75, wlbl, ha='center', va='center',
                color='white', fontsize=9, fontweight='bold', zorder=4)
        # arrow from input
        ax.annotate('', xy=(bx, by+0.75),
                    xytext=(2.3, 3.5),
                    arrowprops=dict(arrowstyle='->', color=bc, lw=1.8,
                                   connectionstyle='arc3,rad=0'))

    # Weighted sum box
    header_box(ax, 8.6, 2.8, 2.4, 1.4, 'Weighted Sum\nS_final',
               ['0.6·S_vuln + 0.2·S_rep', '− 0.2·S_typo', 'clamp ≥ 0'],
               hdr_color=NAVY, fontsize=9)

    # Arrows from branches to sum
    for by_s in [5.95, 4.05, 2.15]:
        ax.annotate('', xy=(8.6, 3.5), xytext=(7.9, by_s),
                    arrowprops=dict(arrowstyle='->', color=NAVY, lw=1.5,
                                   connectionstyle='arc3,rad=0'))

    # Threshold decision
    header_box(ax, 11.5, 3.6, 2.1, 1.1, 'S_final ≥ τ = 0.70?',
               ['τ determined by grid search', '(F1-optimal)'], hdr_color=NAVY, fontsize=9)
    h_arrow(ax, 11.0, 3.5, 11.5, color=NAVY, lw=2.0)

    # Pass / Fail
    header_box(ax, 11.5, 1.8, 2.1, 1.0, 'PASS → V_relevant',
               ['Proceed to contextual', 'relevance check'], hdr_color=OKI['green'], fontsize=9)
    header_box(ax, 11.5, 0.5, 2.1, 1.0, 'FAIL → Mitigation',
               ['Block package', 'Trigger regeneration'], hdr_color=OKI['red'], fontsize=9)

    v_arrow(ax, 12.55, 3.6, 2.8, color=OKI['green'], lw=1.8)
    v_arrow(ax, 12.55, 1.8, 1.5, color=OKI['red'], lw=1.8)
    ax.text(12.7, 2.3, 'Yes', color=OKI['green'], fontsize=10, fontweight='bold')
    ax.text(12.7, 1.65, 'No', color=OKI['red'], fontsize=10, fontweight='bold')

    # Legend
    legend_els = [mpatches.Patch(fc=OKI['red'],    label='S_vuln – Vulnerability (w=0.6)'),
                  mpatches.Patch(fc=OKI['orange'],  label='S_rep – Reputation (w=0.2)'),
                  mpatches.Patch(fc=OKI['purple'],  label='S_typo – Typosquatting (w=0.2, subtracted)'),
                  mpatches.Patch(fc=NAVY,           label='Weighted aggregation & threshold')]
    ax.legend(handles=legend_els, loc='lower center', ncol=4,
              fontsize=9, frameon=True, framealpha=0.9,
              bbox_to_anchor=(0.5, -0.02))

    plt.tight_layout()
    plt.savefig(f'{OUT}/fig4_vsecure_pipeline.png', dpi=DPI, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print('✓ Fig 4 saved')

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 5 – V_relevant Contextual Verification
# ═══════════════════════════════════════════════════════════════════════════════
def fig5():
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 14); ax.set_ylim(0, 6)
    ax.axis('off'); ax.set_facecolor('white')

    ax.text(7, 5.75, 'Figure 5 · V_relevant Contextual Relevance Verification',
            ha='center', fontsize=14, fontweight='bold', color=NAVY)

    # Inputs
    header_box(ax, 0.3, 3.8, 2.2, 1.4, 'Original Prompt  P',
               ['Developer\'s natural-', 'language request'], hdr_color=OKI['blue'], fontsize=10)
    header_box(ax, 0.3, 2.0, 2.2, 1.4, 'Package  d_i',
               ['Passed V_exist &', 'V_secure checks'], hdr_color=OKI['orange'], fontsize=10)

    # Prompt construction
    header_box(ax, 3.4, 2.8, 2.8, 1.6, 'Prompt Constructor',
               ['Builds structured judge query:', '"Is {pkg} relevant for {P}?"',
                'Answer: Yes or No only'],
               hdr_color=NAVY, fontsize=9)

    ax.annotate('', xy=(3.4, 3.6), xytext=(2.5, 4.5),
                arrowprops=dict(arrowstyle='->', color=OKI['blue'], lw=2.0))
    ax.annotate('', xy=(3.4, 3.3), xytext=(2.5, 2.7),
                arrowprops=dict(arrowstyle='->', color=OKI['orange'], lw=2.0))

    # Generator box
    header_box(ax, 7.0, 4.2, 2.4, 1.2, 'Code Generator',
               ['GPT-4-Turbo', '(generates C_g)'], hdr_color=OKI['blue'], fontsize=10)

    # Cross-model judge (different model!)
    header_box(ax, 7.0, 2.4, 2.4, 1.4, '⚖  Cross-Model Judge',
               ['Claude 3.5 Sonnet', 'Generator ≠ Judge', 'Prevents intra-model bias'],
               hdr_color=OKI['green'], body_color='#E8F8F5', fontsize=9)

    # Arrow from constructor to judge
    h_arrow(ax, 6.2, 3.3, 7.0, color=NAVY, lw=2.0, label='Structured query', fontsize=9)

    # ≠ badge
    ax.text(8.2, 3.7, '≠', ha='center', va='center', fontsize=22,
            color=OKI['red'], fontweight='bold')
    ax.text(8.2, 3.5, '(different model)', ha='center', fontsize=8, color=OKI['red'])

    # Decision outputs
    header_box(ax, 10.4, 4.2, 2.8, 1.2, 'Judge → YES',
               ['Package is relevant', 'V_relevant = True → PASS'], hdr_color=OKI['green'], fontsize=10)
    header_box(ax, 10.4, 2.4, 2.8, 1.2, 'Judge → NO',
               ['Package is irrelevant', 'V_relevant = False → FAIL'], hdr_color=OKI['red'], fontsize=10)

    h_arrow(ax, 9.4, 4.8, 10.4, color=OKI['green'], lw=2.0)
    h_arrow(ax, 9.4, 3.0, 10.4, color=OKI['red'], lw=2.0)
    ax.annotate('', xy=(9.4, 4.8), xytext=(9.4, 3.8),
                arrowprops=dict(arrowstyle='-', color='#555', lw=1.2))
    ax.annotate('', xy=(9.4, 3.0), xytext=(9.4, 2.4+0.7),
                arrowprops=dict(arrowstyle='-', color='#555', lw=1.2))

    # Fail → Mitigation arrow
    ax.annotate('', xy=(5.0, 1.5), xytext=(10.4, 1.5),
                arrowprops=dict(arrowstyle='->', color=OKI['red'], lw=2.0))
    ax.text(7.7, 1.6, '→ Mitigation Module triggered', ha='center',
            fontsize=9, color=OKI['red'], style='italic')

    # Bias prevention annotation
    ax.add_patch(FancyBboxPatch((6.8, 1.0), 5.8, 0.8,
                                boxstyle='round,pad=0.1',
                                fc='#E8F8F5', ec=OKI['green'], lw=1.2, zorder=2))
    ax.text(9.7, 1.4,
            '⚡ Cross-model design: GPT-4 generates code · Claude 3.5 judges relevance\n'
            'Same-model verification inflates F1 by +3.2 pp (p < 0.01)',
            ha='center', va='center', fontsize=9, color='#004D30', zorder=3)

    legend_els = [mpatches.Patch(fc=OKI['blue'],   label='Code generator (GPT-4)'),
                  mpatches.Patch(fc=OKI['green'],   label='Cross-model judge (Claude 3.5)'),
                  mpatches.Patch(fc=OKI['red'],     label='Fail → Mitigation'),
                  mpatches.Patch(fc=NAVY,           label='Prompt constructor')]
    ax.legend(handles=legend_els, loc='lower center', ncol=4,
              fontsize=9, frameon=True, framealpha=0.9,
              bbox_to_anchor=(0.5, -0.02))

    plt.tight_layout()
    plt.savefig(f'{OUT}/fig5_vrelevant_flow.png', dpi=DPI, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print('✓ Fig 5 saved')

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 7 – Latency Bar Chart
# ═══════════════════════════════════════════════════════════════════════════════
def fig7():
    stages = ['V_exist\n(Registry API)', 'V_secure\n(OSV + Reputation)',
              'V_relevant\n(LLM Judge)', 'Total\nOverhead']
    means  = [85, 110, 90, 285]
    sds    = [18,  24, 21,  42]
    colors = [OKI['blue'], OKI['orange'], OKI['green'], NAVY]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(stages))
    bars = ax.bar(x, means, color=colors, width=0.55, zorder=3,
                  edgecolor='white', linewidth=0.5,
                  yerr=sds, capsize=7, error_kw=dict(lw=2, color='#333'))

    # value labels
    for bar, m, s in zip(bars, means, sds):
        ax.text(bar.get_x()+bar.get_width()/2, m+s+6,
                f'{m} ms\n±{s}', ha='center', va='bottom',
                fontsize=11, fontweight='bold', color='#222')

    ax.set_xticks(x); ax.set_xticklabels(stages, fontsize=12)
    ax.set_ylabel('Added Latency (ms)', fontsize=13)
    ax.set_ylim(0, 360)
    ax.set_title('Figure 7 · HalluGuard Pipeline Latency Overhead\n(N = 576,000 snippets)',
                 fontsize=13, fontweight='bold', color=NAVY, pad=10)
    ax.axhline(285, color=NAVY, lw=1.5, linestyle='--', alpha=0.6, zorder=2)
    ax.text(3.4, 290, 'Total: 285 ms', color=NAVY, fontsize=10, style='italic')

    # annotation box
    ax.text(1.5, 300,
            'Pipeline dominated by network-bound API calls\nLocal computation overhead is negligible',
            ha='center', fontsize=10, style='italic', color='#444',
            bbox=dict(boxstyle='round,pad=0.4', fc='#F0F8FF', ec=OKI['cyan'], lw=1.2))

    legend_els = [mpatches.Patch(fc=OKI['blue'],   label='V_exist'),
                  mpatches.Patch(fc=OKI['orange'],  label='V_secure'),
                  mpatches.Patch(fc=OKI['green'],   label='V_relevant'),
                  mpatches.Patch(fc=NAVY,           label='Total overhead')]
    ax.legend(handles=legend_els, fontsize=10, frameon=True, loc='upper left')

    ax.grid(axis='y', color=GREY_BOR, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(f'{OUT}/fig7_latency_bar.png', dpi=DPI, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print('✓ Fig 7 saved')

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 8 – Hallucination Rates Bar Chart (16 LLMs)
# ═══════════════════════════════════════════════════════════════════════════════
def fig8():
    models = ['Mistral 7B', 'Llama 3 (8B)', 'Mixtral 8x7B', 'Llama 3 (70B)',
              'Phi-3-medium', 'Mistral Large', 'Claude 3 Haiku', 'StarCoder2 (15B)',
              'GPT-3.5-Turbo', 'Gemini 1.0 Pro', 'Code Llama (34B)', 'Claude 3 Sonnet',
              'GPT-4', 'Gemini 1.5 Pro', 'DeepSeek-Coder', 'Claude 3 Opus']
    rates = [18.3, 16.1, 14.2, 12.4, 11.8, 9.5, 8.9, 7.9,
             7.2,  6.8,  6.5,  5.5,  4.8, 4.5,  4.2, 3.1]
    # provider families
    families = {
        'OpenAI / Anthropic': (['Claude 3 Haiku','Claude 3 Sonnet','Claude 3 Opus',
                                 'GPT-3.5-Turbo','GPT-4'], OKI['blue']),
        'Meta LLaMA':         (['Llama 3 (8B)','Llama 3 (70B)','Code Llama (34B)'], OKI['orange']),
        'Mistral AI':         (['Mistral 7B','Mixtral 8x7B','Mistral Large'], OKI['green']),
        'Specialised Code':   (['DeepSeek-Coder','StarCoder2 (15B)','Phi-3-medium'], OKI['purple']),
        'Google':             (['Gemini 1.0 Pro','Gemini 1.5 Pro'], OKI['cyan']),
    }
    family_color = {}
    for fname, (mlist, fc) in families.items():
        for m in mlist:
            family_color[m] = fc

    colors = [family_color.get(m, '#888') for m in models]

    fig, ax = plt.subplots(figsize=(13, 7))
    y = np.arange(len(models))
    bars = ax.barh(y, rates, color=colors, height=0.65, zorder=3,
                   edgecolor='white', linewidth=0.4)

    for bar, r in zip(bars, rates):
        ax.text(r+0.2, bar.get_y()+bar.get_height()/2,
                f'{r:.1f}%', va='center', fontsize=11, fontweight='bold', color='#222')

    ax.set_yticks(y); ax.set_yticklabels(models, fontsize=11)
    ax.set_xlabel('Hallucination Rate (%)', fontsize=13)
    ax.set_xlim(0, 22)
    ax.axvline(np.mean(rates), color=NAVY, lw=2, linestyle='--', alpha=0.7, zorder=2)
    ax.text(np.mean(rates)+0.2, 15.5, f'Mean = {np.mean(rates):.1f}%',
            color=NAVY, fontsize=10, style='italic')

    ax.set_title('Figure 8 · Package Hallucination Rates Across 16 LLMs\n(N = 576,000 code snippets)',
                 fontsize=13, fontweight='bold', color=NAVY, pad=10)

    legend_els = [mpatches.Patch(fc=OKI['blue'],   label='OpenAI / Anthropic'),
                  mpatches.Patch(fc=OKI['orange'],  label='Meta LLaMA'),
                  mpatches.Patch(fc=OKI['green'],   label='Mistral AI'),
                  mpatches.Patch(fc=OKI['purple'],  label='Specialised Code Models'),
                  mpatches.Patch(fc=OKI['cyan'],    label='Google')]
    ax.legend(handles=legend_els, fontsize=10, frameon=True, loc='lower right')

    ax.grid(axis='x', color=GREY_BOR, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(f'{OUT}/fig8_hallucination_rates.png', dpi=DPI, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print('✓ Fig 8 saved')

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 9 – Ablation Grouped Bar Chart
# ═══════════════════════════════════════════════════════════════════════════════
def fig9():
    configs   = ['Simple RAG\n(Existence Only)', 'Secure RAG\n(+ Security)', 'Full HalluGuard\n(Full CoV-RAG)']
    arr_means = [75.4, 89.1, 92.5]
    arr_sds   = [1.2,  0.9,  0.8]
    fpr_means = [0.3,  0.2,  0.2]
    colors    = [OKI['cyan'], OKI['orange'], OKI['blue']]

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    # ── ARR ──────────────────────────────────────────────────────────────────
    ax = axes[0]
    x = np.arange(len(configs))
    bars = ax.bar(x, arr_means, color=colors, width=0.55, zorder=3,
                  edgecolor='white', linewidth=0.5,
                  yerr=arr_sds, capsize=7,
                  error_kw=dict(lw=2, color='#333'))

    for bar, m, s in zip(bars, arr_means, arr_sds):
        ax.text(bar.get_x()+bar.get_width()/2, m+s+0.5,
                f'{m:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

    # significance brackets
    def sig_bracket(ax, x1, x2, y, p_label, color='#333'):
        margin = 0.3
        ax.plot([x1+margin, x1+margin, x2-margin, x2-margin],
                [y, y+0.8, y+0.8, y], color=color, lw=1.8, zorder=4)
        ax.text((x1+x2)/2, y+1.0, p_label, ha='center', fontsize=11,
                fontweight='bold', color=color)

    sig_bracket(ax, 0, 2, 94.0, '*** p<0.001', OKI['red'])
    sig_bracket(ax, 1, 2, 97.5, '*** p<0.001', OKI['red'])

    ax.set_xticks(x); ax.set_xticklabels(configs, fontsize=11)
    ax.set_ylabel('Automated Repair Rate — ARR (%)', fontsize=12)
    ax.set_ylim(65, 103)
    ax.set_title('(a) Automated Repair Rate', fontsize=12, fontweight='bold', color=NAVY)
    ax.grid(axis='y', color=GREY_BOR, lw=0.8, zorder=0)
    ax.set_axisbelow(True)

    # ── FPR ──────────────────────────────────────────────────────────────────
    ax = axes[1]
    bars2 = ax.bar(x, fpr_means, color=colors, width=0.55, zorder=3,
                   edgecolor='white', linewidth=0.5)
    for bar, m in zip(bars2, fpr_means):
        ax.text(bar.get_x()+bar.get_width()/2, m+0.005,
                f'{m:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels(configs, fontsize=11)
    ax.set_ylabel('False Positive Rate — FPR (%)', fontsize=12)
    ax.set_ylim(0, 0.6)
    ax.set_title('(b) False Positive Rate', fontsize=12, fontweight='bold', color=NAVY)
    ax.grid(axis='y', color=GREY_BOR, lw=0.8, zorder=0)
    ax.set_axisbelow(True)

    legend_els = [mpatches.Patch(fc=OKI['cyan'],   label='Simple RAG'),
                  mpatches.Patch(fc=OKI['orange'],  label='Secure RAG'),
                  mpatches.Patch(fc=OKI['blue'],    label='Full HalluGuard')]
    axes[0].legend(handles=legend_els, fontsize=10, frameon=True)

    fig.suptitle('Figure 9 · Ablation Study: ARR and FPR by Verification Configuration\n'
                 'Error bars: ±1 SD · *** p<0.001 with Bonferroni correction (α = 0.017)',
                 fontsize=12, fontweight='bold', color=NAVY, y=1.02)

    plt.tight_layout()
    plt.savefig(f'{OUT}/fig9_ablation.png', dpi=DPI, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print('✓ Fig 9 saved')

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 10 – Case Study 1: LangChain Git-Diff
# ═══════════════════════════════════════════════════════════════════════════════
def fig10():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14); ax.set_ylim(0, 8)
    ax.axis('off'); ax.set_facecolor('white')

    ax.text(7, 7.75, 'Figure 10 · Case Study 1: LangChain/Milvus Path Analogy Hallucination',
            ha='center', fontsize=13, fontweight='bold', color=NAVY)

    # ── Left panel: hallucinated code ────────────────────────────────────────
    ax.add_patch(FancyBboxPatch((0.3, 0.4), 6.0, 7.0,
                                boxstyle='round,pad=0.1',
                                fc='#FFF8F8', ec=OKI['red'], lw=1.5))
    ax.text(3.3, 7.2, 'LLM-Generated Code (BEFORE HalluGuard)',
            ha='center', fontsize=11, fontweight='bold', color=OKI['red'])

    hallucinated = [
        ('−', 'from langchain_milvus.retrievers import',      '#FFCCCC'),
        ('−', '    MilvusCollectionHybridSearchRetriever',     '#FFCCCC'),
        (' ', 'from pymilvus import WeightedRanker',           '#F8F8F8'),
        (' ', '',                                              '#F8F8F8'),
        (' ', 'retriever = MilvusCollectionHybridSearch',      '#F8F8F8'),
        (' ', '    Retriever(',                                '#F8F8F8'),
        ('−', '    collection=collection,',                    '#FFCCCC'),
        ('−', '    rerank=WeightedRanker(0.7, 0.3),  # ✗',   '#FFCCCC'),
        (' ', '    top_k=5',                                   '#F8F8F8'),
        (' ', ')',                                             '#F8F8F8'),
    ]

    for i, (marker, code, bg) in enumerate(hallucinated):
        y_pos = 6.6 - i*0.55
        ax.add_patch(Rectangle((0.5, y_pos-0.22), 5.6, 0.48, fc=bg, zorder=2))
        ax.text(0.75, y_pos, marker, fontsize=11, color=OKI['red'] if marker=='-' else '#888',
                fontweight='bold', fontfamily='monospace', zorder=3)
        ax.text(1.1, y_pos, code, fontsize=9, color='#1a1a1a',
                fontfamily='monospace', zorder=3)

    # Annotation callout
    ax.add_patch(FancyBboxPatch((0.5, 0.5), 5.6, 1.2,
                                boxstyle='round,pad=0.1',
                                fc='#FFE8E8', ec=OKI['red'], lw=1.2, zorder=3))
    ax.text(3.3, 1.55, '⚠  PATH ANALOGY HALLUCINATION',
            ha='center', fontsize=10, fontweight='bold', color=OKI['red'], zorder=4)
    ax.text(3.3, 1.1,
            'MilvusCollectionHybridSearchRetriever follows LangChain\n'
            'naming convention but does NOT exist in the SDK.',
            ha='center', fontsize=9, color='#600', zorder=4)

    # ── Verification trace (middle) ──────────────────────────────────────────
    ax.add_patch(FancyBboxPatch((6.6, 0.4), 1.5, 7.0,
                                boxstyle='round,pad=0.1', fc='#EEF4FB', ec=GREY_BOR, lw=1))
    ax.text(7.35, 7.2, 'HalluGuard\nVerification', ha='center', fontsize=9,
            fontweight='bold', color=NAVY)
    trace = [('V_exist', 'PyPI 200 OK', '✓ PASS', OKI['green']),
             ('V_path',  'Sub-module\nmissing', '✗ FAIL', OKI['red']),
             ('V_rel.',  'Class absent\nin SDK docs', '✗ FAIL', OKI['red']),
             ('Mitig.', 'Regenerate\nwith fix', '✓ OK', OKI['green'])]
    for i, (stage, detail, verdict, vc) in enumerate(trace):
        y_pos = 6.3 - i*1.4
        ax.text(7.35, y_pos+0.3, stage, ha='center', fontsize=9,
                fontweight='bold', color=NAVY)
        ax.text(7.35, y_pos, detail, ha='center', fontsize=8, color='#444')
        ax.add_patch(FancyBboxPatch((6.7, y_pos-0.35), 1.3, 0.28,
                                    boxstyle='round,pad=0.05', fc=vc, ec='none', zorder=3))
        ax.text(7.35, y_pos-0.22, verdict, ha='center', fontsize=8,
                color='white', fontweight='bold', zorder=4)

    # ── Right panel: repaired code ───────────────────────────────────────────
    ax.add_patch(FancyBboxPatch((8.4, 0.4), 5.3, 7.0,
                                boxstyle='round,pad=0.1',
                                fc='#F0FFF4', ec=OKI['green'], lw=1.5))
    ax.text(11.05, 7.2, 'Repaired Code (AFTER HalluGuard)',
            ha='center', fontsize=11, fontweight='bold', color=OKI['green'])

    repaired = [
        ('+', 'from langchain_milvus import Milvus',         '#CCFFCC'),
        ('+', 'from pymilvus import (',                       '#CCFFCC'),
        ('+', '    Collection,',                              '#CCFFCC'),
        ('+', '    BM25BuiltInFunction',                      '#CCFFCC'),
        ('+', ')',                                             '#CCFFCC'),
        (' ', '',                                             '#F0FFF4'),
        ('+', '# HalluGuard-verified: hybrid search via',     '#E8F8E8'),
        ('+', '# BM25BuiltInFunction + base Milvus class',   '#E8F8E8'),
        ('+', 'vectorstore = Milvus(',                        '#CCFFCC'),
        ('+', '    collection_name="knowledge_base", ...)',   '#CCFFCC'),
    ]

    for i, (marker, code, bg) in enumerate(repaired):
        y_pos = 6.6 - i*0.55
        ax.add_patch(Rectangle((8.6, y_pos-0.22), 4.8, 0.48, fc=bg, zorder=2))
        ax.text(8.75, y_pos, marker, fontsize=11,
                color=OKI['green'] if marker=='+' else '#888',
                fontweight='bold', fontfamily='monospace', zorder=3)
        ax.text(9.1, y_pos, code, fontsize=9, color='#1a1a1a',
                fontfamily='monospace', zorder=3)

    # Success badge
    ax.add_patch(FancyBboxPatch((8.6, 0.5), 4.8, 1.1,
                                boxstyle='round,pad=0.1',
                                fc='#CCFFCC', ec=OKI['green'], lw=1.2, zorder=3))
    ax.text(11.0, 1.1, '✓ SUCCESS — ImportError prevented',
            ha='center', fontsize=10, fontweight='bold', color='#004D30', zorder=4)
    ax.text(11.0, 0.7, 'BM25BuiltInFunction · Verified on PyPI',
            ha='center', fontsize=9, color='#004D30', zorder=4)

    plt.tight_layout()
    plt.savefig(f'{OUT}/fig10_casestudy1.png', dpi=DPI, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print('✓ Fig 10 saved')

# ═══════════════════════════════════════════════════════════════════════════════
# FIG 11 – Case Study 2: Stripe-Go v80 Temporal Race Condition
# ═══════════════════════════════════════════════════════════════════════════════
def fig11():
    fig = plt.figure(figsize=(15, 8))
    ax_main  = fig.add_axes([0.05, 0.12, 0.55, 0.75])  # timeline
    ax_score = fig.add_axes([0.65, 0.12, 0.32, 0.75])  # score panel

    fig.text(0.5, 0.97,
             'Figure 11 · Case Study 2: Stripe-Go v80 — Adversarial Slopsquatting via Version Prediction',
             ha='center', fontsize=13, fontweight='bold', color=NAVY)

    # ── LEFT: Timeline ────────────────────────────────────────────────────────
    ax = ax_main
    ax.set_facecolor('#F9F9FB')
    versions = [60, 65, 70, 71, 72]
    ages_days = [730, 500, 365, 180, 90]
    downloads = [5e6, 4e6, 3.5e6, 2e6, 1.5e6]

    ax.scatter(ages_days, versions, s=180, color=OKI['green'], zorder=5, label='Official Stripe-Go (verified)')
    for v, a, d in zip(versions, ages_days, downloads):
        ax.text(a+10, v+0.1, f'v{v}\n{d/1e6:.1f}M dl', fontsize=8.5, color='#226')

    # Attacker's package
    ax.scatter([2], [80], s=350, color=OKI['red'], marker='X', zorder=6, label='Attacker package (v80)')
    ax.text(8, 80.3, 'github.com/stripe/stripe-go/v80\nAge: <72h · Downloads: 0\nPGP: MISMATCH',
            fontsize=9, color=OKI['red'], style='italic',
            bbox=dict(boxstyle='round,pad=0.3', fc='#FFE8E8', ec=OKI['red'], lw=1.2))

    # LLM prediction arrow
    ax.annotate('', xy=(2, 80), xytext=(90, 73),
                arrowprops=dict(arrowstyle='->', color=OKI['orange'], lw=2.2,
                                connectionstyle='arc3,rad=-0.3'))
    ax.text(50, 77, 'LLM predicts v80\n(temporal extrapolation)', ha='center',
            fontsize=9.5, color=OKI['orange'], fontweight='bold', style='italic')

    # τ threshold line
    ax.axhline(72.5, color=NAVY, lw=1.5, linestyle='--', alpha=0.5)
    ax.text(600, 73.2, 'Latest stable: v72', color=NAVY, fontsize=9, style='italic')

    ax.set_xlabel('Package Age (days, approx.)', fontsize=12)
    ax.set_ylabel('Stripe-Go Version Number', fontsize=12)
    ax.set_xlim(-20, 800); ax.set_ylim(55, 85)
    ax.invert_xaxis()   # time flows left to right (old on right)
    ax.set_title('Version Timeline & Attacker Registration', fontsize=11,
                 fontweight='bold', color=NAVY, pad=6)
    ax.legend(fontsize=10, loc='lower right')
    ax.grid(color=GREY_BOR, lw=0.7)

    # ── RIGHT: Verification trace ─────────────────────────────────────────────
    ax2 = ax_score
    ax2.set_facecolor('white')
    ax2.axis('off')
    ax2.text(0.5, 0.98, 'HalluGuard Verification Trace',
             ha='center', va='top', fontsize=12, fontweight='bold',
             color=NAVY, transform=ax2.transAxes)

    trace_data = [
        ('Stage 1\nV_exist', 'GitHub API → 200 OK\n(attacker registered v80)', 'PASS', OKI['green']),
        ('Stage 2\nV_secure', 'S_rep = 0.08\nAge <72h · 0 downloads\nPGP mismatch → S_final < τ', 'FAIL ✗', OKI['red']),
        ('Stage 3\nV_relevant', 'N/A — Stage 2\nlockdown triggered', 'LOCKED', OKI['orange']),
        ('Mitigation', 'Revert to stripe-go/v72\nVerified stable release', '✓ CRITICAL\nSUCCESS', OKI['green']),
    ]

    for i, (stage, detail, verdict, vc) in enumerate(trace_data):
        y0 = 0.82 - i*0.22
        # stage box
        ax2.add_patch(FancyBboxPatch((0.02, y0), 0.95, 0.19,
                                     boxstyle='round,pad=0.02',
                                     fc='#F5F5F5', ec=GREY_BOR, lw=1,
                                     transform=ax2.transAxes, zorder=2))
        ax2.add_patch(FancyBboxPatch((0.02, y0+0.13), 0.23, 0.06,
                                     boxstyle='round,pad=0.01',
                                     fc=vc, ec='none',
                                     transform=ax2.transAxes, zorder=3))
        ax2.text(0.135, y0+0.16, stage, ha='center', va='center',
                 fontsize=8.5, fontweight='bold', color='white', transform=ax2.transAxes)
        ax2.text(0.32, y0+0.10, detail, ha='left', va='top',
                 fontsize=8, color='#222', transform=ax2.transAxes)
        ax2.add_patch(FancyBboxPatch((0.72, y0+0.04), 0.24, 0.10,
                                     boxstyle='round,pad=0.02',
                                     fc=vc, ec='none',
                                     transform=ax2.transAxes, zorder=3))
        ax2.text(0.84, y0+0.09, verdict, ha='center', va='center',
                 fontsize=8.5, fontweight='bold', color='white', transform=ax2.transAxes)

    # S_rep score bar
    ax2.text(0.5, 0.12, 'S_rep = 0.08  <<  τ = 0.70', ha='center',
             fontsize=11, fontweight='bold', color=OKI['red'], transform=ax2.transAxes)
    ax2.add_patch(Rectangle((0.05, 0.06), 0.90, 0.04, fc=GREY_BOR,
                             transform=ax2.transAxes, zorder=2))
    ax2.add_patch(Rectangle((0.05, 0.06), 0.90*0.08, 0.04, fc=OKI['red'],
                             transform=ax2.transAxes, zorder=3))
    tau_x = 0.05 + 0.90*0.70
    ax2.add_patch(Rectangle((tau_x, 0.045), 0.005, 0.07, fc=NAVY,
                             transform=ax2.transAxes, zorder=4))
    ax2.text(tau_x+0.015, 0.055, 'τ=0.70', fontsize=8, color=NAVY,
             transform=ax2.transAxes)

    ax2.text(0.5, 0.02,
             'Reputation-based detection stops attack\nbefore any malware executes.',
             ha='center', fontsize=9, style='italic', color='#444',
             transform=ax2.transAxes)

    plt.savefig(f'{OUT}/fig11_casestudy2.png', dpi=DPI, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print('✓ Fig 11 saved')

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig7()
    fig8()
    fig9()
    fig10()
    fig11()
    print('\n✅  All 10 figures generated at 300 DPI in', OUT)
