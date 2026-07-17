#!/usr/bin/env python3
"""Independent trial-division checks for the C24 healed-factor result."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
C24_RESULT = ROOT / "compute/wave3/C24_derivation_matching/result_1e6.json"
C16_RESULT = ROOT / "compute/wave3/C16_hole_contraction/result_1e6.json"
NATURAL_RESULT = ROOT / "compute/wave3/C24_derivation_matching/natural_2000.json"


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def pairs(product: int) -> list[tuple[int, int]]:
    result = []
    for left in range(2, math.isqrt(product) + 1):
        if product % left:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return result


def classify_through(limit: int) -> tuple[set[int], list[int]]:
    generated = {2, 3}
    hard = []
    for n in range(4, limit + 1):
        admissible = pairs(n + 1)
        if any(left in generated and right in generated for left, right in admissible):
            generated.add(n)
            continue
        if not allowed(n) or not admissible or n % 2:
            continue
        seed3_parent = (n + 1) // 3
        seed3 = (
            (n + 1) % 3 == 0
            and allowed(seed3_parent)
            and seed3_parent != 3
        )
        if not seed3:
            hard.append(n)
    return generated, hard


def main() -> None:
    generated, hard = classify_through(54)
    assert hard == [54]
    assert pairs(55) == [(5, 11)]
    assert 5 in generated
    assert 11 not in generated
    assert 21 not in generated
    assert generated == {
        2, 3, 5, 9, 14, 17, 26, 27, 33, 41, 44, 50, 51, 53
    }

    c24 = json.loads(C24_RESULT.read_text(encoding="ascii"))
    c16 = json.loads(C16_RESULT.read_text(encoding="ascii"))
    assert c24["limit"] == c16["limit"] == 1_000_000
    assert c24["counts"]["allowed_missing"] == c16["missing"]
    assert c24["counts"]["splitless"] == c16["splitless"]
    assert c24["counts"]["reducible"] == c16["reducible"]
    assert c24["counts"]["hard"] == c16["partition"]["hard"]
    assert c24["first_hard"] == c24["first_failure"]["n"] == 54
    assert c24["first_failure"]["healed_missing_neighbors"] == []
    assert c24["first_failure"]["cutoff_capacity"]["healed_holes"] == [21]
    assert c24["first_matching_hall_witness"] == {
        "cutoff": 54,
        "left_set": [54],
        "neighbor_set": [],
        "hall_deficit": 1,
    }
    rank_zero = c24["rank_hall_audits"][0]
    rank_one = c24["rank_hall_audits"][1]
    assert rank_zero["first_failure"] == {
        "cutoff": 362,
        "depth": 2,
        "excess": 1,
        "left_count": 11,
        "neighbor_count": 10,
        "left_values": [54, 74, 114, 174, 186, 234, 252, 294, 318, 354, 362],
        "neighbor_values": [21, 35, 39, 66, 75, 110, 117, 119, 120, 126],
    }
    assert rank_one["failure_events"] == 0
    assert c24["smallest_surviving_rank_offset"] == 1

    natural = json.loads(NATURAL_RESULT.read_text(encoding="ascii"))
    assert [
        row["first_failure_cutoff"] for row in natural["variants"]
    ] == [32, 39, 54, 186]
    expected_witnesses = [
        ([21, 32], [("half", 11)]),
        ([15, 23, 39], [("half", 8), ("third", 8)]),
        ([21, 32, 54], [("half", 11), ("third", 11)]),
        (
            [11, 21, 32, 54, 186],
            [("half", 6), ("half", 11), ("third", 6), ("third", 11)],
        ),
    ]
    for row, (left, right) in zip(natural["variants"], expected_witnesses):
        witness = row["hall_witness"]
        assert witness["left_values"] == left
        assert [
            (entry["copy"], entry["hole"])
            for entry in witness["neighbor_values"]
        ] == right
        assert witness["left_count"] - witness["neighbor_count"] == 1
    print("16/16 checks pass; natural Hall failures are 32,39,54,186")


if __name__ == "__main__":
    main()
