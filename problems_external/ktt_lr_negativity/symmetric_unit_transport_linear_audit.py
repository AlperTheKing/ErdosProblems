#!/usr/bin/env python3
"""Exact audit for the symmetric unit-column transportation family.

For a >= 3, let T_a have row margins (a,a,a) and column margins
(a+1,1^(2a-1)).  This checker validates the finite binomial expression for
the Ehrhart polynomial L_a(n), its ordinary linear coefficient A(a), and the
closed harmonic-number formula for A(a).

The a=3,4 interpolation cases are reconstructed by two independent integer
dynamic programs.  The final two dilations are held out.  The only broader
calibration is the registered bounded range 3 <= a <= 12.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json
import math


CALIBRATION_RANGE = range(3, 13)
DP_CASES = (3, 4)
EXPECTED_PAYLOAD_SHA256 = (
    "fabd84d1efc1c8b439f2f288d35e8e49245b1cd7624bfddf0b2fdc3623353afb"
)


def encode_fraction(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def multinomial3(total: int, first: int, second: int) -> int:
    third = total - first - second
    assert min(first, second, third) >= 0
    return (
        math.factorial(total)
        // math.factorial(first)
        // math.factorial(second)
        // math.factorial(third)
    )


def generalized_binomial_integer(top: int, bottom: int) -> int:
    """Polynomial binomial(top,bottom) for arbitrary integral top."""

    assert bottom >= 0
    if top >= 0:
        return math.comb(top, bottom) if top >= bottom else 0
    return (-1) ** bottom * math.comb(bottom - top - 1, bottom)


def finite_binomial_count(a: int, n: int) -> int:
    """Evaluate the finite binomial polynomial formula for L_a(n)."""

    assert a >= 3 and n >= 0
    k = 2 * a - 1
    m = 2 * k
    cap_sum = 0
    for i in range(a - 1):
        for j in range(a - 1 - i):
            alpha = a - 1 - i - j
            beta = 2 * k - 1 - i - 2 * j
            cap_sum += (
                (-1) ** i
                * multinomial3(k, i, j)
                * (n + 2) ** i
                * (n + 1) ** j
                * generalized_binomial_integer(alpha * n + beta, m)
            )
    return math.comb(n + 2, 2) ** k - 3 * cap_sum


def table_count_2d_dp(a: int, n: int) -> int:
    """Count tables by convolving the first two entries of every unit column."""

    k = 2 * a - 1
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    kernel = [
        (x, y)
        for x in range(n + 1)
        for y in range(n - x + 1)
    ]
    for _ in range(k):
        updated: defaultdict[tuple[int, int], int] = defaultdict(int)
        for (u, v), multiplicity in states.items():
            for x, y in kernel:
                updated[(u + x, v + y)] += multiplicity
        states = dict(updated)
    return sum(
        multiplicity
        for (u, v), multiplicity in states.items()
        if u <= a * n and v <= a * n and k * n - u - v <= a * n
    )


def table_count_cap_dp(a: int, n: int) -> int:
    """Count by a one-variable row-cap DP plus disjoint inclusion-exclusion."""

    k = 2 * a - 1
    coefficients = [1]
    kernel = list(range(1, n + 2))  # coefficient of t^y is y+1
    for _ in range(k):
        updated = [0] * (len(coefficients) + n)
        for old_degree, old_value in enumerate(coefficients):
            for y, weight in enumerate(kernel):
                updated[old_degree + y] += old_value * weight
        coefficients = updated
    threshold = (a - 1) * n - 1
    violation = sum(coefficients[: threshold + 1]) if threshold >= 0 else 0
    return math.comb(n + 2, 2) ** k - 3 * violation


def multiply_by_linear(
    polynomial: list[Fraction], constant: int
) -> list[Fraction]:
    result = [Fraction(0) for _ in range(len(polynomial) + 1)]
    for degree, coefficient in enumerate(polynomial):
        result[degree] += constant * coefficient
        result[degree + 1] += coefficient
    return result


def interpolate_monomial(samples: list[int]) -> list[Fraction]:
    """Exact Newton interpolation from values at 0,1,...,d."""

    differences = list(samples)
    newton_coefficients: list[int] = []
    while differences:
        newton_coefficients.append(differences[0])
        differences = [
            differences[index + 1] - differences[index]
            for index in range(len(differences) - 1)
        ]

    result = [Fraction(0) for _ in samples]
    binomial_basis = [Fraction(1)]
    for order, coefficient in enumerate(newton_coefficients):
        if order:
            binomial_basis = [
                value / order
                for value in multiply_by_linear(binomial_basis, -(order - 1))
            ]
        for degree, value in enumerate(binomial_basis):
            result[degree] += coefficient * value
    return result


def evaluate_polynomial(coefficients: list[Fraction], n: int) -> Fraction:
    value = Fraction(0)
    for coefficient in reversed(coefficients):
        value = value * n + coefficient
    return value


def grouped_reciprocal_sum(k: int, s: int) -> Fraction:
    """The inner sum before its beta-integral simplification."""

    return sum(
        (
            Fraction(
                math.comb(k, s) * math.comb(s, j) * 2 ** (s - j),
                math.comb(2 * k - 1, s + j),
            )
        )
        for j in range(s + 1)
    )


def linear_coefficient_finite_sum(a: int) -> Fraction:
    """A(a) from the uncollapsed finite (i,j)-sum."""

    k = 2 * a - 1
    q = Fraction(0)
    for i in range(a - 1):
        for j in range(a - 1 - i):
            q += Fraction(
                multinomial3(k, i, j)
                * 2**i
                * (a - 1 - i - j),
                math.comb(2 * k - 1, i + 2 * j),
            )
    return Fraction(3, 2 * k) * (k * k - q)


def linear_coefficient_grouped(a: int) -> Fraction:
    """A(a) after the inner identity J_(k,s)=k/(k-s)."""

    k = 2 * a - 1
    return Fraction(3, 2) * (
        k
        - sum(
            (Fraction(a - 1 - s, k - s) for s in range(a - 1)),
            Fraction(0),
        )
    )


def linear_coefficient_harmonic(a: int) -> Fraction:
    """A(a)=(3a/2)*(1+H_(2a-1)-H_a)."""

    harmonic_tail = sum(
        (Fraction(1, denominator) for denominator in range(a + 1, 2 * a)),
        Fraction(0),
    )
    return Fraction(3 * a, 2) * (1 + harmonic_tail)


def main() -> None:
    dp_payload: list[dict[str, object]] = []
    for a in DP_CASES:
        dimension = 4 * a - 2
        held_out = (dimension + 1, dimension + 2)
        values_2d = [
            table_count_2d_dp(a, n) for n in range(dimension + 3)
        ]
        values_cap = [
            table_count_cap_dp(a, n) for n in range(dimension + 3)
        ]
        values_formula = [
            finite_binomial_count(a, n) for n in range(dimension + 3)
        ]
        assert values_2d == values_cap == values_formula

        coefficients = interpolate_monomial(values_2d[: dimension + 1])
        assert len(coefficients) == dimension + 1
        assert coefficients[dimension] > 0
        for n in held_out:
            assert evaluate_polynomial(coefficients, n) == values_2d[n]

        exact_a = linear_coefficient_finite_sum(a)
        assert coefficients[1] == exact_a
        assert exact_a == linear_coefficient_grouped(a)
        assert exact_a == linear_coefficient_harmonic(a)

        dp_payload.append(
            {
                "a": a,
                "dimension": dimension,
                "held_out_dilations": list(held_out),
                "values_n0_to_d_plus_2": values_2d,
                "linear_coefficient": encode_fraction(exact_a),
            }
        )

    calibration: list[dict[str, object]] = []
    for a in CALIBRATION_RANGE:
        k = 2 * a - 1
        for s in range(a - 1):
            assert grouped_reciprocal_sum(k, s) == Fraction(k, k - s)
        finite = linear_coefficient_finite_sum(a)
        grouped = linear_coefficient_grouped(a)
        harmonic = linear_coefficient_harmonic(a)
        assert finite == grouped == harmonic
        assert harmonic > 0
        calibration.append({"a": a, "A": encode_fraction(harmonic)})

    payload = {
        "dp_cases": dp_payload,
        "calibration_range": [min(CALIBRATION_RANGE), max(CALIBRATION_RANGE)],
        "calibration": calibration,
        "closed_formula": "A(a)=(3a/2)*(1+H_(2a-1)-H_a)",
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    digest = sha256(encoded).hexdigest()
    if EXPECTED_PAYLOAD_SHA256:
        assert digest == EXPECTED_PAYLOAD_SHA256

    print("PASS")
    for row in dp_payload:
        print(
            f"a={row['a']} dimension={row['dimension']} "
            f"held_out={row['held_out_dilations']} A={row['linear_coefficient']}"
        )
    print("calibration=" + ",".join(f"{row['a']}:{row['A']}" for row in calibration))
    print("closed_formula=A(a)=(3a/2)*(1+H_(2a-1)-H_a)>0")
    print(f"payload_sha256={digest}")


if __name__ == "__main__":
    main()
