"""Execution-based semantic-correctness runner (intended for the air-gapped sandbox).

Reads cases from --cases (JSONL: {"case_id", "code", "tests"}), executes each
case's reference tests with pytest under a hard timeout, and writes one row
per case. Failure categories mirror the released taxonomy:
fail-import, fail-param, fail-logic, timeout.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from experiments.common import GENERATED, write_csv

FIELDS = ["case_id", "unit_tests_passed", "result_category", "exit_code"]


def classify(output: str) -> str:
    low = output.lower()
    if "modulenotfounderror" in low or "importerror" in low:
        return "fail-import"
    if "typeerror" in low or "valueerror" in low:
        return "fail-param"
    return "fail-logic"


def run_case(code: str, tests: str, timeout_s: int) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "solution.py").write_text(code, encoding="utf-8")
        Path(tmp, "test_solution.py").write_text(tests, encoding="utf-8")
        try:
            proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "test_solution.py"],
                                  cwd=tmp, capture_output=True, text=True, timeout=timeout_s, check=False)
        except subprocess.TimeoutExpired:
            return {"unit_tests_passed": False, "result_category": "timeout", "exit_code": -1}
        passed = proc.returncode == 0
        return {"unit_tests_passed": passed,
                "result_category": "pass" if passed else classify(proc.stdout + proc.stderr),
                "exit_code": proc.returncode}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--out", type=Path, default=GENERATED / "scr_results.csv")
    args = parser.parse_args()

    rows = []
    with open(args.cases, encoding="utf-8") as fh:
        for line in fh:
            case = json.loads(line)
            rows.append({"case_id": case["case_id"], **run_case(case["code"], case["tests"], args.timeout)})
    passed = sum(r["unit_tests_passed"] for r in rows)
    print(f"SCR: {passed}/{len(rows)} = {100 * passed / max(len(rows), 1):.1f}%")
    write_csv(args.out, rows, FIELDS)


if __name__ == "__main__":
    main()
