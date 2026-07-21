#!/usr/bin/env python3
"""Independently replay an ACE q12 ``vertices.tsv`` artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Iterator, TextIO


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


A2 = 2_568_913
A4 = 1_535_181_310_080
A6 = 59_427_518_261_760_000
SCALE = 10**12
HEIGHT_LIMIT = 1000 * SCALE
EXPECTED_COUNT = 24_356
HEADER = (
    "index",
    "k1",
    "k2",
    "k3",
    "k4",
    "q12_scaled",
    "numerator",
    "denominator",
)
MATRIX = (
    (3066644681814, -1604217266982, 2304106286354, -2647588945619),
    (-1604217266982, 4852120801592, 2186366222773, -805702796450),
    (2304106286354, 2186366222773, 8991728418553, -4979765774895),
    (-2647588945619, -805702796450, -4979765774895, 4515819823940),
)
BASIS = (
    (Fraction(-861840), Fraction(65622960)),
    (Fraction(-860928), Fraction(60830400)),
    (Fraction(-855520), Fraction(10311840)),
    (Fraction(-1506120), Fraction(-397614360)),
)
TORSION = (Fraction(-1672000), Fraction(0))
BASE_TRIPLE = {
    Fraction(243, 560),
    Fraction(1100, 63),
    Fraction(95, 112),
}
Point = tuple[Fraction, Fraction] | None
Vector = tuple[int, int, int, int]


class VerificationError(Exception):
    """A concise artifact-verification failure."""


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
        slope = (3 * x1 * x1 + 2 * A2 * x1 + A4) / (2 * y1)
    else:
        slope = (y2 - y1) / (x2 - x1)
    x3 = slope * slope - A2 - x1 - x2
    y3 = slope * (x1 - x3) - y1
    return x3, y3


def multiply(coefficient: int, point: Point) -> Point:
    if coefficient < 0:
        return multiply(-coefficient, negate(point))
    result: Point = None
    addend = point
    while coefficient:
        if coefficient & 1:
            result = add(result, addend)
        addend = add(addend, addend)
        coefficient >>= 1
    return result


def q12(vector: Vector) -> int:
    return sum(
        vector[row] * MATRIX[row][column] * vector[column]
        for row in range(4)
        for column in range(4)
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def parse_row(stream: TextIO, line_number: int) -> tuple[int, Vector, int, int, int] | None:
    line = stream.readline()
    if line == "":
        return None
    fields = line.rstrip("\r\n").split("\t")
    if len(fields) != len(HEADER):
        raise VerificationError(
            f"line {line_number}: expected {len(HEADER)} tab-separated fields"
        )
    try:
        values = tuple(int(field) for field in fields)
    except ValueError as error:
        raise VerificationError(f"line {line_number}: non-integer field") from error
    index, k1, k2, k3, k4, proxy, numerator, denominator = values
    return index, (k1, k2, k3, k4), proxy, numerator, denominator


def canonical_vectors() -> Iterator[tuple[Vector, int]]:
    for k1 in range(1, 56, 2):
        for k2 in range(-55, 56, 2):
            for k3 in range(-55, 56, 2):
                for k4 in range(-54, 55, 2):
                    vector = (k1, k2, k3, k4)
                    proxy = q12(vector)
                    if proxy <= HEIGHT_LIMIT:
                        yield vector, proxy


def point_for_vector(
    vector: Vector, multiples: tuple[dict[int, Point], ...]
) -> Point:
    point: Point = TORSION
    for coefficient, table in zip(vector, multiples, strict=True):
        point = add(point, table[coefficient])
    return point


def verify(path: Path) -> dict[str, object]:
    started = time.perf_counter()
    input_sha256 = sha256_file(path)

    if not all(on_curve(point) for point in (*BASIS, TORSION)):
        raise VerificationError("independent basis calibration failed")
    if multiply(2, TORSION) is not None:
        raise VerificationError("independent torsion calibration failed")

    coefficient_ranges = (
        range(1, 56, 2),
        range(-55, 56, 2),
        range(-55, 56, 2),
        range(-54, 55, 2),
    )
    multiples = tuple(
        {coefficient: multiply(coefficient, point) for coefficient in coefficients}
        for point, coefficients in zip(BASIS, coefficient_ranges, strict=True)
    )

    seen_indices: set[int] = set()
    seen_vectors: set[Vector] = set()
    seen_values: set[Fraction] = set()
    region_vectors = 0
    excluded_zero = 0
    excluded_base = 0
    row_count = 0
    previous_vector: Vector | None = None

    with path.open("r", encoding="ascii", newline="") as stream:
        header = tuple(stream.readline().rstrip("\r\n").split("\t"))
        if header != HEADER:
            raise VerificationError("line 1: unexpected header")

        for vector, proxy in canonical_vectors():
            region_vectors += 1
            point = point_for_vector(vector, multiples)
            if point is None or not on_curve(point):
                raise VerificationError(f"invalid recomputed point at vector {vector}")
            h = Fraction(7, 5_078_700) * point[0]
            if h == 0:
                excluded_zero += 1
                continue
            if h in BASE_TRIPLE:
                excluded_base += 1
                continue

            line_number = row_count + 2
            parsed = parse_row(stream, line_number)
            if parsed is None:
                raise VerificationError(
                    f"line {line_number}: artifact ended before vector {vector}"
                )
            index, parsed_vector, parsed_proxy, numerator, denominator = parsed

            if index != row_count:
                raise VerificationError(
                    f"line {line_number}: index {index} does not equal {row_count}"
                )
            if index in seen_indices:
                raise VerificationError(f"line {line_number}: duplicate index {index}")
            if parsed_vector != vector:
                raise VerificationError(
                    f"line {line_number}: vector differs from canonical order"
                )
            if parsed_vector in seen_vectors:
                raise VerificationError(f"line {line_number}: duplicate vector")
            k1, k2, k3, k4 = parsed_vector
            if k1 <= 0 or any(value % 2 == 0 for value in (k1, k2, k3)):
                raise VerificationError(f"line {line_number}: odd-positive parity failed")
            if k4 % 2 != 0:
                raise VerificationError(f"line {line_number}: even k4 parity failed")
            if not (
                k1 <= 55
                and -55 <= k2 <= 55
                and -55 <= k3 <= 55
                and -54 <= k4 <= 54
            ):
                raise VerificationError(f"line {line_number}: coordinate bound failed")
            if previous_vector is not None and parsed_vector <= previous_vector:
                raise VerificationError(f"line {line_number}: vector order failed")
            if parsed_proxy != proxy or parsed_proxy != q12(parsed_vector):
                raise VerificationError(f"line {line_number}: q12 mismatch")
            if parsed_proxy > HEIGHT_LIMIT:
                raise VerificationError(f"line {line_number}: q12 boundary failed")
            if denominator <= 0:
                raise VerificationError(f"line {line_number}: nonpositive denominator")
            parsed_h = Fraction(numerator, denominator)
            if (
                parsed_h.numerator != numerator
                or parsed_h.denominator != denominator
            ):
                raise VerificationError(f"line {line_number}: h is not normalized")
            if parsed_h != h:
                raise VerificationError(f"line {line_number}: recomputed h mismatch")
            if parsed_h == 0 or parsed_h in BASE_TRIPLE:
                raise VerificationError(f"line {line_number}: excluded h present")
            if parsed_h in seen_values:
                raise VerificationError(f"line {line_number}: duplicate h")

            seen_indices.add(index)
            seen_vectors.add(parsed_vector)
            seen_values.add(parsed_h)
            previous_vector = parsed_vector
            row_count += 1

        extra = parse_row(stream, row_count + 2)
        if extra is not None:
            raise VerificationError(f"line {row_count + 2}: unexpected extra row")

    if row_count != EXPECTED_COUNT:
        raise VerificationError(
            f"row count {row_count} does not equal {EXPECTED_COUNT}"
        )
    if not (
        len(seen_indices) == len(seen_vectors) == len(seen_values) == row_count
    ):
        raise VerificationError("uniqueness count mismatch")

    return {
        "status": "PASS",
        "implementation": "independent-python-fraction-group-law",
        "input_sha256": input_sha256,
        "rows": row_count,
        "region_vectors": region_vectors,
        "excluded_zero": excluded_zero,
        "excluded_base": excluded_base,
        "checks": [
            "header",
            "index",
            "order",
            "uniqueness",
            "bounds",
            "parity",
            "q12",
            "curve",
            "h",
            "exclusions",
        ],
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vertices_tsv", type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    try:
        report = verify(args.vertices_tsv)
    except (OSError, VerificationError) as error:
        report = {
            "status": "FAIL",
            "implementation": "independent-python-fraction-group-law",
            "error": str(error),
            "elapsed_seconds": round(time.perf_counter() - started, 6),
        }
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
        return 1
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
