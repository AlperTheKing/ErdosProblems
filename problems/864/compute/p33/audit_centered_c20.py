#!/usr/bin/env python3
"""Exact audit of centered C20 and the P33 tangent-gap factorization."""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from typing import Any


def ceil_cuberoot_square(n: int) -> int:
    target = n * n
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid * mid >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


def keep_largest(
    items: list[dict[str, Any]],
    row: dict[str, Any],
    key: str,
    limit: int,
) -> None:
    items.append(row)
    items.sort(key=lambda value: value[key], reverse=True)
    del items[limit:]


def audit(input_path: Path) -> dict[str, Any]:
    profile_count = 0
    canonical_count = 0
    high_support_count = 0
    centered_mismatch_count = 0
    negative_endpoint_slack_count = 0
    factorization_mismatch_count = 0
    centered_mismatches: list[dict[str, Any]] = []
    negative_endpoint_slacks: list[dict[str, Any]] = []
    factorization_mismatches: list[dict[str, Any]] = []
    c20_failures: list[dict[str, Any]] = []
    lg33_failures: list[dict[str, Any]] = []
    internal_lg33_failures: list[dict[str, Any]] = []
    strongest_c20: list[dict[str, Any]] = []
    strongest_lg33: list[dict[str, Any]] = []

    with gzip.open(input_path, "rt", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            row = json.loads(line)
            profile_count += 1
            h = int(row["H"])
            n = int(row["N"])
            k = int(row["size"])
            m = int(row["M"])
            d_weight = int(row["duplicate_weight"])
            q_weight = int(row["missing_weight"])
            z = int(row["Z"])
            truncation = int(row["gap_truncation_weight"])
            ambient_holes = n + h - 1 - m
            endpoint_slack = ambient_holes - truncation

            if z != d_weight - q_weight:
                centered_mismatch_count += 1
                if len(centered_mismatches) < 20:
                    centered_mismatches.append(
                        {
                            "line": line_number,
                            "sample_id": row["sample_id"],
                            "H": h,
                            "D": d_weight,
                            "Q": q_weight,
                            "Z": z,
                        }
                    )

            if endpoint_slack < 0:
                negative_endpoint_slack_count += 1
                if len(negative_endpoint_slacks) < 20:
                    negative_endpoint_slacks.append(
                        {
                            "line": line_number,
                            "sample_id": row["sample_id"],
                            "H": h,
                            "N": n,
                            "M": m,
                            "T": truncation,
                            "G": ambient_holes,
                            "endpoint_slack": endpoint_slack,
                        }
                    )

            if h != ceil_cuberoot_square(n):
                continue
            canonical_count += 1

            phi = (
                6 * m * (h * h + 2 * z)
                - 8 * n * h * h
                - 9 * h * h * h
                - 9 * n * (k - 1) * h
            )
            psi = (
                8 * n * z
                - 12 * h * h * ambient_holes
                + 3 * h * h * h
                - 12 * h * h
                - 9 * n * (k - 1) * h
            )
            internal_psi = (
                8 * n * z
                - 12 * h * h * truncation
                + 3 * h * h * h
                - 12 * h * h
                - 9 * n * (k - 1) * h
            )
            remainder = 2 * (3 * m - 2 * n) * (2 * z - h * h)
            factorization_error = phi - psi - remainder
            if factorization_error:
                factorization_mismatch_count += 1
                if len(factorization_mismatches) < 20:
                    factorization_mismatches.append(
                        {
                            "line": line_number,
                            "sample_id": row["sample_id"],
                            "phi": phi,
                            "psi": psi,
                            "remainder": remainder,
                            "error": factorization_error,
                        }
                    )

            record = {
                "phi": phi,
                "psi": psi,
                "remainder": remainder,
                "internal_psi": internal_psi,
                "sample_id": row["sample_id"],
                "line": line_number,
                "N": n,
                "k": k,
                "H": h,
                "M": m,
                "D": d_weight,
                "Q": q_weight,
                "Z": z,
                "T": truncation,
                "G": ambient_holes,
                "endpoint_slack": endpoint_slack,
            }
            keep_largest(strongest_c20, record, "phi", 20)
            if phi > 0:
                c20_failures.append(record)

            if 3 * m < 2 * n:
                continue
            high_support_count += 1
            keep_largest(strongest_lg33, record, "psi", 20)
            if psi > 0:
                lg33_failures.append(record)
            if internal_psi > 0:
                internal_lg33_failures.append(record)

    return {
        "arithmetic": "integer",
        "input": str(input_path).replace("\\", "/"),
        "profile_count": profile_count,
        "canonical_count": canonical_count,
        "high_support_count": high_support_count,
        "centered_mismatch_count": centered_mismatch_count,
        "centered_mismatches": centered_mismatches,
        "negative_endpoint_slack_count": negative_endpoint_slack_count,
        "negative_endpoint_slacks": negative_endpoint_slacks,
        "factorization": "phi = psi + 2*(3*M-2*N)*(2*Z-H^2)",
        "factorization_mismatch_count": factorization_mismatch_count,
        "factorization_mismatches": factorization_mismatches,
        "c20_failure_count": len(c20_failures),
        "c20_failures": c20_failures[:20],
        "strongest_c20": strongest_c20,
        "lg33_domain": "canonical H and 3*M >= 2*N",
        "lg33_failure_count": len(lg33_failures),
        "lg33_failures": lg33_failures[:20],
        "internal_lg33_failure_count": len(internal_lg33_failures),
        "internal_lg33_failures": internal_lg33_failures[:20],
        "strongest_lg33": strongest_lg33,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("problems/864/compute/p20/results/profiles.jsonl.gz"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p33/audit_centered_c20.json"),
    )
    args = parser.parse_args()

    result = audit(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: value
                for key, value in result.items()
                if key
                not in {
                    "c20_failures",
                    "factorization_mismatches",
                    "internal_lg33_failures",
                    "lg33_failures",
                    "negative_endpoint_slacks",
                    "strongest_c20",
                    "strongest_lg33",
                }
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
