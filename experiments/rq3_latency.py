"""RQ3 — verification latency.

  --from-expected  Print the released per-stage summary (default; offline).
  --live N         Time N live V_exist round-trips to PyPI for a benign package.
"""

from __future__ import annotations

import argparse
import statistics

from experiments.common import EXPECTED, read_csv
from halluguard.config import load_settings
from halluguard.extractor import Dependency
from halluguard.http import RequestsClient
from halluguard.registry_client import RegistryClient


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", type=int, default=0, metavar="N")
    parser.add_argument("--package", default="requests")
    args = parser.parse_args()

    if args.live <= 0:
        for r in read_csv(EXPECTED / "latency_by_stage.csv"):
            print(f"{r['stage']:<26} mean {r['mean_ms']:>4} ms  SD {r['sd_ms']:>3} ms  "
                  f"dispersion [{r['dispersion_lower_ms']}, {r['dispersion_upper_ms']}] ms")
        return

    settings = load_settings()
    registry = RegistryClient(RequestsClient(settings.http_timeout_s), settings.pypi_url)
    samples = [registry.verify_existence(Dependency(args.package)).latency_ms for _ in range(args.live)]
    print(f"V_exist live ({args.live} calls): mean {statistics.mean(samples):.1f} ms, "
          f"SD {statistics.stdev(samples) if len(samples) > 1 else 0:.1f} ms")


if __name__ == "__main__":
    main()
