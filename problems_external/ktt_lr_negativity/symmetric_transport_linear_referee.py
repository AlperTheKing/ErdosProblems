#!/usr/bin/env python3
"""Independent exact audit of the symmetric unit-column transportation family.

For a >= 3, T_a has row margins (a,a,a) and column margins
(a+1,1,...,1), with 2a-1 unit columns.  This script checks the exact
finite-binomial formula for its Ehrhart polynomial, reconstructs the linear
coefficient by interpolation, and compares small dilations with a direct
two-dimensional table dynamic program.

Only Python integers and fractions are used.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import comb, factorial


def s_by_weighted_dp(a: int, n: int) -> int:
    """Count one bad-row event by its exact one-dimensional generating DP."""
    k = 2 * a - 1
    cutoff = (a - 1) * n - 1
    if cutoff < 0:
        return 0
    dp = [0] * (cutoff + 1)
    dp[0] = 1
    for _ in range(k):
        nxt = [0] * (cutoff + 1)
        for old_sum, count in enumerate(dp):
            if not count:
                continue
            for y in range(min(n, cutoff - old_sum) + 1):
                nxt[old_sum + y] += count * (y + 1)
        dp = nxt
    return sum(dp)


def safe_comb(top: int, bottom: int) -> int:
    """Power-series binomial coefficient: zero below the required degree."""
    if top < bottom or top < 0:
        return 0
    return comb(top, bottom)


def s_by_finite_binomial_sum(a: int, n: int) -> int:
    """The exact finite numerator expansion, including its small-n zeros."""
    k = 2 * a - 1
    d = 2 * k
    answer = 0
    for i in range(a - 1):
        for j in range(a - 1 - i):
            m = i + j
            multinomial = factorial(k) // (
                factorial(i) * factorial(j) * factorial(k - m)
            )
            top = (a - 1 - m) * n + d - 1 - i - 2 * j
            answer += (
                (-1) ** i
                * multinomial
                * (n + 2) ** i
                * (n + 1) ** j
                * safe_comb(top, d)
            )
    return answer


def ehrhart_by_inclusion_exclusion(a: int, n: int) -> int:
    k = 2 * a - 1
    total = comb(n + 2, 2) ** k
    return total - 3 * s_by_weighted_dp(a, n)


def ehrhart_by_direct_2d_dp(a: int, n: int) -> int:
    """Directly count the projected unit columns; no bad-row decomposition."""
    k = 2 * a - 1
    cap = a * n
    states = {(0, 0): 1}
    column = [(x, y) for x in range(n + 1) for y in range(n - x + 1)]
    for _ in range(k):
        nxt: dict[tuple[int, int], int] = {}
        for (r1, r2), count in states.items():
            for x, y in column:
                nr1, nr2 = r1 + x, r2 + y
                if nr1 <= cap and nr2 <= cap:
                    key = (nr1, nr2)
                    nxt[key] = nxt.get(key, 0) + count
        states = nxt
    return sum(
        count
        for (r1, r2), count in states.items()
        if k * n - r1 - r2 <= cap
    )


def forward_differences(values: list[int]) -> list[int]:
    firsts = []
    row = values[:]
    while row:
        firsts.append(row[0])
        row = [row[i + 1] - row[i] for i in range(len(row) - 1)]
    return firsts


def newton_evaluate(firsts: list[int], n: int) -> int:
    return sum(delta * comb(n, q) for q, delta in enumerate(firsts))


def linear_from_newton(firsts: list[int]) -> Fraction:
    return sum(
        (Fraction((-1) ** (q - 1), q) * firsts[q] for q in range(1, len(firsts))),
        Fraction(0),
    )


def linear_from_double_sum(a: int) -> Fraction:
    k = 2 * a - 1
    d = 2 * k
    s_linear = Fraction(0)
    for i in range(a - 1):
        for j in range(a - 1 - i):
            m = i + j
            multinomial = factorial(k) // (
                factorial(i) * factorial(j) * factorial(k - m)
            )
            s_linear += Fraction(
                multinomial * 2**i * (a - 1 - m),
                d * comb(d - 1, i + 2 * j),
            )
    return Fraction(3 * k, 2) - 3 * s_linear


def linear_from_single_sum(a: int) -> Fraction:
    k = 2 * a - 1
    bad_linear = sum(
        (Fraction(r, a + r) for r in range(1, a)), Fraction(0)
    ) / 2
    return Fraction(3 * k, 2) - 3 * bad_linear


def linear_from_harmonics(a: int) -> Fraction:
    harmonic_tail = sum(
        (Fraction(1, q) for q in range(a + 1, 2 * a)), Fraction(0)
    )
    return Fraction(3 * a, 2) * (1 + harmonic_tail)


def fraction_text(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def audit_one(a: int) -> dict:
    degree = 4 * a - 2
    values = []
    finite_sum_values = []
    for n in range(degree + 3):
        s_dp = s_by_weighted_dp(a, n)
        s_sum = s_by_finite_binomial_sum(a, n)
        assert s_dp == s_sum, (a, n, s_dp, s_sum)
        values.append(comb(n + 2, 2) ** (2 * a - 1) - 3 * s_dp)
        finite_sum_values.append(s_sum)

    direct = []
    for n in range(5):
        count = ehrhart_by_direct_2d_dp(a, n)
        assert count == values[n], (a, n, count, values[n])
        direct.append(count)

    firsts = forward_differences(values[: degree + 1])
    assert len(firsts) == degree + 1
    assert firsts[-1] != 0
    assert newton_evaluate(firsts, degree + 1) == values[degree + 1]
    assert newton_evaluate(firsts, degree + 2) == values[degree + 2]

    by_interpolation = linear_from_newton(firsts)
    by_double = linear_from_double_sum(a)
    by_single = linear_from_single_sum(a)
    by_harmonic = linear_from_harmonics(a)
    assert by_interpolation == by_double == by_single == by_harmonic
    assert by_harmonic > 0

    value_digest = sha256(
        json.dumps(values, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return {
        "a": a,
        "degree": degree,
        "direct_2d_n_0_through_4": direct,
        "linear_coefficient": fraction_text(by_harmonic),
        "held_out": {
            str(degree + 1): values[degree + 1],
            str(degree + 2): values[degree + 2],
        },
        "values_sha256": value_digest,
    }


def main() -> None:
    payload = {
        "family": "3 x (2a), rows (a,a,a), columns (a+1,1^(2a-1))",
        "formula": "A(a)=(3a/2)*(1+H_(2a-1)-H_a)",
        "cases": [audit_one(a) for a in (3, 4, 5)],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("payload_sha256=" + sha256(canonical.encode("ascii")).hexdigest())
    print("PASS")


if __name__ == "__main__":
    main()
