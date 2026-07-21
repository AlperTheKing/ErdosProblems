#!/usr/bin/env python3
"""Independently re-enumerate the declared ACE q12 search region."""

from __future__ import annotations

import json
import sys
import time
from fractions import Fraction
from math import isqrt


A2 = 2_568_913
A4 = 1_535_181_310_080
A6 = 59_427_518_261_760_000
SCALE = 10**12
HEIGHT_LIMIT = 1000 * SCALE
MATRIX = (
    (3066644681814, -1604217266982, 2304106286354, -2647588945619),
    (-1604217266982, 4852120801592, 2186366222773, -805702796450),
    (2304106286354, 2186366222773, 8991728418553, -4979765774895),
    (-2647588945619, -805702796450, -4979765774895, 4515819823940),
)
Point = tuple[Fraction, Fraction] | None


def on_curve(point: Point) -> bool:
    if point is None:
        return True
    x, y = point
    return y * y == x**3 + A2 * x**2 + A4 * x + A6


def negate(point: Point) -> Point:
    if point is None:
        return None
    return point[0], -point[1]


def add(left: Point, right: Point) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2:
        if y1 == -y2:
            return None
        slope = (3 * x1**2 + 2 * A2 * x1 + A4) / (2 * y1)
    else:
        slope = (y2 - y1) / (x2 - x1)
    x3 = slope * slope - A2 - x1 - x2
    y3 = slope * (x1 - x3) - y1
    return x3, y3


def multiply(multiplier: int, point: Point) -> Point:
    if multiplier < 0:
        return multiply(-multiplier, negate(point))
    result: Point = None
    addend = point
    while multiplier:
        if multiplier & 1:
            result = add(result, addend)
        addend = add(addend, addend)
        multiplier >>= 1
    return result


def q12(vector: tuple[int, int, int, int]) -> int:
    k1, k2, k3, k4 = vector
    return (
        MATRIX[0][0] * k1 * k1
        + MATRIX[1][1] * k2 * k2
        + MATRIX[2][2] * k3 * k3
        + MATRIX[3][3] * k4 * k4
        + 2 * MATRIX[0][1] * k1 * k2
        + 2 * MATRIX[0][2] * k1 * k3
        + 2 * MATRIX[0][3] * k1 * k4
        + 2 * MATRIX[1][2] * k2 * k3
        + 2 * MATRIX[1][3] * k2 * k4
        + 2 * MATRIX[2][3] * k3 * k4
    )


def is_rational_square(value: Fraction) -> bool:
    if value < 0:
        return False
    numerator_root = isqrt(value.numerator)
    denominator_root = isqrt(value.denominator)
    return (
        numerator_root * numerator_root == value.numerator
        and denominator_root * denominator_root == value.denominator
    )


def main() -> int:
    started = time.perf_counter()
    basis: tuple[Point, ...] = (
        (Fraction(-861840), Fraction(65622960)),
        (Fraction(-860928), Fraction(60830400)),
        (Fraction(-855520), Fraction(10311840)),
        (Fraction(-1506120), Fraction(-397614360)),
    )
    torsion: Point = (Fraction(-1672000), Fraction(0))
    if not all(on_curve(point) for point in (*basis, torsion)):
        raise ArithmeticError("basis or torsion calibration point is off curve")
    if multiply(2, torsion) is not None:
        raise ArithmeticError("torsion calibration failed")

    multiples = tuple(
        {coefficient: multiply(coefficient, point) for coefficient in range(-55, 56)}
        for point in basis
    )
    fixed = {
        Fraction(243, 560),
        Fraction(1147, 5040),
        Fraction(1100, 63),
        Fraction(7820, 567),
        Fraction(95, 112),
        Fraction(196, 45),
    }
    b = Fraction(1147, 5040)
    d = Fraction(7820, 567)
    g = Fraction(196, 45)

    lattice_vectors = 0
    nonzero_distinct = 0
    pass_b: list[dict[str, object]] = []
    pass_bd: list[dict[str, object]] = []
    candidates: list[dict[str, object]] = []

    for k1 in range(-55, 56, 2):
        for k2 in range(-55, 56, 2):
            for k3 in range(-55, 56, 2):
                for k4 in range(-54, 55, 2):
                    vector = (k1, k2, k3, k4)
                    proxy = q12(vector)
                    if proxy > HEIGHT_LIMIT:
                        continue
                    lattice_vectors += 1
                    if lattice_vectors % 5000 == 0:
                        print(
                            f"checked={lattice_vectors} pass_b={len(pass_b)} "
                            f"pass_bd={len(pass_bd)} candidates={len(candidates)}",
                            file=sys.stderr,
                            flush=True,
                        )

                    point = torsion
                    point = add(point, multiples[0][k1])
                    point = add(point, multiples[1][k2])
                    point = add(point, multiples[2][k3])
                    point = add(point, multiples[3][k4])
                    if point is None or not on_curve(point):
                        raise ArithmeticError(f"invalid point for vector {vector}")
                    h = Fraction(7, 5_078_700) * point[0]
                    if h == 0 or h in fixed:
                        continue
                    nonzero_distinct += 1

                    if not is_rational_square(b * h + 1):
                        continue
                    record = {"k": list(vector), "h": str(h), "q12": proxy}
                    pass_b.append(record)
                    if not is_rational_square(d * h + 1):
                        continue
                    pass_bd.append(record)
                    if not is_rational_square(g * h + 1):
                        continue
                    candidates.append(record)

    report = {
        "implementation": "independent-python-fraction-group-law",
        "status": "HIT" if candidates else "NO_HIT",
        "lattice_vectors": lattice_vectors,
        "nonzero_distinct": nonzero_distinct,
        "passed_b": len(pass_b),
        "passed_bd": len(pass_bd),
        "candidates": candidates,
        "pass_b_records": pass_b,
        "pass_bd_records": pass_bd,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    expected = (48714, 48706, 6, 2, 0)
    observed = (
        lattice_vectors,
        nonzero_distinct,
        len(pass_b),
        len(pass_bd),
        len(candidates),
    )
    return 0 if observed == expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
