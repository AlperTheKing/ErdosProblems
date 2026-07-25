#!/usr/bin/env python3
"""Exact audit for the full symmetric unit-column transportation family.

For 2a<k<3a this independently reconstructs the registered minimal cases by
raw two-dimensional DP, checks the exact three-summand numerator expansion of
the double-cap generating function, interpolates at n=0,...,2k, and reserves
the last two dilations as heldouts.  A bounded exact loop also replays the two
finite cone identities used in the uniform proof.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json
import math


DP_CASES = ((2, 5), (3, 7), (3, 8))
CALIBRATION_MAX_A = 12
EXPECTED_PAYLOAD_SHA256 = (
    "2cf9b20044eff0c0e3b487d7688120ce9f5d998ab6c373f57aadd69390991d37"
)


def aggregate_distribution(k: int, n: int) -> dict[tuple[int, int], int]:
    """Distribution of the first two row totals for k labelled n-columns."""

    kernel = [(x, y) for x in range(n + 1) for y in range(n - x + 1)]
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for _ in range(k):
        updated: defaultdict[tuple[int, int], int] = defaultdict(int)
        for (u, v), multiplicity in states.items():
            for x, y in kernel:
                updated[(u + x, v + y)] += multiplicity
        states = dict(updated)
    return states


def counts_raw(a: int, k: int, n: int) -> tuple[int, int, int, int]:
    """Return (L,U,C1,C2) from one raw aggregate distribution."""

    distribution = aggregate_distribution(k, n)
    cap = a * n
    total = k * n
    unrestricted = sum(distribution.values())
    c1 = sum(value for (x, _y), value in distribution.items() if x > cap)
    c2 = sum(
        value
        for (x, y), value in distribution.items()
        if x > cap and y > cap
    )
    ehrhart = sum(
        value
        for (x, y), value in distribution.items()
        if x <= cap and y <= cap and total - x - y <= cap
    )
    assert ehrhart == unrestricted - 3 * c1 + 3 * c2
    return ehrhart, unrestricted, c1, c2


def cone_coefficient(p_degree: int, t_degree: int, A: int, B: int, C: int) -> int:
    """Coefficient of (1-p)^-A (1-t)^-B (1-pt)^-C."""

    if p_degree < 0 or t_degree < 0:
        return 0
    return sum(
        math.comb(A + p_degree - diagonal - 1, A - 1)
        * math.comb(B + t_degree - diagonal - 1, B - 1)
        * math.comb(C + diagonal - 1, C - 1)
        for diagonal in range(min(p_degree, t_degree) + 1)
    )


def c2_numerator_expansion(a: int, k: int, n: int) -> int:
    """C2 from the exact numerator of h_n(t,1,pt), with no raw DP."""

    b = k - 2 * a
    h = k - a
    answer = 0
    for i in range(k + 1):
        for j in range(k - i + 1):
            p_degree = b * n - 2 - j * (n + 2)
            t_degree = h * n - 1 - (i + j) * (n + 1)
            coefficient = cone_coefficient(
                p_degree,
                t_degree,
                i + j + 1,
                k - j,
                k - i + 1,
            )
            answer += (
                (-1) ** i
                * math.factorial(k)
                // math.factorial(i)
                // math.factorial(j)
                // math.factorial(k - i - j)
                * coefficient
            )
    return answer


def multiply_by_linear(poly: list[Fraction], constant: int) -> list[Fraction]:
    result = [Fraction(0) for _ in range(len(poly) + 1)]
    for degree, coefficient in enumerate(poly):
        result[degree] += constant * coefficient
        result[degree + 1] += coefficient
    return result


def interpolate(samples: list[int]) -> list[Fraction]:
    differences = list(samples)
    newton: list[int] = []
    while differences:
        newton.append(differences[0])
        differences = [b - a for a, b in zip(differences, differences[1:])]
    result = [Fraction(0) for _ in samples]
    basis = [Fraction(1)]
    for order, coefficient in enumerate(newton):
        if order:
            basis = [x / order for x in multiply_by_linear(basis, 1 - order)]
        for degree, value in enumerate(basis):
            result[degree] += coefficient * value
    return result


def evaluate(poly: list[Fraction], n: int) -> Fraction:
    value = Fraction(0)
    for coefficient in reversed(poly):
        value = value * n + coefficient
    return value


def c1_linear_formula(a: int, k: int) -> Fraction:
    return Fraction(1, 2) * sum(
        (Fraction(r, a + r) for r in range(1, k - a + 1)), Fraction(0)
    )


def c2_linear_formula(a: int, k: int) -> Fraction:
    return -Fraction(1, 2) * sum(
        (Fraction(r, 2 * a + r) for r in range(1, k - 2 * a + 1)),
        Fraction(0),
    )


def l_linear_formula(a: int, k: int) -> Fraction:
    b = k - 2 * a
    assert 1 <= b < a
    first_tail = sum(
        (Fraction(1, r) for r in range(a + 1, k + 1)), Fraction(0)
    )
    second_tail = sum(
        (Fraction(1, r) for r in range(2 * a + 1, k + 1)), Fraction(0)
    )
    return Fraction(3, 2) * (a - b + a * first_tail + 2 * a * second_tail)


def p_limited_dixon_sum(k: int, i: int, j: int) -> Fraction:
    """Finite sum after differentiating the p<=t chamber polynomial."""

    total = Fraction(0)
    for r in range(i + j + 1):
        numerator = (
            (-1) ** r
            * math.comb(i + j, r)
            * math.comb(2 * k - i - j - 1 - r, k - j - 1 - r)
        )
        denominator = (2 * k - r) * math.comb(2 * k - r - 1, k - j - 1)
        total += Fraction(numerator, denominator)
    return total


def t_limited_cancellation_sum(k: int, i: int, j: int) -> Fraction:
    """Finite sum after differentiating the t<=p chamber polynomial."""

    N = i + j
    total = Fraction(0)
    for r in range(min(N, 2 * j + 1) + 1):
        numerator = (
            (-1) ** (N + r)
            * math.comb(2 * j + 1, r)
            * math.comb(k + j - r, N - r)
        )
        denominator = (2 * k - r) * math.comb(
            2 * k - r - 1, 2 * k - 2 * N - 1
        )
        total += Fraction(numerator, denominator)
    return total


def main() -> None:
    payload_cases: list[dict[str, object]] = []
    for a, k in DP_CASES:
        degree = 2 * k
        rows = [counts_raw(a, k, n) for n in range(degree + 3)]
        assert [c2_numerator_expansion(a, k, n) for n in range(degree + 3)] == [
            row[3] for row in rows
        ]
        names = ("L", "U", "C1", "C2")
        linear: dict[str, Fraction] = {}
        for coordinate, name in enumerate(names):
            samples = [row[coordinate] for row in rows]
            polynomial = interpolate(samples[: degree + 1])
            for n in (degree + 1, degree + 2):
                assert evaluate(polynomial, n) == samples[n]
            linear[name] = polynomial[1]
        assert linear["L"] == linear["U"] - 3 * linear["C1"] + 3 * linear["C2"]
        assert linear["C1"] == c1_linear_formula(a, k)
        assert linear["C2"] == c2_linear_formula(a, k)
        assert linear["L"] == l_linear_formula(a, k)
        assert linear["L"] > 0
        payload_cases.append(
            {
                "a": a,
                "k": k,
                "degree": degree,
                "held_out": [degree + 1, degree + 2],
                "values_L_n0_to_d_plus_2": [row[0] for row in rows],
                "linear_L": str(linear["L"]),
                "linear_C1": str(linear["C1"]),
                "linear_C2": str(linear["C2"]),
            }
        )
        print(
            f"a={a} k={k} degree={degree} "
            + " ".join(f"{name}1={linear[name]}" for name in names)
        )

    calibration: list[dict[str, object]] = []
    for a in range(2, CALIBRATION_MAX_A + 1):
        for k in range(2 * a + 1, 3 * a):
            b = k - 2 * a
            h = k - a
            for j in range(b):
                expected = Fraction(
                    math.factorial(j) * math.factorial(k - j - 1),
                    2 * math.factorial(k),
                )
                assert p_limited_dixon_sum(k, 0, j) == expected
                for i in range(1, h - j):
                    if i < a:
                        assert p_limited_dixon_sum(k, i, j) == 0
                    else:
                        assert t_limited_cancellation_sum(k, i, j) == 0
            coefficient = l_linear_formula(a, k)
            assert coefficient > 0
            calibration.append({"a": a, "k": k, "A": str(coefficient)})

    payload = {
        "dp_cases": payload_cases,
        "calibration_max_a": CALIBRATION_MAX_A,
        "calibration": calibration,
        "c2_formula": "-1/2*sum(r/(2a+r),r=1..k-2a)",
        "l_formula": "3/2*(a-b+a*(H_k-H_a)+2a*(H_k-H_2a))",
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    digest = sha256(encoded).hexdigest()
    if EXPECTED_PAYLOAD_SHA256:
        assert digest == EXPECTED_PAYLOAD_SHA256
    print(f"calibration_pairs={len(calibration)} max_a={CALIBRATION_MAX_A}")
    print("closed_C2=-1/2*sum_(r=1)^b r/(2a+r)")
    print("closed_L=3/2*(a-b+a*(H_k-H_a)+2a*(H_k-H_2a))>0")
    print(f"payload_sha256={digest}")
    print("PASS")


if __name__ == "__main__":
    main()
