#!/usr/bin/env python3
"""Cross-calibrate the fast and independent E-lane engines on tiny domains."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

from elliptic_reference import atomic_write_text, make_point_record, self_test


ENGINE_DIR = Path(__file__).resolve().parent
EXPECTED = {
    16: {"integral_points": 5, "distinct_doubled_x": 3, "ap_triples": 0, "candidates_reconstructed": 0},
    50: {"integral_points": 10, "distinct_doubled_x": 5, "ap_triples": 0, "candidates_reconstructed": 0},
    100: {"integral_points": 11, "distinct_doubled_x": 5, "ap_triples": 0, "candidates_reconstructed": 0},
    500: {"integral_points": 13, "distinct_doubled_x": 6, "ap_triples": 0, "candidates_reconstructed": 0},
}
COMPARE_COUNT_KEYS = (
    "kappas_selected",
    "kappas_completed",
    "x_tested",
    "integral_points",
    "distinct_doubled_x",
    "ap_endpoint_pairs",
    "ap_triples",
    "candidates_reconstructed",
    "verifier_attempts",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def run_logged(command: list[str], cwd: Path, stdout_path: Path, stderr_path: Path) -> int:
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    atomic_write_text(stdout_path, completed.stdout)
    atomic_write_text(stderr_path, completed.stderr)
    return completed.returncode


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fast-exe",
        type=Path,
        default=ENGINE_DIR / "elliptic_integral_search.exe",
    )
    parser.add_argument(
        "--reference",
        type=Path,
        default=ENGINE_DIR / "elliptic_reference.py",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ENGINE_DIR / "calibration" / "elliptic_k16",
    )
    parser.add_argument(
        "--bounds",
        type=int,
        nargs="+",
        default=sorted(EXPECTED),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    fast_exe = args.fast_exe.resolve()
    reference = args.reference.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    self_test()

    errors: list[str] = []
    cases: list[dict[str, Any]] = []
    baseline_500_counts: dict[str, int] | None = None
    baseline_500_inventory: list[dict[str, Any]] | None = None
    for bound in args.bounds:
        if bound not in EXPECTED:
            errors.append(f"no independent frozen expectation for B={bound}")
            continue
        fast_dir = out_dir / f"B{bound}" / "fast"
        reference_dir = out_dir / f"B{bound}" / "reference"
        fast_dir.mkdir(parents=True, exist_ok=True)
        reference_dir.mkdir(parents=True, exist_ok=True)
        common = [
            "--kappa-min", "1",
            "--kappa-max", "16",
            "--x-bound", str(bound),
            "--chunk-count", "1",
            "--chunk-index", "0",
            "--max-seconds", "60",
            "--emit-inventory",
        ]
        fast_exit = run_logged(
            [str(fast_exe), *common, "--out-dir", str(fast_dir)],
            ENGINE_DIR,
            fast_dir / "process.stdout.jsonl",
            fast_dir / "process.stderr.txt",
        )
        reference_exit = run_logged(
            [sys.executable, str(reference), *common, "--out-dir", str(reference_dir)],
            ENGINE_DIR,
            reference_dir / "process.stdout.jsonl",
            reference_dir / "process.stderr.txt",
        )
        case_errors: list[str] = []
        if fast_exit != 0:
            case_errors.append(f"fast exit {fast_exit}")
        if reference_exit != 0:
            case_errors.append(f"reference exit {reference_exit}")
        fast_summary = load_json(fast_dir / "summary.json")
        reference_summary = load_json(reference_dir / "summary.json")
        fast_counts = fast_summary["counts"]
        reference_counts = reference_summary["counts"]
        for key in COMPARE_COUNT_KEYS:
            if fast_counts[key] != reference_counts[key]:
                case_errors.append(
                    f"count {key}: fast={fast_counts[key]} reference={reference_counts[key]}"
                )
        for key, expected in EXPECTED[bound].items():
            if fast_counts[key] != expected:
                case_errors.append(
                    f"frozen {key}: observed={fast_counts[key]} expected={expected}"
                )
        fast_inventory = load_jsonl(fast_dir / "inventory.jsonl")
        reference_inventory = load_jsonl(reference_dir / "inventory.jsonl")
        if fast_inventory != reference_inventory:
            case_errors.append("canonical point inventories differ")
        if fast_summary["status"] != "NO_HIT" or reference_summary["status"] != "NO_HIT":
            case_errors.append(
                f"unexpected status fast={fast_summary['status']} reference={reference_summary['status']}"
            )
        cases.append(
            {
                "x_bound": bound,
                "valid": not case_errors,
                "errors": case_errors,
                "counts": {key: fast_counts[key] for key in COMPARE_COUNT_KEYS},
                "inventory_records": len(fast_inventory),
                "fast_summary": str(fast_dir / "summary.json"),
                "reference_summary": str(reference_dir / "summary.json"),
            }
        )
        if bound == 500:
            baseline_500_counts = {key: fast_counts[key] for key in COMPARE_COUNT_KEYS}
            baseline_500_inventory = fast_inventory
        errors.extend(f"B={bound}: {message}" for message in case_errors)

    chunk_errors: list[str] = []
    chunk_count = 3
    aggregate_counts = {key: 0 for key in COMPARE_COUNT_KEYS}
    aggregate_inventory: list[dict[str, Any]] = []
    if baseline_500_counts is None or baseline_500_inventory is None:
        chunk_errors.append("B=500 baseline missing")
    else:
        for chunk_index in range(chunk_count):
            chunk_dir = out_dir / "B500" / f"fast_chunk_{chunk_index}_of_{chunk_count}"
            chunk_dir.mkdir(parents=True, exist_ok=True)
            command = [
                str(fast_exe),
                "--kappa-min", "1",
                "--kappa-max", "16",
                "--x-bound", "500",
                "--chunk-count", str(chunk_count),
                "--chunk-index", str(chunk_index),
                "--max-seconds", "60",
                "--emit-inventory",
                "--out-dir", str(chunk_dir),
            ]
            chunk_exit = run_logged(
                command,
                ENGINE_DIR,
                chunk_dir / "process.stdout.jsonl",
                chunk_dir / "process.stderr.txt",
            )
            if chunk_exit != 0:
                chunk_errors.append(f"chunk {chunk_index} exit {chunk_exit}")
                continue
            chunk_summary = load_json(chunk_dir / "summary.json")
            if chunk_summary["status"] != "NO_HIT":
                chunk_errors.append(
                    f"chunk {chunk_index} status {chunk_summary['status']}"
                )
            for key in COMPARE_COUNT_KEYS:
                aggregate_counts[key] += chunk_summary["counts"][key]
            aggregate_inventory.extend(load_jsonl(chunk_dir / "inventory.jsonl"))

        for key in COMPARE_COUNT_KEYS:
            if aggregate_counts[key] != baseline_500_counts[key]:
                chunk_errors.append(
                    f"chunk aggregate {key}: {aggregate_counts[key]} != {baseline_500_counts[key]}"
                )
        inventory_key = lambda item: (
            item["kappa"],
            Fraction(int(item["x2_num"]), int(item["x2_den"])),
        )
        if sorted(aggregate_inventory, key=inventory_key) != sorted(
            baseline_500_inventory, key=inventory_key
        ):
            chunk_errors.append("three-chunk inventory union differs from unchunked B=500")
    errors.extend(f"chunk calibration: {message}" for message in chunk_errors)
    chunk_calibration = {
        "valid": not chunk_errors,
        "chunk_count": chunk_count,
        "aggregate_counts": aggregate_counts,
        "inventory_records": len(aggregate_inventory),
        "errors": chunk_errors,
    }

    point_5 = make_point_record(5, -4, 6)
    point_6 = make_point_record(6, 12, 36)
    vectors_valid = (
        point_5 is not None
        and [str(point_5.root_minus), str(point_5.root_center), str(point_5.root_plus)]
        == ["31/12", "41/12", "49/12"]
        and point_6 is not None
        and [str(point_6.root_minus), str(point_6.root_center), str(point_6.root_plus)]
        == ["1/2", "5/2", "7/2"]
    )
    if not vectors_valid:
        errors.append("frozen kappa=5 or kappa=6 doubling vector failed")

    report = {
        "schema_version": 1,
        "valid": not errors,
        "status": "CALIBRATION_OK" if not errors else "CALIBRATION_FAILED",
        "finished_utc": utc_now(),
        "fast_exe": str(fast_exe),
        "fast_exe_sha256": sha256(fast_exe),
        "fast_source_sha256": sha256(ENGINE_DIR / "elliptic_integral_search.cpp"),
        "reference_sha256": sha256(reference),
        "vectors_valid": vectors_valid,
        "cases": cases,
        "chunk_calibration": chunk_calibration,
        "errors": errors,
    }
    atomic_write_text(out_dir / "calibration_summary.json", json.dumps(report, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
