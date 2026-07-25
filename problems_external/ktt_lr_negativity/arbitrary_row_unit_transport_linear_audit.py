#!/usr/bin/env python3
"""Hostile exact audit of the arbitrary-row unit-column linear formula.

For positive row margins r=(r1,r2,r3), N=sum(r)>k, and column margins
(N-k,1^k), this checker reconstructs the degree-2k Ehrhart polynomial from
raw projected-table counts.  It does not use the proposed linear formula in
the counting engine.  Two further dilations are held out from interpolation.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement
import json
import math


CALIBRATION_MAX_K = 7
EXPECTED_PAYLOAD_SHA256 = (
    "cd2314207b507e7f32d25b4d34c17ccc1a2370403da3cc14036217356ee8dc85"
)
EXPLICIT_ASYMMETRIC_CASES = (
    ((1, 2, 5), 7),
    ((1, 4, 4), 7),
    ((2, 2, 4), 7),
    ((2, 3, 3), 7),
)


def aggregate_distribution(k: int, n: int) -> dict[tuple[int, int], int]:
    """Distribution of the first two row totals in k labelled n-columns."""

    kernel = [(x, y) for x in range(n + 1) for y in range(n - x + 1)]
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for _ in range(k):
        updated: defaultdict[tuple[int, int], int] = defaultdict(int)
        for (a, b), multiplicity in states.items():
            for x, y in kernel:
                updated[(a + x, b + y)] += multiplicity
        states = dict(updated)
    return states


def full_count(
    rows: tuple[int, int, int],
    k: int,
    n: int,
    distribution: dict[tuple[int, int], int],
) -> int:
    bounds = tuple(n * row for row in rows)
    return sum(
        multiplicity
        for (a, b), multiplicity in distribution.items()
        if a <= bounds[0]
        and b <= bounds[1]
        and k * n - a - b <= bounds[2]
    )


def single_violation_count(
    cap: int,
    n: int,
    distribution: dict[tuple[int, int], int],
) -> int:
    return sum(
        multiplicity
        for (a, _b), multiplicity in distribution.items()
        if a > cap * n
    )


def pair_violation_count(
    first_cap: int,
    second_cap: int,
    n: int,
    distribution: dict[tuple[int, int], int],
) -> int:
    return sum(
        multiplicity
        for (a, b), multiplicity in distribution.items()
        if a > first_cap * n and b > second_cap * n
    )


def first_differences(values: list[int]) -> list[int]:
    firsts: list[int] = []
    row = values[:]
    while row:
        firsts.append(row[0])
        row = [right - left for left, right in zip(row, row[1:])]
    return firsts


def linear_from_newton(firsts: list[int]) -> Fraction:
    return sum(
        (
            Fraction((-1) ** (order - 1), order) * firsts[order]
            for order in range(1, len(firsts))
        ),
        Fraction(0),
    )


def newton_evaluate(firsts: list[int], n: int) -> int:
    return sum(
        coefficient * math.comb(n, order)
        for order, coefficient in enumerate(firsts)
    )


def F(k: int, cap: int) -> Fraction:
    if cap >= k:
        return Fraction(0)
    return sum(
        (
            Fraction(t, 2 * (cap + t))
            for t in range(1, k - cap + 1)
        ),
        Fraction(0),
    )


def proposed_linear(rows: tuple[int, int, int], k: int) -> Fraction:
    return (
        Fraction(3 * k, 2)
        - sum((F(k, row) for row in rows), Fraction(0))
        - sum(
            (
                F(k, rows[first] + rows[second])
                for first, second in ((0, 1), (0, 2), (1, 2))
            ),
            Fraction(0),
        )
    )


def deficit_bound(rows: tuple[int, int, int], k: int) -> int:
    """Twice the elementary upper bound on all six F terms."""

    delta = sum(rows) - k
    assert delta >= 1
    # The pair complementary to row i has deficit
    # k-(r_j+r_l)=r_i-delta.
    return sum(
        max(k - row, 0) + max(row - delta, 0) for row in rows
    )


def zero_extended_binomial(top: int, bottom: int) -> int:
    if top < 0 or bottom < 0 or bottom > top:
        return 0
    return math.comb(top, bottom)


def vandermonde_term(k: int, i: int, j: int) -> Fraction:
    """The finite identity D_(k,i,j) in the hostile audit."""

    return sum(
        (
            Fraction(
                (-1) ** h
                * math.comb(i + j, h)
                * zero_extended_binomial(
                    2 * k - i - j - 1 - h, k - j - 1 - h
                ),
                (2 * k - h) * math.comb(2 * k - h - 1, k - j - 1),
            )
            for h in range(i + j + 1)
        ),
        Fraction(0),
    )


def main() -> None:
    full_cases = 0
    single_checks = 0
    pair_checks = 0
    held_out_checks = 0
    minimum_linear: tuple[Fraction, tuple[int, int, int], int] | None = None
    explicit_records: list[dict[str, object]] = []
    uncapped_records: list[dict[str, object]] = []
    vandermonde_checks = 0

    # Independent exact calibration of the terminating identity used in the
    # symbolic two-cap proof.  This is not used by the raw table DP.
    for k in range(1, 13):
        for j in range(k):
            for i in range(k - j):
                expected = (
                    Fraction(
                        math.factorial(j) * math.factorial(k - j - 1),
                        2 * math.factorial(k),
                    )
                    if i == 0
                    else Fraction(0)
                )
                assert vandermonde_term(k, i, j) == expected
                vandermonde_checks += 1

    for k in range(1, CALIBRATION_MAX_K + 1):
        degree = 2 * k
        distributions = [
            aggregate_distribution(k, n) for n in range(degree + 3)
        ]

        # Check the two half-open cap coefficient lemmas separately.
        for cap in range(1, k):
            values = [
                single_violation_count(cap, n, distributions[n])
                for n in range(degree + 3)
            ]
            firsts = first_differences(values[: degree + 1])
            assert linear_from_newton(firsts) == F(k, cap)
            for held_out in (degree + 1, degree + 2):
                assert newton_evaluate(firsts, held_out) == values[held_out]
            single_checks += 1

        for first_cap in range(1, k):
            for second_cap in range(first_cap, k - first_cap):
                values = [
                    pair_violation_count(
                        first_cap, second_cap, n, distributions[n]
                    )
                    for n in range(degree + 3)
                ]
                firsts = first_differences(values[: degree + 1])
                assert linear_from_newton(firsts) == -F(
                    k, first_cap + second_cap
                )
                for held_out in (degree + 1, degree + 2):
                    assert newton_evaluate(firsts, held_out) == values[held_out]
                pair_checks += 1

        # Cap invariance reduces arbitrary rows to 1<=ri<=k.
        for rows in combinations_with_replacement(range(1, k + 1), 3):
            if sum(rows) <= k:
                continue
            values = [
                full_count(rows, k, n, distributions[n])
                for n in range(degree + 3)
            ]
            firsts = first_differences(values[: degree + 1])
            assert firsts[-1] != 0
            linear = linear_from_newton(firsts)
            assert linear == proposed_linear(rows, k)
            assert linear > 0
            bound = deficit_bound(rows, k)
            assert bound <= 3 * (k - 1)
            assert linear >= Fraction(3, 2)
            for held_out in (degree + 1, degree + 2):
                assert newton_evaluate(firsts, held_out) == values[held_out]
                held_out_checks += 1
            full_cases += 1
            candidate = (linear, rows, k)
            if minimum_linear is None or candidate < minimum_linear:
                minimum_linear = candidate
            if (rows, k) in EXPLICIT_ASYMMETRIC_CASES:
                explicit_records.append(
                    {
                        "rows": list(rows),
                        "k": k,
                        "degree": degree,
                        "linear": str(linear),
                        "held_out": [degree + 1, degree + 2],
                        "held_out_values": [values[-2], values[-1]],
                    }
                )

        # Explicitly test that rows above k have the same entire count as
        # their capped representatives at every interpolation/held-out point.
        uncapped = (1, k, k + 4)
        capped = tuple(min(row, k) for row in uncapped)
        uncapped_values = [
            full_count(uncapped, k, n, distributions[n])
            for n in range(degree + 3)
        ]
        capped_values = [
            full_count(capped, k, n, distributions[n])
            for n in range(degree + 3)
        ]
        assert uncapped_values == capped_values
        assert proposed_linear(uncapped, k) == proposed_linear(capped, k)
        uncapped_records.append(
            {
                "k": k,
                "uncapped": list(uncapped),
                "capped": list(capped),
                "number_of_checked_dilations": degree + 3,
            }
        )

    assert minimum_linear is not None
    assert len(explicit_records) == len(EXPLICIT_ASYMMETRIC_CASES)

    payload = {
        "calibration_max_k": CALIBRATION_MAX_K,
        "full_row_cases": full_cases,
        "single_cap_checks": single_checks,
        "pair_cap_checks": pair_checks,
        "held_out_full_checks": held_out_checks,
        "vandermonde_checks_through_k12": vandermonde_checks,
        "minimum_linear": {
            "value": str(minimum_linear[0]),
            "rows": list(minimum_linear[1]),
            "k": minimum_linear[2],
        },
        "explicit_asymmetric_cases": explicit_records,
        "uncapped_cap_invariance": uncapped_records,
        "formula": "3k/2-sum_i F_k(ri)-sum_i<j F_k(ri+rj)",
        "F": "1/2 sum_(t=1)^(k-x) t/(x+t), zero for x>=k",
        "uniform_lower_bound": "linear coefficient >= 3/2",
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    digest = sha256(encoded).hexdigest()
    if EXPECTED_PAYLOAD_SHA256:
        assert digest == EXPECTED_PAYLOAD_SHA256

    print("PASS")
    print(f"calibration_max_k={CALIBRATION_MAX_K}")
    print(f"full_row_cases={full_cases}")
    print(f"single_cap_checks={single_checks}")
    print(f"pair_cap_checks={pair_checks}")
    print(f"held_out_full_checks={held_out_checks}")
    print(f"vandermonde_checks_through_k12={vandermonde_checks}")
    print(
        f"minimum_linear={minimum_linear[0]} "
        f"rows={minimum_linear[1]} k={minimum_linear[2]}"
    )
    for record in explicit_records:
        print(
            f"asymmetric rows={tuple(record['rows'])} k={record['k']} "
            f"linear={record['linear']} held_out={tuple(record['held_out'])}"
        )
    print(f"payload_sha256={digest}")


if __name__ == "__main__":
    main()
