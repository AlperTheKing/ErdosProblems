#!/usr/bin/env python3
"""Exact audit of P52's arc-sensitive spectral staircase."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable


Poly = dict[int, int]


STORED_WITNESSES = [
    {"p": 5, "G": 6, "Z": [0, 4, 9, 11, 12]},
    {"p": 9, "G": 18, "Z": [0, 6, 13, 29, 34, 38, 46, 48, 49]},
    {"p": 10, "G": 42, "Z": [0, 2, 14, 21, 29, 32, 45, 49, 54, 55]},
    {"p": 11, "G": 23, "Z": [0, 15, 22, 34, 43, 54, 70, 78, 80, 83, 84]},
    {
        "p": 12,
        "G": 24,
        "Z": [0, 13, 33, 38, 47, 78, 79, 86, 89, 101, 105, 107],
    },
]


def clean(poly: Poly) -> Poly:
    return {n: value for n, value in poly.items() if value}


def convolve(left: Poly, right: Poly) -> Poly:
    out: Poly = {}
    for i, ai in left.items():
        for j, bj in right.items():
            out[i + j] = out.get(i + j, 0) + ai * bj
    return clean(out)


def reciprocal(poly: Poly) -> Poly:
    return {-n: value for n, value in poly.items()}


def linear_combination(*terms: tuple[int, Poly]) -> Poly:
    out: Poly = {}
    for scale, poly in terms:
        for n, value in poly.items():
            out[n] = out.get(n, 0) + scale * value
    return clean(out)


def autocorrelation(poly: Poly) -> Poly:
    return convolve(poly, reciprocal(poly))


def poly_terms(poly: Poly) -> list[list[int]]:
    return [[n, poly[n]] for n in sorted(poly)]


def profile(poly: Poly) -> dict[str, int]:
    counts = Counter(poly.values())
    return {str(value): counts[value] for value in sorted(counts)}


def sidon_data(z: tuple[int, ...]) -> tuple[set[int], dict[int, int]] | None:
    sums: set[int] = set()
    ordered_sum_weights: dict[int, int] = {}
    for i, left in enumerate(z):
        for j in range(i, len(z)):
            value = left + z[j]
            if value in sums:
                return None
            sums.add(value)
            ordered_sum_weights[value] = 1 if i == j else 2

    differences: set[int] = set()
    for i, left in enumerate(z):
        for right in z[i + 1 :]:
            value = right - left
            if value in differences:
                return None
            differences.add(value)
    return differences, ordered_sum_weights


def valid_gap(
    differences: set[int], ordered_sum_weights: dict[int, int], gap: int
) -> bool:
    return not differences.intersection(gap + value for value in ordered_sum_weights)


def is_unimodal(values: list[int]) -> bool:
    for peak in range(len(values)):
        if all(values[i] <= values[i + 1] for i in range(peak)) and all(
            values[i] >= values[i + 1] for i in range(peak, len(values) - 1)
        ):
            return True
    return False


def staircase(z: tuple[int, ...], gap: int) -> tuple[Poly, list[int]]:
    width = z[-1]
    length = gap + 2 * width
    q: Poly = {}
    for value in z:
        q[width - value] = q.get(width - value, 0) + 1
        exponent = gap + width + value
        q[exponent] = q.get(exponent, 0) - 1
    q = clean(q)

    running = 0
    coefficients: list[int] = []
    for n in range(length + 1):
        running += q.get(n, 0)
        if n < length:
            coefficients.append(running)
    assert running == 0
    return q, coefficients


def tail_slacks(
    differences: set[int],
    ordered_sum_weights: dict[int, int],
    gap: int,
    length: int,
) -> list[int]:
    difference_at = [0] * (length + 1)
    sum_at = [0] * (length + 1)
    for value in differences:
        difference_at[value] = 1
    for value, weight in ordered_sum_weights.items():
        sum_at[gap + value] = weight

    tail_difference = 0
    tail_sum = 0
    twice_slack = [0] * length
    for n in range(length - 1, -1, -1):
        tail_difference += difference_at[n + 1]
        tail_sum += sum_at[n + 1]
        twice_slack[n] = tail_sum - 2 * tail_difference
    return twice_slack


def first_unimodality_backtrack(values: list[int]) -> dict[str, int] | None:
    for down in range(len(values) - 1):
        if values[down + 1] >= values[down]:
            continue
        for up in range(down + 1, len(values) - 1):
            if values[up + 1] > values[up]:
                return {
                    "decrease_at_curvature_index": down + 1,
                    "later_increase_at_curvature_index": up + 1,
                }
    return None


def full_audit(z_values: Iterable[int], gap: int, certificate: bool = False) -> dict:
    z = tuple(z_values)
    p = len(z)
    width = z[-1]
    length = gap + 2 * width
    data = sidon_data(z)
    assert data is not None
    differences, ordered_sum_weights = data
    assert valid_gap(differences, ordered_sum_weights, gap)

    newman = {value: 1 for value in z}
    difference_poly = convolve(newman, reciprocal(newman))
    sum_poly = {
        gap + value: weight for value, weight in ordered_sum_weights.items()
    }
    assert not set(difference_poly).intersection(sum_poly)
    assert profile(difference_poly) == {"1": p * (p - 1), str(p): 1}
    assert profile(sum_poly) == {"1": p, "2": p * (p - 1) // 2}
    assert autocorrelation(difference_poly) == autocorrelation(sum_poly)

    indices = [-value for value in z] + [gap + value for value in z]
    gram = [
        [difference_poly.get(right - left, 0) for right in indices]
        for left in indices
    ]
    block = [[p if i == j else 1 for j in range(p)] for i in range(p)]
    expected_gram = [
        block[i] + [0] * p if i < p else [0] * p + block[i - p]
        for i in range(2 * p)
    ]
    assert gram == expected_gram

    q, r_values = staircase(z, gap)
    r_poly = {n: value for n, value in enumerate(r_values)}
    assert convolve({0: 1, 1: -1}, r_poly) == q
    assert all(value > 0 for value in r_values)
    assert r_values == r_values[::-1]
    assert is_unimodal(r_values)

    r_autocorrelation = autocorrelation(r_poly)
    twice_t = linear_combination(
        (2, difference_poly), (-1, sum_poly), (-1, reciprocal(sum_poly))
    )
    laplacian = {-1: -1, 0: 2, 1: -1}
    assert twice_t == convolve(laplacian, r_autocorrelation)

    twice_slope = [
        r_autocorrelation.get(n, 0) - r_autocorrelation.get(n + 1, 0)
        for n in range(length)
    ]
    expected_slope = tail_slacks(
        differences, ordered_sum_weights, gap, length
    )
    assert twice_slope == expected_slope
    assert min(twice_slope) >= 0

    slope_unimodal = is_unimodal(twice_slope)
    assert twice_t[gap] == -1
    assert twice_t[width] == 2
    if gap < width:
        assert not slope_unimodal

    r_sum = sum(r_values)
    r_l2_squared = sum(value * value for value in r_values)
    assert r_sum == p * gap + 2 * sum(z)
    assert r_l2_squared == p * p * gap + 2 * sum(
        (2 * p - 2 * i - 1) * value for i, value in enumerate(z)
    )
    assert r_sum * r_sum <= length * r_l2_squared

    result = {
        "p": p,
        "G": gap,
        "W": width,
        "L": length,
        "difference_profile": profile(difference_poly),
        "sum_profile": profile(sum_poly),
        "aperiodic_autocorrelation_equal": True,
        "toeplitz_gram_blocks": "((p-1)I+J) direct-sum ((p-1)I+J)",
        "toeplitz_gram_spectrum": {
            str(2 * p - 1): 2,
            str(p - 1): 2 * p - 2,
        },
        "R_sum": r_sum,
        "R_l2_squared": r_l2_squared,
        "fejer_effective_length": str(Fraction(r_sum * r_sum, r_l2_squared)),
        "fejer_bound_slack": length * r_l2_squared - r_sum * r_sum,
        "minimum_twice_tail_slack": min(twice_slope),
        "tail_domination_holds": True,
        "single_peak_slope_candidate": slope_unimodal,
        "first_slope_backtrack": first_unimodality_backtrack(twice_slope),
        "endpoint_curvatures_twice": {"at_G": -1, "at_W": 2},
    }
    if certificate:
        result["certificate"] = {
            "Z": list(z),
            "P_exponents": list(z),
            "A_terms": poly_terms(difference_poly),
            "B_terms": poly_terms(sum_poly),
            "Q_terms": poly_terms(q),
            "R_coefficients": r_values,
            "twice_H_coefficients_nonnegative_lags": [
                r_autocorrelation.get(n, 0) for n in range(length + 1)
            ],
            "twice_slope": twice_slope,
            "twice_curvature_nonnegative_lags": [
                twice_t.get(n, 0) for n in range(length + 1)
            ],
            "toeplitz_gram": gram,
        }
    return result


def exhaustive_audit(max_width: int) -> dict:
    ruler_count = 0
    valid_pair_count = 0
    valid_pair_count_p_ge_3 = 0
    candidate_failure_count = 0
    minimum_twice_tail_slack: int | None = None
    smallest_counterexample: tuple[int, int, int, tuple[int, ...]] | None = None
    by_p: dict[int, dict[str, int]] = defaultdict(
        lambda: {"sidon_rulers": 0, "valid_pairs": 0, "candidate_failures": 0}
    )

    for width in range(1, max_width + 1):
        interior = range(1, width)
        for interior_size in range(width):
            for middle in combinations(interior, interior_size):
                z = (0, *middle, width)
                data = sidon_data(z)
                if data is None:
                    continue
                differences, ordered_sum_weights = data
                p = len(z)
                ruler_count += 1
                by_p[p]["sidon_rulers"] += 1

                for gap in range(1, width):
                    if not valid_gap(differences, ordered_sum_weights, gap):
                        continue
                    valid_pair_count += 1
                    by_p[p]["valid_pairs"] += 1
                    if p >= 3:
                        valid_pair_count_p_ge_3 += 1

                    length = gap + 2 * width
                    twice_slack = tail_slacks(
                        differences, ordered_sum_weights, gap, length
                    )
                    local_minimum = min(twice_slack)
                    assert local_minimum >= 0
                    if minimum_twice_tail_slack is None:
                        minimum_twice_tail_slack = local_minimum
                    else:
                        minimum_twice_tail_slack = min(
                            minimum_twice_tail_slack, local_minimum
                        )

                    # At G the curvature is -1, while at W it is +2.
                    assert gap < width
                    candidate_failure_count += 1
                    by_p[p]["candidate_failures"] += 1
                    if p >= 3:
                        key = (p, width, gap, z)
                        if smallest_counterexample is None or key < smallest_counterexample:
                            smallest_counterexample = key

    assert smallest_counterexample is not None
    p, width, gap, z = smallest_counterexample
    certificate = full_audit(z, gap, certificate=True)
    return {
        "max_width": max_width,
        "endpoint_normalized_sidon_rulers": ruler_count,
        "valid_pairs_with_1_le_G_lt_W": valid_pair_count,
        "valid_pairs_with_p_ge_3": valid_pair_count_p_ge_3,
        "tail_domination_checks": valid_pair_count,
        "minimum_twice_tail_slack": minimum_twice_tail_slack,
        "single_peak_slope_candidate_failures": candidate_failure_count,
        "all_valid_pairs_fail_single_peak_candidate": (
            candidate_failure_count == valid_pair_count
        ),
        "by_p": {str(p): by_p[p] for p in sorted(by_p)},
        "lexicographically_smallest_p_ge_3_counterexample": certificate,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=18)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("audit_results.json"),
    )
    args = parser.parse_args()

    result = {
        "candidate": {
            "name": "single-peak autocorrelation slope",
            "statement": (
                "s_n=H_n-H_{n+1} is unimodal for the structured staircase R"
            ),
            "consequence": "G >= W, since 2t_G=-1 and 2t_W=2",
        },
        "stored_witnesses": [
            full_audit(record["Z"], record["G"]) for record in STORED_WITNESSES
        ],
        "exhaustive": exhaustive_audit(args.max_width),
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
