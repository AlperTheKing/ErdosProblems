#!/usr/bin/env python3
"""Exact layer-cake and square-block verification from a C108 endpoint census."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


def load(path: Path) -> tuple[dict, str]:
    payload = path.read_bytes()
    return json.loads(payload), hashlib.sha256(payload).hexdigest().upper()


def frac_json(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def ceil_sqrt(n: int) -> int:
    root = math.isqrt(n)
    return root if root * root == n else root + 1


def verify(source: dict, source_sha256: str) -> dict:
    bins = {row["j"]: row for row in source["bins"]}
    maximum_q = max((len(row["threshold_counts"]) for row in bins.values()), default=0)
    tails: dict[int, Fraction] = {}
    for d in range(1, maximum_q + 1):
        cutoff = ceil_sqrt(d)
        tails[d] = sum(
            (
                Fraction(row["threshold_counts"][d - 1], row["capacity"])
                for j, row in bins.items()
                if j >= cutoff and len(row["threshold_counts"]) >= d
            ),
            Fraction(),
        )
    for d in range(1, maximum_q):
        if tails[d + 1] > tails[d]:
            raise AssertionError(("tail is not monotone", d, tails[d], tails[d + 1]))

    lx = source["limit"].bit_length()
    best_gate = max(
        (
            (
                Fraction(d * tail * tail, lx * lx),
                d,
                ceil_sqrt(d),
                tail,
            )
            for d, tail in tails.items()
        ),
        default=(Fraction(), 0, 0, Fraction()),
    )

    layer_sum = sum(tails.values(), Fraction())
    capped_energy = sum(
        (
            Fraction(
                sum(row["threshold_counts"][: min(len(row["threshold_counts"]), j * j)]),
                row["capacity"],
            )
            for j, row in bins.items()
        ),
        Fraction(),
    )
    if layer_sum != capped_energy:
        raise AssertionError(("full layer-cake mismatch", layer_sum, capped_energy))

    blocks = []
    maximum_m = math.isqrt(maximum_q - 1) if maximum_q else 0
    for m in range(1, maximum_m + 1):
        lower = m * m
        upper = (m + 1) * (m + 1)
        block = sum((tails.get(d, Fraction()) for d in range(lower + 1, upper + 1)), Fraction())
        endpoint_tail = tails.get(upper, Fraction())
        monotone_lhs = (2 * m + 1) * endpoint_tail
        if monotone_lhs > block:
            raise AssertionError(("square-block monotonicity mismatch", m))

        direct_block = sum(
            (
                Fraction(
                    sum(
                        max(0, min(q, j * j, upper) - lower)
                        for q in range(1, len(row["threshold_counts"]) + 1)
                        for _ in range(
                            row["threshold_counts"][q - 1]
                            - (row["threshold_counts"][q] if q < len(row["threshold_counts"]) else 0)
                        )
                    ),
                    row["capacity"],
                )
                for j, row in bins.items()
            ),
            Fraction(),
        )
        if block != direct_block:
            raise AssertionError(("square-block layer-cake mismatch", m, block, direct_block))
        blocks.append(
            {
                "m": m,
                "D": upper,
                "terms": 2 * m + 1,
                "block_mass": frac_json(block),
                "direct_capped_increment": frac_json(direct_block),
                "endpoint_tail": frac_json(endpoint_tail),
                "monotone_lower_bound": frac_json(monotone_lhs),
                "block_over_m_cubed": frac_json(block / (m**3)),
            }
        )

    return {
        "schema": "C114-layercake-square-block-v1",
        "source_limit": source["limit"],
        "source_sha256": source_sha256,
        "arithmetic": "exact integers and Fraction only",
        "maximum_q": maximum_q,
        "L_X": lx,
        "maximum_endpoint_C_squared": frac_json(best_gate[0]),
        "maximum_endpoint_location": {
            "D": best_gate[1],
            "J": best_gate[2],
            "tail": frac_json(best_gate[3]),
        },
        "endpoint_C_equals_1": best_gate[0] <= 1,
        "threshold_tails_monotone": True,
        "full_layer_cake_identity": True,
        "sum_of_threshold_tails": frac_json(layer_sum),
        "capped_energy": frac_json(capped_energy),
        "square_blocks": blocks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, source_sha256 = load(args.input)
    result = verify(source, source_sha256)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_bytes(payload.encode("ascii"))
    print(hashlib.sha256(payload.encode("ascii")).hexdigest().upper())


if __name__ == "__main__":
    main()
