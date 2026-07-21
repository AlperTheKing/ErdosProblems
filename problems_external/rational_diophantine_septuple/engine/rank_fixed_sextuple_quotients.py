"""Run the frozen workspace-local mwrank gate on unique quotient models."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path


MWRANK = (
    "/mnt/e/Projects/ErdosProblems/problems_external/"
    "rational_diophantine_septuple/tools/eclib-ubuntu/root/usr/bin/mwrank"
)
LIBRARY_PATH = (
    "/mnt/e/Projects/ErdosProblems/problems_external/"
    "rational_diophantine_septuple/tools/eclib-ubuntu/root/usr/lib/x86_64-linux-gnu"
)
OPTIONS = ("-q", "-v", "0", "-p", "60", "-b", "8", "-x", "10", "-S", "10")
RANK_LINE = re.compile(r"^Curve \[([^]]+)\] :\s*Rank = ([0-9]+)$", re.MULTILINE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def model_label(record: dict[str, object]) -> str:
    return str(record["triple"] if record["degree"] == 3 else record["quadruple"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("models_json", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--timeout-seconds", type=int, default=1200)
    arguments = parser.parse_args()

    models = json.loads(arguments.models_json.read_text(encoding="utf-8"))
    if models.get("status") != "PASS" or models.get("quotient_records") != 70:
        raise RuntimeError("models.json did not pass its declared generation gate")

    unique: dict[tuple[int, ...], list[dict[str, object]]] = {}
    for record in models["records"]:
        key = tuple(int(value) for value in record["ainvariants"])
        unique.setdefault(key, []).append(record)
    if len(unique) != 55:
        raise RuntimeError("expected exactly 55 distinct integral models")

    ordered_models = list(unique)
    curve_input = "".join(
        "[" + ",".join(str(value) for value in model) + "]\n"
        for model in ordered_models
    )
    command = [
        "wsl.exe",
        "-d",
        "Ubuntu",
        "--",
        "env",
        f"LD_LIBRARY_PATH={LIBRARY_PATH}",
        MWRANK,
        *OPTIONS,
    ]
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        input=curve_input,
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=True,
        timeout=arguments.timeout_seconds,
        check=False,
    )
    elapsed = time.perf_counter() - started

    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = arguments.output_dir / "mwrank_stdout.txt"
    stderr_path = arguments.output_dir / "mwrank_stderr.txt"
    stdout_path.write_text(completed.stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(completed.stderr, encoding="utf-8", newline="\n")
    if completed.returncode != 0:
        raise RuntimeError(f"mwrank exited with code {completed.returncode}")
    if completed.stderr:
        raise RuntimeError("mwrank wrote nonempty stderr")

    matches = RANK_LINE.findall(completed.stdout)
    if len(matches) != len(ordered_models):
        raise RuntimeError(
            f"expected {len(ordered_models)} rank lines, observed {len(matches)}"
        )

    results: list[dict[str, object]] = []
    for expected, (coefficients_text, rank_text) in zip(ordered_models, matches):
        observed = tuple(int(value.strip()) for value in coefficients_text.split(","))
        if observed != expected:
            raise RuntimeError("mwrank output order/model differs from frozen input")
        references = [
            {
                "sextuple": record["sextuple"],
                "degree": record["degree"],
                "subset": model_label(record),
            }
            for record in unique[expected]
        ]
        results.append(
            {
                "ainvariants": list(expected),
                "rank": int(rank_text),
                "references": references,
            }
        )

    rank_zero = [result for result in results if result["rank"] == 0]
    report = {
        "status": "RANK_ZERO_FOUND" if rank_zero else "NO_RANK_ZERO",
        "mwrank_exit_code": completed.returncode,
        "mwrank_options": list(OPTIONS),
        "models_sha256": sha256(arguments.models_json),
        "unique_models": len(results),
        "quotient_records": 70,
        "rank_histogram": {
            str(rank): sum(result["rank"] == rank for result in results)
            for rank in sorted({int(result["rank"]) for result in results})
        },
        "minimum_rank": min(int(result["rank"]) for result in results),
        "rank_zero_count": len(rank_zero),
        "elapsed_seconds": elapsed,
        "stdout_sha256": sha256(stdout_path),
        "stderr_sha256": sha256(stderr_path),
        "results": results,
    }
    report_path = arguments.output_dir / "rank_results.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {key: report[key] for key in (
                "status",
                "unique_models",
                "rank_histogram",
                "minimum_rank",
                "rank_zero_count",
                "elapsed_seconds",
            )},
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
