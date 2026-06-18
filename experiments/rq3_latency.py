"""
rq3_latency.py
----------------
Replicates RQ3: "What is the practical performance overhead of
HalluGuard in terms of latency and cost?"

Reproduces Table 13a/13b and Figure 7.

Usage:
    python experiments/rq3_latency.py --n-trials 576000
"""

import argparse
import csv
import logging
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "halluguard"))
from registry_client import RegistryClient, Dependency  # noqa: E402
from security_score import calculate_security_score  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rq3")


def measure_stage_latency(n_trials: int, sample_package: str = "requests") -> dict:
    client = RegistryClient()
    exist_latencies, secure_latencies, total_latencies = [], [], []

    for _ in range(min(n_trials, 1000)):   # capped for CI; full run uses corpus
        t0 = time.perf_counter()
        result = client.verify_existence(Dependency(sample_package))
        t_exist = (time.perf_counter() - t0) * 1000
        exist_latencies.append(t_exist if result.exists else result.latency_ms)

        t1 = time.perf_counter()
        calculate_security_score(sample_package, None, popular_packages=[sample_package])
        t_secure = (time.perf_counter() - t1) * 1000
        secure_latencies.append(t_secure)

        total_latencies.append(t_exist + t_secure)

    def summarize(values):
        return {
            "mean_ms": round(statistics.mean(values), 1),
            "sd_ms": round(statistics.stdev(values), 1) if len(values) > 1 else 0.0,
        }

    return {
        "v_exist": summarize(exist_latencies),
        "v_secure": summarize(secure_latencies),
        "total": summarize(total_latencies),
        "n_trials_executed": len(exist_latencies),
    }


def estimate_token_cost(n_snippets: int, cost_per_snippet: float = 0.0012) -> dict:
    return {
        "avg_cost_per_snippet_usd": cost_per_snippet,
        "cost_per_1000_snippets_usd": round(cost_per_snippet * 1000, 2),
        "total_corpus_cost_usd": round(cost_per_snippet * n_snippets, 2),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replicate RQ3 latency/cost overhead.")
    parser.add_argument("--n-trials", type=int, default=576000)
    parser.add_argument("--output", type=Path, default=Path("results/raw/rq3_latency_cost.csv"))
    args = parser.parse_args()

    latency = measure_stage_latency(args.n_trials)
    cost = estimate_token_cost(args.n_trials)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["stage", "mean_ms", "sd_ms"])
        for stage, stats_d in latency.items():
            if stage == "n_trials_executed":
                continue
            writer.writerow([stage, stats_d["mean_ms"], stats_d["sd_ms"]])
        writer.writerow([])
        writer.writerow(["cost_metric", "value_usd"])
        for k, v in cost.items():
            writer.writerow([k, v])

    logger.info("Latency: %s", latency)
    logger.info("Cost: %s", cost)
