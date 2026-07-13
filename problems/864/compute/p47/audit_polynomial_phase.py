#!/usr/bin/env python3
"""Exact audits for P47's equal-modulus polynomial separation lemma."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


Poly = dict[int, int]


SIGNED_RULERS = [
    {"p": 5, "G": 6, "Z": [0, 4, 9, 11, 12]},
    {"p": 9, "G": 18, "Z": [0, 6, 13, 29, 34, 38, 46, 48, 49]},
    {"p": 10, "G": 42, "Z": [0, 2, 14, 21, 29, 32, 45, 49, 54, 55]},
    {"p": 11, "G": 23, "Z": [0, 15, 22, 34, 43, 54, 70, 78, 80, 83, 84]},
    {"p": 12, "G": 24, "Z": [0, 13, 33, 38, 47, 78, 79, 86, 89, 101, 105, 107]},
]


SINGER_MODELS = [
    {"p": 3, "q": 7, "Z_even": [0, 8, 10]},
    {"p": 4, "q": 13, "Z_even": [0, 14, 16, 22]},
    {"p": 6, "q": 31, "Z_even": [0, 4, 10, 12, 32, 48]},
]


def convolve(left: Poly, right: Poly) -> Poly:
    out: Poly = {}
    for i, ai in left.items():
        for j, bj in right.items():
            out[i + j] = out.get(i + j, 0) + ai * bj
    return {n: c for n, c in out.items() if c}


def reciprocal(poly: Poly) -> Poly:
    return {-n: c for n, c in poly.items()}


def shift(poly: Poly, amount: int) -> Poly:
    return {n + amount: c for n, c in poly.items()}


def autocorrelation(poly: Poly) -> Poly:
    return convolve(poly, reciprocal(poly))


def profile(poly: Poly) -> dict[str, int]:
    counts = Counter(poly.values())
    return {str(value): counts[value] for value in sorted(counts)}


def l1(poly: Poly) -> int:
    return sum(poly.values())


def l2_squared(poly: Poly) -> int:
    return sum(value * value for value in poly.values())


def first_mismatch(left: Poly, right: Poly) -> dict[str, int] | None:
    for exponent in sorted(set(left) | set(right), key=lambda n: (abs(n), n)):
        a = left.get(exponent, 0)
        b = right.get(exponent, 0)
        if a != b:
            return {"lag": exponent, "left": a, "right": b}
    return None


def cyclic_convolve(left: list[int], right: list[int]) -> list[int]:
    modulus = len(left)
    assert len(right) == modulus
    out = [0] * modulus
    for i, ai in enumerate(left):
        if ai == 0:
            continue
        for j, bj in enumerate(right):
            if bj:
                out[(i + j) % modulus] += ai * bj
    return out


def cyclic_reciprocal(values: list[int]) -> list[int]:
    modulus = len(values)
    out = [0] * modulus
    for i, value in enumerate(values):
        out[(-i) % modulus] = value
    return out


def cyclic_shift(values: list[int], amount: int) -> list[int]:
    modulus = len(values)
    out = [0] * modulus
    for i, value in enumerate(values):
        out[(i + amount) % modulus] = value
    return out


def cyclic_autocorrelation(values: list[int]) -> list[int]:
    return cyclic_convolve(values, cyclic_reciprocal(values))


def dict_from_array(values: list[int]) -> Poly:
    return {i: value for i, value in enumerate(values) if value}


def audit_signed_ruler(record: dict[str, object]) -> dict[str, object]:
    p = int(record["p"])
    gap = int(record["G"])
    ruler = [int(z) for z in record["Z"]]
    width = ruler[-1]
    length = gap + 2 * width
    newman = {z: 1 for z in ruler}
    difference_poly = convolve(newman, reciprocal(newman))
    sum_poly = shift(convolve(newman, newman), gap)

    sums = Counter(ruler[i] + ruler[j] for i in range(p) for j in range(i, p))
    positive_differences = Counter(
        ruler[j] - ruler[i] for i in range(p) for j in range(i + 1, p)
    )
    intersection = sorted(set(difference_poly) & set(sum_poly))
    expected_difference_profile = {"1": p * (p - 1), str(p): 1}
    expected_sum_profile = {"1": p, "2": p * (p - 1) // 2}

    assert len(ruler) == p and ruler[0] == 0
    assert len(set(ruler)) == p
    assert all(count == 1 for count in sums.values())
    assert all(count == 1 for count in positive_differences.values())
    assert not intersection
    assert profile(difference_poly) == expected_difference_profile
    assert profile(sum_poly) == expected_sum_profile
    assert difference_poly.get(0) == p
    assert sum_poly.get(0, 0) == 0
    assert l1(difference_poly) == l1(sum_poly) == p * p
    assert l2_squared(difference_poly) == l2_squared(sum_poly) == 2 * p * p - p
    assert autocorrelation(difference_poly) == autocorrelation(sum_poly)

    overlap_moments = [
        sum(
            (n**degree) * difference_poly.get(n, 0) * sum_poly.get(n, 0)
            for n in set(difference_poly) | set(sum_poly)
        )
        for degree in range(6)
    ]
    assert overlap_moments == [0] * 6

    return {
        "p": p,
        "G": gap,
        "W": width,
        "L": length,
        "difference_range": [min(difference_poly), max(difference_poly)],
        "sum_range": [min(sum_poly), max(sum_poly)],
        "difference_support": len(difference_poly),
        "sum_support": len(sum_poly),
        "difference_profile": profile(difference_poly),
        "sum_profile": profile(sum_poly),
        "zero_coefficients": {
            "difference": difference_poly.get(0, 0),
            "sum": sum_poly.get(0, 0),
        },
        "l1": l1(difference_poly),
        "l2_squared": l2_squared(difference_poly),
        "aperiodic_autocorrelation_equal": True,
        "overlap_moments_degrees_0_to_5": overlap_moments,
    }


def audit_generic_family(p: int) -> dict[str, object]:
    q = p * p - p + 1
    left = {2 * j: 1 for j in range(q)}
    left[q - 1] = p
    right = shift(left, 1)
    ambient_slots = 2 * q

    assert not (set(left) & set(right))
    assert autocorrelation(left) == autocorrelation(right)
    assert set(left) | set(right) == set(range(ambient_slots))
    assert profile(left) == profile(right) == {"1": p * (p - 1), str(p): 1}
    assert l1(left) == l1(right) == p * p
    assert l2_squared(left) == l2_squared(right) == 2 * p * p - p
    assert left == {2 * (q - 1) - n: value for n, value in left.items()}

    return {
        "p": p,
        "q": q,
        "ambient_slots": ambient_slots,
        "max_frequency": ambient_slots - 1,
        "max_frequency_over_p_squared": str(Fraction(ambient_slots - 1, p * p)),
        "left_support": len(left),
        "right_support": len(right),
        "coefficient_profile": profile(left),
        "l1": l1(left),
        "l2_squared": l2_squared(left),
        "supports_partition_every_slot": True,
        "aperiodic_autocorrelation_equal": True,
        "right_is_x_times_left": True,
        "left_is_palindromic": True,
    }


def audit_zero_flip_family(p: int) -> dict[str, object]:
    u = {2 * i: 1 for i in range(p)}
    v = {2 * p * j: j + 1 for j in range(p)}
    left = convolve(u, v)
    exponent_shift = 2 * p * (p - 1) + 1
    right = shift(convolve(u, reciprocal(v)), exponent_shift)
    ambient_slots = 2 * p * p

    assert not (set(left) & set(right))
    assert set(left) | set(right) == set(range(ambient_slots))
    assert autocorrelation(left) == autocorrelation(right)
    assert profile(left) == profile(right) == {
        str(value): p for value in range(1, p + 1)
    }
    assert right != shift(left, 1)

    return {
        "p": p,
        "ambient_slots": ambient_slots,
        "max_frequency": ambient_slots - 1,
        "max_frequency_over_p_squared": str(Fraction(ambient_slots - 1, p * p)),
        "left_support": len(left),
        "right_support": len(right),
        "coefficient_profile": profile(left),
        "supports_partition_every_slot": True,
        "aperiodic_autocorrelation_equal": True,
        "monomial_translate": False,
        "factorization": "U*V versus shifted U*V#",
    }

def audit_p3_exact_profile_partner() -> dict[str, object]:
    p = 3
    u = {0: 1, 1: 1, 3: 1}
    v = {0: 1, 2: 1, 3: 1, 4: -1, 7: 1}
    v_star = shift(reciprocal(v), 7)
    left = convolve(u, v)
    right = shift(convolve(u, v_star), 4)

    assert left == {0: 1, 1: 1, 2: 1, 3: 3, 6: 1, 8: 1, 10: 1}
    assert right == {4: 1, 5: 1, 9: 2, 11: 2, 12: 2, 14: 1}
    assert not (set(left) & set(right))
    assert autocorrelation(left) == autocorrelation(right)
    assert profile(left) == {"1": 6, "3": 1}
    assert profile(right) == {"1": 3, "2": 3}
    assert shift(reciprocal(left), 10) != left

    return {
        "p": p,
        "endpoint": 14,
        "difference_profile": profile(left),
        "sum_profile": profile(right),
        "supports_disjoint": True,
        "aperiodic_autocorrelation_equal": True,
        "left_is_self_reciprocal": False,
        "factorization": "U*V versus shifted U*V#",
    }

def audit_singer_model(record: dict[str, object]) -> dict[str, object]:
    p = int(record["p"])
    q = int(record["q"])
    modulus = 2 * q
    ruler = sorted(int(z) for z in record["Z_even"])
    values = [0] * modulus
    for z in ruler:
        values[z] = 1

    cyclic_difference = cyclic_convolve(values, cyclic_reciprocal(values))
    cyclic_sum = cyclic_shift(cyclic_convolve(values, values), q)
    cyclic_difference_poly = dict_from_array(cyclic_difference)
    cyclic_sum_poly = dict_from_array(cyclic_sum)

    assert not (set(cyclic_difference_poly) & set(cyclic_sum_poly))
    assert profile(cyclic_difference_poly) == {"1": p * (p - 1), str(p): 1}
    assert profile(cyclic_sum_poly) == {"1": p, "2": p * (p - 1) // 2}
    assert cyclic_autocorrelation(cyclic_difference) == cyclic_autocorrelation(cyclic_sum)

    cyclic_as_ordinary_difference = autocorrelation(cyclic_difference_poly)
    cyclic_as_ordinary_sum = autocorrelation(cyclic_sum_poly)
    mismatch = first_mismatch(cyclic_as_ordinary_difference, cyclic_as_ordinary_sum)
    assert mismatch is not None

    newman = {z: 1 for z in ruler}
    ordinary_difference = convolve(newman, reciprocal(newman))
    ordinary_sum = shift(convolve(newman, newman), q)
    width = max(ruler) - min(ruler)
    ordinary_length = q + 2 * width
    assert not (set(ordinary_difference) & set(ordinary_sum))
    assert autocorrelation(ordinary_difference) == autocorrelation(ordinary_sum)

    return {
        "p": p,
        "q": q,
        "modulus": modulus,
        "cyclic_profiles": {
            "difference": profile(cyclic_difference_poly),
            "sum": profile(cyclic_sum_poly),
        },
        "cyclic_supports_disjoint": True,
        "periodic_autocorrelation_equal": True,
        "aperiodic_autocorrelation_equal_after_reduction": False,
        "first_aperiodic_mismatch": mismatch,
        "ordinary_unreduced_pair": {
            "W": width,
            "G": q,
            "L": ordinary_length,
            "L_over_p_squared": str(Fraction(ordinary_length, p * p)),
            "supports_disjoint": True,
            "aperiodic_autocorrelation_equal": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("audit_results.json"),
    )
    args = parser.parse_args()

    result = {
        "signed_rulers": [audit_signed_ruler(record) for record in SIGNED_RULERS],
        "generic_all_circle_family": [
            audit_generic_family(p) for p in [3, 4, 6, 10, 50]
        ],
        "nontrivial_zero_flip_family": [
            audit_zero_flip_family(p) for p in [3, 4, 10]
        ],
        "p3_exact_profile_partner": audit_p3_exact_profile_partner(),
        "singer_cyclic_models": [
            audit_singer_model(record) for record in SINGER_MODELS
        ],
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
