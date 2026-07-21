#!/usr/bin/env python3
"""Slow independent reference for u^2 + v^2 = 2*m^2.

This file intentionally does not factor m and does not use Gaussian integer
arithmetic.  It scans coordinates directly and is limited to small centers by
default.
"""

from __future__ import annotations

import argparse
import json
import math
from typing import Any


def brute_center(m: int) -> dict[str, Any]:
    target = 2 * m * m
    limit = math.isqrt(target)
    representations: set[tuple[int, int]] = set()
    deviations: dict[int, tuple[int, int]] = {}

    for x in range(limit + 1):
        y_squared = target - x * x
        y = math.isqrt(y_squared)
        if y * y != y_squared:
            continue
        x_signs = {x, -x}
        y_signs = {y, -y}
        for signed_x in x_signs:
            for signed_y in y_signs:
                representations.add((signed_x, signed_y))
        lower, upper = sorted((x, y))
        if 0 < lower < upper:
            difference = upper * upper - lower * lower
            if difference % 2:
                raise AssertionError(f"parity failure at m={m}")
            deviation = difference // 2
            if lower * lower + deviation != m * m:
                raise AssertionError(f"minus-root failure at m={m}")
            if m * m + deviation != upper * upper:
                raise AssertionError(f"plus-root failure at m={m}")
            previous = deviations.setdefault(deviation, (lower, upper))
            if previous != (lower, upper):
                raise AssertionError(f"deviation collision at m={m}")

    for x, y in representations:
        if x * x + y * y != target:
            raise AssertionError(f"norm failure at m={m}")

    pairs = [
        [str(deviation), roots[0], roots[1]]
        for deviation, roots in sorted(deviations.items())
    ]
    return {"m": m, "r2": len(representations), "pairs": pairs}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--unsafe-large-reference", action="store_true")
    arguments = parser.parse_args()

    if arguments.start <= 0 or arguments.end < arguments.start:
        parser.error("a closed positive range is required")
    if arguments.end > 100_000 and not arguments.unsafe_large_reference:
        parser.error(
            "the independent brute-force reference is capped at 100000; "
            "pass --unsafe-large-reference to override"
        )

    for m in range(arguments.start, arguments.end + 1):
        print(
            json.dumps(
                brute_center(m),
                separators=(",", ":"),
                ensure_ascii=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
