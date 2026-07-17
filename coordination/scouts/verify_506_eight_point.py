#!/usr/bin/env python3
"""Exact verifier for the eight-point obstruction recorded in the #506 rescout."""

from collections import Counter
from itertools import combinations
from math import comb, gcd
import json


POINTS = tuple(
    (sx * a, sy * a)
    for a in (1, 2)
    for sx in (-1, 1)
    for sy in (-1, 1)
)


def det3(rows: tuple[tuple[int, int, int], ...]) -> int:
    (a, b, c), (d, e, f), (g, h, i) = rows
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def circle_key(indices: tuple[int, int, int]) -> tuple[int, int, int, int] | None:
    rows = tuple(
        (x * x + y * y, x, y, 1)
        for x, y in (POINTS[index] for index in indices)
    )
    area2 = det3(tuple((row[1], row[2], row[3]) for row in rows))
    if area2 == 0:
        return None

    coefficients = (
        det3(tuple((row[1], row[2], row[3]) for row in rows)),
        -det3(tuple((row[0], row[2], row[3]) for row in rows)),
        det3(tuple((row[0], row[1], row[3]) for row in rows)),
        -det3(tuple((row[0], row[1], row[2]) for row in rows)),
    )
    divisor = 0
    for value in coefficients:
        divisor = gcd(divisor, abs(value))
    normalized = tuple(value // divisor for value in coefficients)
    if normalized[0] < 0:
        normalized = tuple(-value for value in normalized)
    assert normalized[0] > 0
    return normalized


def lies_on(point: tuple[int, int], key: tuple[int, int, int, int]) -> bool:
    x, y = point
    a, b, c, d = key
    return a * (x * x + y * y) + b * x + c * y + d == 0


def main() -> None:
    circle_multiplicity: Counter[tuple[int, int, int, int]] = Counter()
    collinear = 0
    for indices in combinations(range(len(POINTS)), 3):
        key = circle_key(indices)
        if key is None:
            collinear += 1
        else:
            circle_multiplicity[key] += 1

    support_sizes = {
        key: sum(lies_on(point, key) for point in POINTS)
        for key in circle_multiplicity
    }
    assert len(POINTS) == 8
    assert comb(len(POINTS), 3) == 56
    assert collinear == 8
    assert sum(circle_multiplicity.values()) == 48
    assert len(circle_multiplicity) == 18
    assert Counter(circle_multiplicity.values()) == Counter({4: 10, 1: 8})
    assert Counter(support_sizes.values()) == Counter({4: 10, 3: 8})
    assert all(
        circle_multiplicity[key] == comb(support_sizes[key], 3)
        for key in circle_multiplicity
    )

    n = len(POINTS)
    extrapolated_formula = 1 + comb(n - 1, 2) - (n - 1) // 2
    assert extrapolated_formula == 19

    result = {
        "circle_triples": sum(circle_multiplicity.values()),
        "collinear_triples": collinear,
        "distinct_circles": len(circle_multiplicity),
        "extrapolated_large_n_formula": extrapolated_formula,
        "multiplicity_histogram": {
            str(value): count
            for value, count in sorted(Counter(circle_multiplicity.values()).items())
        },
        "points": [list(point) for point in POINTS],
        "status": "PASS",
        "support_size_histogram": {
            str(value): count
            for value, count in sorted(Counter(support_sizes.values()).items())
        },
        "triples": comb(n, 3),
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
