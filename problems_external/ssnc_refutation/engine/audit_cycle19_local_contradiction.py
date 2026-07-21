#!/usr/bin/env python3
"""Exhaust the relaxed five-vertex model behind the cycle-19 contradiction."""

from __future__ import annotations

import itertools
import json


VERTICES = tuple(range(5))
A, B, C, D, E = VERTICES
BLOCK_B = (A, B, C)
BLOCK_C = (A, D, E)
PAIRS = tuple((x, y) for x in VERTICES for y in VERTICES if x < y)


def arc(state: tuple[int, ...], tail: int, head: int) -> bool:
    """State 0 is missing, 1 is low-to-high, and 2 is high-to-low."""

    low, high = sorted((tail, head))
    pair_state = state[PAIRS.index((low, high))]
    return pair_state == (1 if tail == low else 2)


def is_directed_triangle(state: tuple[int, ...], block: tuple[int, int, int]) -> bool:
    x, y, z = block
    return (
        arc(state, x, y) and arc(state, y, z) and arc(state, z, x)
    ) or (
        arc(state, y, x) and arc(state, z, y) and arc(state, x, z)
    )


def rows_agree_outside(
    state: tuple[int, ...], block: tuple[int, int, int]
) -> bool:
    outside = tuple(x for x in VERTICES if x not in block)
    return all(
        arc(state, root, x) == arc(state, other, x)
        for root in block
        for other in block
        for x in outside
    )


def main() -> int:
    counts = {
        "all_oriented_or_missing_graphs": 0,
        "block_B_is_directed_triangle": 0,
        "both_blocks_are_directed_triangles": 0,
        "B_outside_rows_agree_after_both_triangles": 0,
        "C_outside_rows_agree_after_both_triangles": 0,
        "both_outside_row_equalities": 0,
    }

    for state in itertools.product(range(3), repeat=len(PAIRS)):
        counts["all_oriented_or_missing_graphs"] += 1
        if not is_directed_triangle(state, BLOCK_B):
            continue
        counts["block_B_is_directed_triangle"] += 1
        if not is_directed_triangle(state, BLOCK_C):
            continue
        counts["both_blocks_are_directed_triangles"] += 1
        agrees_b = rows_agree_outside(state, BLOCK_B)
        agrees_c = rows_agree_outside(state, BLOCK_C)
        counts["B_outside_rows_agree_after_both_triangles"] += int(agrees_b)
        counts["C_outside_rows_agree_after_both_triangles"] += int(agrees_c)
        counts["both_outside_row_equalities"] += int(agrees_b and agrees_c)

    expected = {
        "all_oriented_or_missing_graphs": 3**10,
        "block_B_is_directed_triangle": 2 * 3**7,
        "both_blocks_are_directed_triangles": 4 * 3**4,
        "B_outside_rows_agree_after_both_triangles": 16,
        "C_outside_rows_agree_after_both_triangles": 16,
        "both_outside_row_equalities": 0,
    }
    if counts != expected:
        raise AssertionError({"expected": expected, "actual": counts})
    print(json.dumps({"status": "PASS", "counts": counts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
