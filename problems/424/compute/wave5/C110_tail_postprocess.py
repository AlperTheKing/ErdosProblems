#!/usr/bin/env python3
"""Exact moving-cutoff and integrated-tail audit for a C110 weighted census."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def fraction_json(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    raw = args.input.read_bytes()
    source = json.loads(raw)
    require(source["arithmetic"] == "exact integers only", "nonexact source")
    require(source["first_C104_BIN_failure"] is None, "source has C104-BIN failure")

    bins = {int(row["j"]): row for row in source["bins"]}
    require(bins, "no occupied bins")
    for j, row in bins.items():
        counts = [int(value) for value in row["threshold_counts"]]
        require(int(row["capacity"]) == 1 << j, ("capacity", j))
        require(counts[0] == int(row["positive_root_count"]), ("positive", j))
        require(sum(counts) == int(row["threshold_token_sum"]), ("tokens", j))
        require(all(a >= b for a, b in zip(counts, counts[1:])), ("monotone", j))

    limit = int(source["limit"])
    log_bins = limit.bit_length()
    maximum_d = max(len(row["threshold_counts"]) for row in bins.values())
    rows: list[dict[str, object]] = []
    largest_pointwise = Fraction(0)
    largest_integrated = Fraction(0)

    for d in range(1, maximum_d + 1):
        cutoff = math.isqrt(d)
        if cutoff * cutoff < d:
            cutoff += 1
        tail = Fraction(0)
        pointwise = Fraction(0)
        tail_roots = 0
        for j, row in bins.items():
            counts = row["threshold_counts"]
            count = int(counts[d - 1]) if d <= len(counts) else 0
            if j < cutoff:
                continue
            tail_roots += count
            tail += Fraction(count, 1 << j)
            pointwise = max(pointwise, Fraction(d * count * count, 1 << (2 * j)))
        integrated = Fraction(d, log_bins * log_bins) * tail * tail
        largest_pointwise = max(largest_pointwise, pointwise)
        largest_integrated = max(largest_integrated, integrated)
        rows.append(
            {
                "D": d,
                "J_ceil_sqrt_D": cutoff,
                "tail_root_count": tail_roots,
                "dyadic_tail_upper": fraction_json(tail),
                "pointwise_square_ratio": fraction_json(pointwise),
                "integrated_square_ratio": fraction_json(integrated),
                "pointwise_C1_pass": pointwise <= 1,
                "integrated_C1_pass": integrated <= 1,
            }
        )

    payload = {
        "schema": "C110-moving-cutoff-tail-audit-v1",
        "source": {
            "path": args.input.as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "limit": limit,
            "classification_fnv1a64": source["classification_fnv1a64"],
        },
        "definitions": {
            "q_X(r)": "max(d(h)-1) over processed hard sources witnessing r",
            "J(D)": "ceil(sqrt(D))",
            "dyadic_tail_upper": "sum_{j>=J(D)} N_j(X,D)/2^j",
            "pointwise_square_ratio": "max_{j>=J(D)} D*N_j(X,D)^2/2^(2j)",
            "integrated_square_ratio": "D*dyadic_tail_upper^2/(1+floor(log2 X))^2",
        },
        "integer_log_bin_count": log_bins,
        "maximum_tested_D": maximum_d,
        "largest_pointwise_square_ratio": fraction_json(largest_pointwise),
        "largest_integrated_square_ratio": fraction_json(largest_integrated),
        "all_pointwise_C1_pass": largest_pointwise <= 1,
        "all_integrated_C1_pass": largest_integrated <= 1,
        "rows": rows,
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    encoded_bytes = encoded.encode("ascii")
    args.output.write_bytes(encoded_bytes)
    print(hashlib.sha256(encoded_bytes).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
