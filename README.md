# HalluGuard — Replication Package

**Vibe Coding at Risk: A CoV-RAG Framework for Mitigating Slopsquatting Attacks in AI-Generated Code**

This repository contains the complete source code, configuration files, datasets, and experiment scripts required to independently reproduce every quantitative result reported in the manuscript.

---

## Project Overview

**HalluGuard** is an active, verification-first security middleware designed to secure the AI-assisted software development cycle (often termed *vibe coding*) against the emerging threat of **slopsquatting**. While Large Language Models (LLMs) accelerate software production, they exhibit a critical vulnerability: package hallucination—the generation of plausible-sounding but non-existent package dependencies. Adversaries systematically exploit this by pre-registering these hallucinated names on public registries (like PyPI or npm) with malicious payloads, executing a silent, pre-installation supply-chain compromise when a developer runs `pip install` or `npm install`.

Unlike existing hallucination-mitigation tools that rely on static text corpora or post-execution sandboxing, HalluGuard formally specializes the **Chain-of-Verification with Retrieval-Augmented Generation (CoV-RAG)** paradigm for live, stateful software-dependency security. It intercepts generated code, extracts imported packages, and validates them against live registry APIs, open-source vulnerability databases, and contextual relevance judgers before the code ever reaches the developer's workstation.

---

## Key Architectural Contributions

*   **Stateful CoV-RAG Pipeline:** Integrates a three-stage, sequential, short-circuiting verification loop—$V_{\mathrm{exist}}$ (registry existence), $V_{\mathrm{secure}}$ (multi-factor posture analysis), and $V_{\mathrm{relevant}}$ (contextual alignment)—operating on live, real-time API states to eliminate the "temporal decay of truth" typical of standard RAG systems.
*   **Adversarial Reputation Hardening ($S_{\mathrm{rep}}$):** Combines log-normalized package age, download velocity, and cryptographic PGP maintainer-key validation into a combined score, rendering the security checks highly resilient to automated reputation-tampering and download-inflation attacks.
*   **Cross-Model Verification Protocol:** Decouples the code-generation LLM from the relevance-judging LLM (e.g., GPT-4 paired with Claude 3.5 Sonnet) to eliminate intra-model semantic self-consistency bias, which empirically inflates same-model judge accuracy by $+3.2$ percentage points.
*   **Context-Preserving Mitigation Loop:** Automatically constructs non-truncated, structured regeneration prompts on verification failure, guiding the LLM toward safe, functionally equivalent repairs using PyPI-verified components without human manual intervention.

---

## 1. Repository Structure

```
halluguard/
├── halluguard/                     # Core framework source
│   ├── verifier.py                 # CoV orchestration (Algorithm 1)
│   ├── registry_client.py          # V_exist — PyPI/npm API client
│   ├── security_score.py           # V_secure — composite score (Algorithm 2)
│   ├── relevance_judge.py          # V_relevant — cross-model judge
│   ├── mitigation.py               # Mitigation & Regeneration Module
│   ├── config.yaml                 # Master experiment configuration
│   └── prompts/
│       ├── verbatim_relevance_prompt.txt
│       ├── verbatim_mitigation_prompt.txt
│       └── judge_config.yaml
├── data/
│   ├── nl_api_prompts.jsonl        # NL-API dataset (N=2,500)
│   ├── adversarial_benchmark.json  # Adversarial set (N=500)
│   ├── annotated_gold_standard.csv # Human-annotated GT (N=800, κ=0.88)
│   ├── package_dictionary/         # 20,000 module→package mappings
│   └── README.md                  # Dataset provenance & Zenodo DOI
├── experiments/
│   ├── rq1_hallucination_rate.py
│   ├── rq2_detection_repair.py
│   ├── rq3_latency.py
│   ├── rq4_ablation.py
│   └── grid_search.py
├── docker/sandbox/
│   ├── Dockerfile                  # Air-gapped Ubuntu 22.04 image
│   └── docker-compose.yml
├── figures/
│   └── generate_all.py             # Regenerates all 10 manuscript figures
├── results/
│   ├── raw/                        # Per-model, per-metric CSVs
│   └── figures/                    # 300 DPI PNG outputs
├── requirements.txt
├── LICENSE
├── CITATION.cff
└── README.md                       # (this file)
```

## 2. Environment Setup

```bash
git clone https://github.com/massenon/halluguard.git
cd halluguard
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Python ≥ 3.10 required. All pinned dependencies are listed in `requirements.txt`
(generated via `pip freeze` from the original experiment environment).

## 3. Configuration

Edit `halluguard/config.yaml` to set API keys as environment variables
(never commit raw keys):

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export OSV_API_ENDPOINT="https://api.osv.dev/v1"
export LIBRARIES_IO_API_KEY="..."
```

## 4. Reproducing Each Research Question

```bash
# RQ1 — Hallucination prevalence across 16 LLMs
python experiments/rq1_hallucination_rate.py --seed 42 137 2024

# RQ2 — Detection / repair effectiveness (uses human-annotated gold standard)
python experiments/rq2_detection_repair.py --gold data/annotated_gold_standard.csv

# RQ3 — Latency and cost overhead
python experiments/rq3_latency.py --n-trials 576000

# RQ4 — Ablation study (Simple RAG vs Secure RAG vs Full HalluGuard)
python experiments/rq4_ablation.py --bonferroni

# Security hyperparameter grid search (τ_secure derivation)
python experiments/grid_search.py --validation-set data/security_validation_300.json
```

All scripts write outputs to `results/raw/` as CSV files with column headers
matching the corresponding manuscript tables.

## 5. Regenerating All Figures

```bash
python figures/generate_all.py
```

Produces all figures in `results/figures/`,
using the Okabe-Ito colour-blind-safe palette throughout.

## 6. Semantic Correctness Verification (Sandboxed)

```bash
cd docker/sandbox
docker compose build
docker compose run --rm sandbox python /experiments/verify_scr.py
```

The sandbox runs with `network_mode: none` (no outbound network access) to
safely execute repaired snippets and adversarial benchmark packages without
risk of live malware execution.

## 7. Random Seeds and Reproducibility Parameters

| Parameter | Value |
|---|---|
| Random seeds | 42, 137, 2024 |
| GPT-4 model string | `gpt-4-turbo-2024-04-09` |
| Relevance judge model | `claude-3-5-sonnet-20240620` |
| Generation temperature | 0.2 (main); 0.0–1.0 step 0.1 (sampling sweep) |
| Max tokens | 512 |
| OSV database snapshot | 2025-03-01 |
| Security threshold τ_secure | 0.70 (grid-search optimal) |

## 8. Data Availability

The full 576,000-snippet evaluation corpus exceeds GitHub's file-size limits
and is archived on Zenodo: **DOI: 10.5281/zenodo.[TO BE MINTED ON RELEASE]**.
This repository includes the NL-API dataset (2,500 prompts), the adversarial
benchmark (500 packages), and the human-annotated gold standard (800
snippets) in full. See `data/README.md` for the complete provenance chain.

## 9. License

MIT License — see `LICENSE`.

## 11. Contact

Corresponding authors: Saurabh Agarwal (saurabh@yu.ac.kr),
Wooguil Pak (wooguilpak@yu.ac.kr)
