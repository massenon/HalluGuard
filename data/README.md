# Data — Provenance and Access

## 1. Full 576,000-Snippet Evaluation Corpus

The complete corpus used for RQ1 prevalence analysis originates from the
large-scale measurement study of Spracklen et al. (USENIX Security 2025)
and was extended with our NL-API tier. Due to GitHub's file-size limits,
the full corpus is archived on Zenodo:

**DOI: 10.5281/zenodo.[TO BE MINTED ON CAMERA-READY RELEASE]**

Download and extract to `data/full_576k_corpus/` before running
`experiments/rq1_hallucination_rate.py` against the complete dataset.

## 2. Files Included in This Repository

| File | N | Description |
|---|---|---|
| `nl_api_prompts.jsonl` | 2,500 | Niche-Library API dataset (LangChain, AWS CDK, Stripe-Go, Kubernetes-client) |
| `adversarial_benchmark.json` | 500 | Malicious/benign packages for V_secure validation |
| `annotated_gold_standard.csv` | 800 | Human-annotated ground truth (κ = 0.88), used for RQ2 |
| `security_validation_300.json` | 300 | Grid-search validation set for τ_secure derivation |
| `package_dictionary/python_modules.json` | ~20,000 | Module→package mappings (PyPI) |
| `package_dictionary/js_modules.json` | ~20,000 | Module→package mappings (npm) |

## 3. NL-API Dataset Construction (Algorithm 3)

1. `fetch_issues()` — crawled GitHub Issues (label: `good-first-issue`,
   ≥500 stars) from `langchain`, `boto3`, `stripe-python`,
   `kubernetes-client`.
2. `fetch_stackoverflow()` — collected Stack Overflow questions
   (CC BY-SA 4.0, tags: `langchain`, `boto3`, `stripe`, 2023–2024).
3. `dedup()` — removed near-duplicates via MinHash LSH (Jaccard ≥ 0.85).
4. `complexity_filter()` — retained only prompts requiring ≥3 third-party
   imports.
5. `domain_annotate()` — labelled each prompt with ecosystem and risk
   category.

Domain distribution: LangChain (700), AWS CDK/boto3 (650),
Stripe-Go/stripe-python (400), Kubernetes-client (300),
Other niche APIs (450).

## 4. Human Annotation Protocol (Algorithm 4)

800 snippets were stratified-sampled from the full corpus
(strata: model, hallucination-rate range, domain) and independently
labelled by two non-author SE researchers using the codebook in
`Appendix E` of the manuscript. Disagreements were resolved by a third
annotator. Cohen's κ = 0.88.

## 5. Adversarial Benchmark Composition (N = 500)

| Category | N | Source |
|---|---|---|
| Malicious/insecure (critical CVEs) | 150 | OSV database, public advisories |
| Known typosquatting attempts | 100 | Vu et al. (2020) dataset |
| Slopsquatting simulations | 100 | Hallucinated names from Spracklen et al., sandbox-registered then removed |
| Benign popular packages | 150 | PyPI top-5000 list (monthly snapshot) |

## 6. License

All included datasets are released under CC BY 4.0 unless otherwise noted
(Stack Overflow content under CC BY-SA 4.0 per platform terms).
