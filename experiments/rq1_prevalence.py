"""RQ1 — prevalence of package hallucination.

Two modes:
  --from-expected   Summarise the released per-model prevalence table (default; offline).
  --corpus-dir DIR  Recompute PHR from a local prevalence corpus by querying PyPI
                    (requires network; corpus available on reasonable request).

Corpus layout for --corpus-dir: one JSONL file per model version, each line
``{"task_id": ..., "code": ...}``.
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from experiments.common import DATA, EXPECTED, GENERATED, read_csv, write_csv
from halluguard.config import load_settings
from halluguard.extractor import Dependency, extract_module_roots
from halluguard.http import RequestsClient
from halluguard.registry_client import RegistryClient


def summarise_expected() -> None:
    rows = read_csv(EXPECTED / "prevalence_by_model.csv")
    phr = [float(r["phr_pct"]) for r in rows]
    udr = [float(r["udr_pct"]) for r in rows]
    print(f"Models: {len(rows)}")
    print(f"PHR (existence-based): mean {statistics.mean(phr):.1f}%  SD {statistics.stdev(phr):.1f}%  "
          f"range {min(phr):.1f}–{max(phr):.1f}%")
    print(f"UDR (any-stage):       mean {statistics.mean(udr):.1f}%  SD {statistics.stdev(udr):.1f}%  "
          f"range {min(udr):.1f}–{max(udr):.1f}%")


def recompute_from_corpus(corpus_dir: Path, pypi_url: str, timeout_s: float,
                          module_map: dict[str, str]) -> None:
    registry = RegistryClient(RequestsClient(timeout_s), pypi_url)
    cache: dict[str, bool | None] = {}
    out = []
    for path in sorted(corpus_dir.glob("*.jsonl")):
        n = hallucinated = indeterminate = 0
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                n += 1
                code = json.loads(line)["code"]
                try:
                    roots = extract_module_roots(code)
                except SyntaxError:
                    continue
                verdicts = []
                for root in roots:
                    pkg = module_map.get(root, root)
                    if pkg not in cache:
                        cache[pkg] = registry.verify_existence(Dependency(pkg)).exists
                    verdicts.append(cache[pkg])
                if any(v is False for v in verdicts):
                    hallucinated += 1
                elif any(v is None for v in verdicts):
                    indeterminate += 1
        out.append({"model_version": path.stem, "snippets": n, "hallucinated": hallucinated,
                    "indeterminate": indeterminate, "phr_pct": round(100 * hallucinated / max(n, 1), 2)})
        print(out[-1])
    write_csv(GENERATED / "rq1_prevalence_recomputed.csv", out, list(out[0].keys()))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--corpus-dir", type=Path, help="local prevalence corpus (JSONL per model)")
    args = parser.parse_args()
    if args.corpus_dir is None:
        summarise_expected()
        return
    settings = load_settings()
    module_map = json.loads((DATA / "package_dictionary/module_to_package.json").read_text(encoding="utf-8"))
    recompute_from_corpus(args.corpus_dir, settings.pypi_url, settings.http_timeout_s, module_map)


if __name__ == "__main__":
    main()
