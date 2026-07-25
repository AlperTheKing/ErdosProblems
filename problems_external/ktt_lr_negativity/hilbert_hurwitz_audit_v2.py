"""Exact Hurwitz audit over all certified LR-polynomial formats in the corpus.

Accepted JSON fields are ``coeffs_low_to_high`` and ``coeffs``.  A record must
carry lam/mu/nu, have constant coefficient one, agree with its stated degree,
and pass every available sample/held-out flag.  The two hstar_atlas TSV files
are also read by converting h* to the monomial basis exactly.
"""

from __future__ import annotations

import csv
import json
import os
import sys
from fractions import Fraction

import sympy as sp


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    matrix = [row[:] for row in matrix]
    value = Fraction(1)
    for column in range(len(matrix)):
        pivot = next((row for row in range(column, len(matrix))
                      if matrix[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
            value = -value
        entry = matrix[column][column]
        value *= entry
        for j in range(column, len(matrix)):
            matrix[column][j] /= entry
        for row in range(column + 1, len(matrix)):
            entry = matrix[row][column]
            for j in range(column, len(matrix)):
                matrix[row][j] -= entry * matrix[column][j]
    return value


def hurwitz_determinants(low_to_high: tuple[Fraction, ...]) -> list[Fraction]:
    degree = len(low_to_high) - 1
    descending = tuple(reversed(low_to_high))
    matrix = [[Fraction(0) for _ in range(degree)] for _ in range(degree)]
    for row in range(degree):
        for column in range(degree):
            index = 2 * column - row + 1
            if 0 <= index <= degree:
                matrix[row][column] = descending[index]
    return [determinant([row[:size] for row in matrix[:size]])
            for size in range(1, degree + 1)]


def multiply(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return result


def hstar_to_coefficients(hstar: list[int], degree: int) -> tuple[Fraction, ...]:
    result = [Fraction(0)] * (degree + 1)
    factorial = 1
    for k in range(2, degree + 1):
        factorial *= k
    for index, weight in enumerate(hstar):
        term = [Fraction(1)]
        for offset in range(degree):
            term = multiply(term, [Fraction(degree - index - offset), Fraction(1)])
        for power, coefficient in enumerate(term):
            result[power] += Fraction(weight) * coefficient / factorial
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return tuple(result)


def nested_records(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        if path.endswith(".jsonl"):
            for line in handle:
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    yield value
            return
        try:
            root = json.load(handle)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return
    stack = [root]
    while stack:
        value = stack.pop()
        if isinstance(value, dict):
            yield value
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)


def has_triple(record: dict) -> bool:
    return all(isinstance(record.get(key), (list, tuple, str))
               for key in ("lam", "mu", "nu"))


def validated_coefficients(record: dict, stats: dict[str, int]):
    raw = record.get("coeffs_low_to_high", record.get("coeffs"))
    if not isinstance(raw, list) or not has_triple(record):
        return None
    stats["triple_coefficient_records"] += 1
    for flag in ("heldout_ok", "agree", "roundtrip_ok", "hstar_roundtrip_ok"):
        if flag in record and record[flag] is not True:
            stats["flag_rejected"] += 1
            return None
    try:
        coefficients = [Fraction(value) for value in raw]
    except (TypeError, ValueError, ZeroDivisionError):
        stats["parse_rejected"] += 1
        return None
    while len(coefficients) > 1 and coefficients[-1] == 0:
        coefficients.pop()
    if coefficients[0] != 1 or coefficients[-1] <= 0:
        stats["ordering_rejected"] += 1
        return None
    stated_degree = record.get("d", record.get("degree"))
    if isinstance(stated_degree, int) and stated_degree != len(coefficients) - 1:
        stats["degree_rejected"] += 1
        return None
    samples = next((record[key] for key in ("P", "profile", "counts")
                    if isinstance(record.get(key), list)), None)
    if samples:
        try:
            sample_values = [Fraction(value) for value in samples]
        except (TypeError, ValueError, ZeroDivisionError):
            sample_values = []
        for n, expected in enumerate(sample_values):
            actual = sum(value * n**power
                         for power, value in enumerate(coefficients))
            if actual != expected:
                stats["sample_rejected"] += 1
                return None
    stats["validated_json_records"] += 1
    return tuple(coefficients)


def tsv_records(root: str, stats: dict[str, int]):
    for name in ("hstar_atlas.tsv", "hstar_atlas2.tsv"):
        path = os.path.join(root, "hstar_spread", name)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                if name.endswith("2.tsv") and not all(row.get(key) for key in ("lam", "mu", "nu")):
                    continue
                try:
                    degree = int(row["d"])
                    hstar = [int(value) for value in row["hstar"].split(",")]
                    coefficients = hstar_to_coefficients(hstar, degree)
                except (KeyError, TypeError, ValueError, ZeroDivisionError):
                    stats["tsv_rejected"] += 1
                    continue
                if coefficients[0] != 1 or len(coefficients) - 1 != degree:
                    stats["tsv_rejected"] += 1
                    continue
                stats["validated_tsv_records"] += 1
                yield path, row, coefficients


def audit(source: str, record, coefficients: tuple[Fraction, ...],
          seen: set[tuple[Fraction, ...]], stats: dict[str, int]) -> bool:
    if coefficients in seen:
        stats["duplicates"] += 1
        return False
    seen.add(coefficients)
    determinants = hurwitz_determinants(coefficients)
    if all(value > 0 for value in determinants):
        return False
    x = sp.symbols("x")
    polynomial = sum(sp.Rational(q.numerator, q.denominator) * x**power
                     for power, q in enumerate(coefficients))
    print("EXACT_HURWITZ_COUNTEREXAMPLE")
    print("source=", source)
    print("record=", json.dumps(record, sort_keys=True))
    print("coeffs_low_to_high=", [str(q) for q in coefficients])
    print("hurwitz_determinants=", [str(q) for q in determinants])
    print("roots=", sp.nroots(polynomial, n=30, maxsteps=500))
    return True


def main(root: str) -> int:
    stats = {key: 0 for key in (
        "triple_coefficient_records", "flag_rejected", "parse_rejected",
        "ordering_rejected", "degree_rejected", "sample_rejected",
        "validated_json_records", "validated_tsv_records", "tsv_rejected",
        "duplicates")}
    seen: set[tuple[Fraction, ...]] = set()
    for directory, _, names in os.walk(root):
        for name in names:
            if not name.endswith((".json", ".jsonl")):
                continue
            path = os.path.join(directory, name)
            for record in nested_records(path):
                coefficients = validated_coefficients(record, stats)
                if coefficients is not None and audit(path, record, coefficients, seen, stats):
                    print("stats=", json.dumps(stats, sort_keys=True))
                    return 0
    for path, record, coefficients in tsv_records(root, stats):
        if audit(path, record, coefficients, seen, stats):
            print("stats=", json.dumps(stats, sort_keys=True))
            return 0
    print("NO_HURWITZ_COUNTEREXAMPLE")
    print("distinct_exact_polynomials=", len(seen))
    print("stats=", json.dumps(stats, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
