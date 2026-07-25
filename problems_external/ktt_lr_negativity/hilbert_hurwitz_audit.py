"""One-shot exact falsifier for Hurwitz stability of LR stretching polynomials.

The input is the already-produced JSON/JSONL corpus.  No LR coefficients are
recomputed.  A candidate is reported only when an exact Hurwitz determinant
is nonpositive; numerical roots are displayed merely as a diagnostic.
"""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

import sympy as sp


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    a = [row[:] for row in matrix]
    out = Fraction(1)
    for col in range(len(a)):
        pivot = next((row for row in range(col, len(a)) if a[row][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            out = -out
        q = a[col][col]
        out *= q
        for j in range(col, len(a)):
            a[col][j] /= q
        for row in range(col + 1, len(a)):
            q = a[row][col]
            if q:
                for j in range(col, len(a)):
                    a[row][j] -= q * a[col][j]
    return out


def hurwitz_determinants(low_to_high: tuple[Fraction, ...]) -> list[Fraction]:
    degree = len(low_to_high) - 1
    # c[k] is the coefficient of x^(degree-k), with out-of-range entries zero.
    c = tuple(reversed(low_to_high))
    h = [[Fraction(0) for _ in range(degree)] for _ in range(degree)]
    for row in range(degree):
        for col in range(degree):
            index = 2 * col - row + 1
            if 0 <= index <= degree:
                h[row][col] = c[index]
    return [determinant([row[:k] for row in h[:k]]) for k in range(1, degree + 1)]


def records(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        if path.endswith(".jsonl"):
            for line in handle:
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    yield value
        else:
            try:
                value = json.load(handle)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return
            stack = [value]
            while stack:
                value = stack.pop()
                if isinstance(value, dict):
                    yield value
                    stack.extend(value.values())
                elif isinstance(value, list):
                    stack.extend(value)


def main(root: str) -> int:
    seen: set[tuple[Fraction, ...]] = set()
    audited = 0
    for directory, _, names in os.walk(root):
        for name in names:
            if not name.endswith((".json", ".jsonl")):
                continue
            path = os.path.join(directory, name)
            for record in records(path):
                raw = record.get("coeffs_low_to_high")
                if not isinstance(raw, list) or len(raw) < 2:
                    continue
                try:
                    coeffs = tuple(Fraction(item) for item in raw)
                except (TypeError, ValueError, ZeroDivisionError):
                    continue
                if coeffs in seen or coeffs[-1] <= 0:
                    continue
                seen.add(coeffs)
                audited += 1
                deltas = hurwitz_determinants(coeffs)
                if any(delta <= 0 for delta in deltas):
                    x = sp.symbols("x")
                    polynomial = sum(sp.Rational(q.numerator, q.denominator) * x**i
                                     for i, q in enumerate(coeffs))
                    print("EXACT_HURWITZ_COUNTEREXAMPLE")
                    print("source=", path)
                    print("record=", json.dumps(record, sort_keys=True))
                    print("coeffs_low_to_high=", [str(q) for q in coeffs])
                    print("hurwitz_determinants=", [str(q) for q in deltas])
                    print("roots=", sp.nroots(polynomial, n=30, maxsteps=500))
                    print("distinct_polynomials_audited=", audited)
                    return 0
    print("NO_COUNTEREXAMPLE", audited)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
