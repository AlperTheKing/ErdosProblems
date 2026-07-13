#!/usr/bin/env python3
"""Audit the indexed-star support bound on exact signed-ruler witnesses."""

from __future__ import annotations

from collections import Counter


ROWS = (
    (2, (0, 1), 4),
    (3, (0, 1, 3), 10),
    (4, (0, 2, 5, 6), 19),
    (5, (0, 1, 3, 8, 12), 30),
    (6, (0, 1, 3, 8, 14, 18), 48),
    (7, (0, 5, 8, 9, 15, 26, 28), 68),
    (8, (0, 2, 3, 10, 16, 28, 33, 37), 85),
    (9, (0, 1, 3, 11, 15, 20, 36, 43, 49), 116),
    (10, (0, 1, 3, 8, 14, 26, 30, 47, 62, 71), 152),
    (11, (0, 1, 4, 6, 14, 30, 41, 50, 62, 69, 84), 191),
    (12, (0, 1, 4, 6, 14, 29, 36, 53, 69, 87, 96, 107), 240),
)


def labels(z: tuple[int, ...], gap: int):
    p = len(z)
    differences = tuple(z[j] - z[i] for i in range(p) for j in range(i + 1, p))
    stars = tuple(
        tuple(gap + z[i] + z[j] for j in range(i, p))
        for i in range(p)
    )
    return differences, stars


def interval_residue_capacity(value: int, modulus: int, width: int) -> int:
    residue = value % modulus
    first = modulus if residue == 0 else residue
    if first > width:
        return 0
    count = 1 + (width - first) // modulus
    if 1 <= value <= width:
        count -= 1
    return count


def audit_row(p: int, x: tuple[int, ...], span: int) -> dict[str, int]:
    width = x[-1]
    z = tuple(sorted(width - value for value in x))
    gap = span - 2 * width
    differences, stars = labels(z, gap)
    assert len(differences) == len(set(differences))
    assert not set(differences).intersection(value for star in stars for value in star)

    sum_lower = 0
    sum_intersection = 0
    sum_actual = 0
    sum_capacity = 0
    positive_moduli = 0
    max_lower = 0
    max_actual = 0
    tight_moduli = 0
    minimum_slack = None

    for modulus in range(p, p * p + 1):
        dcounts = Counter(value % modulus for value in differences)
        d_support = len(dcounts)
        lower = 0
        intersection = 0
        actual = 0
        capacity = 0
        for star in stars:
            ccounts = Counter(value % modulus for value in star)
            lower += max(0, d_support + len(ccounts) - modulus)
            intersection += len(set(dcounts).intersection(ccounts))
            actual += sum(dcounts[residue] * count for residue, count in ccounts.items())
            capacity += sum(
                interval_residue_capacity(value, modulus, width)
                for value in star
            )
        assert lower <= intersection <= actual <= capacity
        sum_lower += lower
        sum_intersection += intersection
        sum_actual += actual
        sum_capacity += capacity
        positive_moduli += lower > 0
        max_lower = max(max_lower, lower)
        max_actual = max(max_actual, actual)
        tight_moduli += lower == actual
        slack = capacity - lower
        minimum_slack = slack if minimum_slack is None else min(minimum_slack, slack)

    return {
        "p": p,
        "width": width,
        "gap": gap,
        "span": span,
        "sum_lower": sum_lower,
        "sum_intersection": sum_intersection,
        "sum_actual": sum_actual,
        "sum_capacity": sum_capacity,
        "positive_moduli": positive_moduli,
        "tight_moduli": tight_moduli,
        "max_lower": max_lower,
        "max_actual": max_actual,
        "minimum_capacity_slack": int(minimum_slack),
    }


def main() -> None:
    print(
        "p W G L sumLB sumH sumK sumU posM tightM maxLB maxK min(U-LB)"
    )
    for row in ROWS:
        stats = audit_row(*row)
        print(
            stats["p"],
            stats["width"],
            stats["gap"],
            stats["span"],
            stats["sum_lower"],
            stats["sum_intersection"],
            stats["sum_actual"],
            stats["sum_capacity"],
            stats["positive_moduli"],
            stats["tight_moduli"],
            stats["max_lower"],
            stats["max_actual"],
            stats["minimum_capacity_slack"],
        )


if __name__ == "__main__":
    main()

