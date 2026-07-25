#!/usr/bin/env python3
"""Exact finite gate for the registered codegree-three 3x8 route.

For row margins r_i >= 3 and column margins (sum(r)-7,1^7), a lattice
table at dilation one is determined by assigning each of the seven labelled
unit columns to one of the three rows.  If k_i columns choose row i, the large
column entry in that row is r_i-k_i.  Hence feasibility is exactly k_i <= r_i,
which depends only on min(r_i,7).

This checker first enumerates all 35 unordered capped triples twice, by
multinomial composition summation and by direct enumeration of all 3^7
assignments.  It then treats the 35 caps as the canonical representatives
3 <= r1 <= r2 <= r3 <= 7 and reconstructs their degree-14 Ehrhart
polynomials from a separate exact transportation-table dynamic program.
Values at n=15,16 are held out from interpolation.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement, product
import json
import math


TARGET_L1 = 255
NUMBER_OF_UNIT_COLUMNS = 7
CAP_VALUES = range(3, NUMBER_OF_UNIT_COLUMNS + 1)
EXPECTED_PAYLOAD_SHA256 = (
    "3907934da5f593179491c267b4fca629967dd442273afd520070040b10e6c0fb"
)
EXPECTED_FULL_PAYLOAD_SHA256 = (
    "3799958aaee2183d00beb97b793fa1a1d41ea053395a5c7d970469367b41fc48"
)
DIMENSION = 14
INTERPOLATION_MAX = DIMENSION
HELD_OUT_DILATIONS = (15, 16)


def multinomial(parts: tuple[int, int, int]) -> int:
    result = math.factorial(NUMBER_OF_UNIT_COLUMNS)
    for part in parts:
        result //= math.factorial(part)
    return result


def l1_by_compositions(caps: tuple[int, int, int]) -> int:
    total = 0
    for k0 in range(NUMBER_OF_UNIT_COLUMNS + 1):
        for k1 in range(NUMBER_OF_UNIT_COLUMNS - k0 + 1):
            k2 = NUMBER_OF_UNIT_COLUMNS - k0 - k1
            counts = (k0, k1, k2)
            if all(count <= cap for count, cap in zip(counts, caps)):
                total += multinomial(counts)
    return total


def l1_by_assignments(caps: tuple[int, int, int]) -> int:
    total = 0
    for assignment in product(range(3), repeat=NUMBER_OF_UNIT_COLUMNS):
        counts = tuple(assignment.count(row) for row in range(3))
        if all(count <= cap for count, cap in zip(counts, caps)):
            total += 1
    return total


def aggregate_distribution(dilation: int) -> dict[tuple[int, int], int]:
    """Count seven labelled unit-column allocations by first two row totals.

    At dilation n, one unit column contains a weak composition (x,y,z) of n.
    Repeated exact convolution of its triangular support gives the coefficient
    table of h_n(X,Y,Z)^7.  The third total is 7*n-a-b.
    """

    kernel = [
        (x, y)
        for x in range(dilation + 1)
        for y in range(dilation - x + 1)
    ]
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for _ in range(NUMBER_OF_UNIT_COLUMNS):
        updated: defaultdict[tuple[int, int], int] = defaultdict(int)
        for (a, b), multiplicity in states.items():
            for x, y in kernel:
                updated[(a + x, b + y)] += multiplicity
        states = dict(updated)
    return states


def table_count(
    rows: tuple[int, int, int],
    dilation: int,
    distribution: dict[tuple[int, int], int],
) -> int:
    """Count T(n*rows, n*(sum(rows)-7,1^7)) exactly."""

    bounds = tuple(dilation * row for row in rows)
    return sum(
        multiplicity
        for (a, b), multiplicity in distribution.items()
        if a <= bounds[0]
        and b <= bounds[1]
        and NUMBER_OF_UNIT_COLUMNS * dilation - a - b <= bounds[2]
    )


def multiply_by_linear(
    polynomial: list[Fraction], constant: int
) -> list[Fraction]:
    """Return polynomial*(n+constant), coefficients in ascending order."""

    result = [Fraction(0) for _ in range(len(polynomial) + 1)]
    for degree, coefficient in enumerate(polynomial):
        result[degree] += constant * coefficient
        result[degree + 1] += coefficient
    return result


def interpolate_monomial(samples: list[int]) -> list[Fraction]:
    """Interpolate degree <=14 in the Newton binomial basis, exactly."""

    assert len(samples) == DIMENSION + 1
    differences = list(samples)
    newton_coefficients: list[int] = []
    while differences:
        newton_coefficients.append(differences[0])
        differences = [
            differences[index + 1] - differences[index]
            for index in range(len(differences) - 1)
        ]

    result = [Fraction(0) for _ in range(DIMENSION + 1)]
    binomial_basis = [Fraction(1)]
    for order, newton_coefficient in enumerate(newton_coefficients):
        if order:
            binomial_basis = [
                coefficient / order
                for coefficient in multiply_by_linear(
                    binomial_basis, -(order - 1)
                )
            ]
        for degree, coefficient in enumerate(binomial_basis):
            result[degree] += newton_coefficient * coefficient
    return result


def evaluate_polynomial(coefficients: list[Fraction], n: int) -> Fraction:
    value = Fraction(0)
    for coefficient in reversed(coefficients):
        value = value * n + coefficient
    return value


def hstar_from_values(values: list[int]) -> list[int]:
    assert len(values) >= DIMENSION + 1
    return [
        sum(
            (-1) ** index
            * math.comb(DIMENSION + 1, index)
            * values[degree - index]
            for index in range(degree + 1)
        )
        for degree in range(DIMENSION + 1)
    ]


def linear_cancellation_ratio(
    hstar: list[int], linear_coefficient: Fraction
) -> Fraction:
    """Ratio negative/positive in the h*-expansion of the linear term."""

    harmonic = sum(
        (Fraction(1, denominator) for denominator in range(1, DIMENSION + 1)),
        Fraction(0),
    )
    terms = [Fraction(hstar[0]) * harmonic]
    terms.extend(
        Fraction(
            (-1) ** (index - 1) * hstar[index],
            DIMENSION * math.comb(DIMENSION - 1, index - 1),
        )
        for index in range(1, DIMENSION + 1)
    )
    positive = sum((term for term in terms if term > 0), Fraction(0))
    negative = sum((-term for term in terms if term < 0), Fraction(0))
    assert positive - negative == linear_coefficient
    return negative / positive


def encode_fraction(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def main() -> None:
    capped_rows: list[dict[str, object]] = []
    for caps in combinations_with_replacement(CAP_VALUES, 3):
        composition_count = l1_by_compositions(caps)
        assignment_count = l1_by_assignments(caps)
        assert composition_count == assignment_count
        capped_rows.append({"caps": list(caps), "L1": composition_count})

    survivors = [row for row in capped_rows if row["L1"] == TARGET_L1]
    minimum = min(capped_rows, key=lambda row: int(row["L1"]))
    maximum = max(capped_rows, key=lambda row: int(row["L1"]))

    # The finite orbit space has C(5+3-1,3)=35 elements.  Its least element
    # under coordinatewise inclusion is (3,3,3), so the computed minimum also
    # supplies the monotonic lower bound for every uncapped r_i >= 3.
    assert len(capped_rows) == 35
    assert minimum == {"caps": [3, 3, 3], "L1": 1050}
    assert maximum == {"caps": [7, 7, 7], "L1": 2187}
    assert len({int(row["L1"]) for row in capped_rows}) == 35
    assert survivors == []
    assert 1050 > TARGET_L1

    payload = {
        "target_L1": TARGET_L1,
        "number_of_unordered_capped_triples": len(capped_rows),
        "minimum": minimum,
        "maximum": maximum,
        "survivors": survivors,
        "rows": capped_rows,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    digest = sha256(encoded).hexdigest()
    assert digest == EXPECTED_PAYLOAD_SHA256

    # Exact raw counts for n=0,...,16.  The distribution depends only on n,
    # and is therefore computed once and queried for every canonical row
    # representative.  This DP is separate from both L(1) enumerators above.
    distributions = {
        dilation: aggregate_distribution(dilation)
        for dilation in range(max(HELD_OUT_DILATIONS) + 1)
    }
    polynomial_rows: list[dict[str, object]] = []
    negative_coefficients = 0
    negative_polynomials = 0
    smallest_coefficient: tuple[
        Fraction, tuple[int, int, int], int
    ] | None = None
    largest_cancellation: tuple[
        Fraction, tuple[int, int, int], Fraction
    ] | None = None

    for rows_tuple in combinations_with_replacement(CAP_VALUES, 3):
        values = [
            table_count(rows_tuple, dilation, distributions[dilation])
            for dilation in range(max(HELD_OUT_DILATIONS) + 1)
        ]
        assert values[1] == l1_by_compositions(rows_tuple)
        coefficients = interpolate_monomial(values[: DIMENSION + 1])

        # Direct raw DP values at 15 and 16 were not used in interpolation.
        for held_out in HELD_OUT_DILATIONS:
            predicted = evaluate_polynomial(coefficients, held_out)
            assert predicted.denominator == 1
            assert predicted.numerator == values[held_out]

        assert coefficients[DIMENSION] > 0
        hstar = hstar_from_values(values)
        # Codegree three: one relative-interior lattice point at n=3.
        assert hstar[12] == 1
        assert hstar[13:] == [0, 0]

        row_negative_count = sum(coefficient < 0 for coefficient in coefficients)
        negative_coefficients += row_negative_count
        negative_polynomials += int(row_negative_count > 0)

        for degree, coefficient in enumerate(coefficients):
            candidate = (coefficient, rows_tuple, degree)
            if smallest_coefficient is None or candidate < smallest_coefficient:
                smallest_coefficient = candidate

        cancellation = linear_cancellation_ratio(hstar, coefficients[1])
        cancellation_candidate = (cancellation, rows_tuple, coefficients[1])
        if largest_cancellation is None or cancellation_candidate > largest_cancellation:
            largest_cancellation = cancellation_candidate

        polynomial_rows.append(
            {
                "rows": list(rows_tuple),
                "values_n0_to_n16": values,
                "hstar": hstar,
                "coefficients": [encode_fraction(value) for value in coefficients],
                "linear_cancellation_ratio": encode_fraction(cancellation),
            }
        )

    assert len(polynomial_rows) == 35
    assert negative_coefficients == 0
    assert negative_polynomials == 0
    assert smallest_coefficient == (
        Fraction(128114573, 29059430400),
        (3, 3, 3),
        14,
    )
    assert largest_cancellation == (
        Fraction(131174147, 131215991),
        (4, 4, 4),
        Fraction(317, 35),
    )

    full_payload = {
        "dimension": DIMENSION,
        "canonical_row_patterns": len(polynomial_rows),
        "held_out_dilations": list(HELD_OUT_DILATIONS),
        "negative_coefficients": negative_coefficients,
        "negative_polynomials": negative_polynomials,
        "smallest_coefficient": {
            "value": encode_fraction(smallest_coefficient[0]),
            "rows": list(smallest_coefficient[1]),
            "degree": smallest_coefficient[2],
        },
        "largest_linear_cancellation": {
            "ratio": encode_fraction(largest_cancellation[0]),
            "rows": list(largest_cancellation[1]),
            "linear_coefficient": encode_fraction(largest_cancellation[2]),
        },
        "polynomials": polynomial_rows,
    }
    full_encoded = json.dumps(
        full_payload, sort_keys=True, separators=(",", ":")
    ).encode()
    full_digest = sha256(full_encoded).hexdigest()
    if EXPECTED_FULL_PAYLOAD_SHA256:
        assert full_digest == EXPECTED_FULL_PAYLOAD_SHA256

    print("PASS")
    print(f"unordered_capped_triples={len(capped_rows)}")
    print(f"minimum={minimum}")
    print(f"maximum={maximum}")
    print(f"target={TARGET_L1}")
    print(f"survivors={len(survivors)}")
    print(f"L1_payload_sha256={digest}")
    print(f"canonical_polynomials={len(polynomial_rows)}")
    print(f"negative_polynomials={negative_polynomials}")
    print(f"negative_coefficients={negative_coefficients}")
    print(
        "smallest_coefficient="
        f"{encode_fraction(smallest_coefficient[0])} "
        f"rows={smallest_coefficient[1]} degree={smallest_coefficient[2]}"
    )
    print(
        "largest_linear_cancellation="
        f"{encode_fraction(largest_cancellation[0])} "
        f"rows={largest_cancellation[1]} "
        f"linear_coefficient={encode_fraction(largest_cancellation[2])}"
    )
    print(f"full_payload_sha256={full_digest}")


if __name__ == "__main__":
    main()
