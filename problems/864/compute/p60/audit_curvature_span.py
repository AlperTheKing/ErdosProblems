#!/usr/bin/env python3
"""Exact candidate audit for P60's curvature-inversion span."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable

import sympy as sp


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


def sidon_data(z: tuple[int, ...]) -> tuple[set[int], dict[int, int]] | None:
    sums: set[int] = set()
    weighted_sums: dict[int, int] = {}
    for i, left in enumerate(z):
        for j in range(i, len(z)):
            value = left + z[j]
            if value in sums:
                return None
            sums.add(value)
            weighted_sums[value] = 1 if i == j else 2

    differences: set[int] = set()
    for i, left in enumerate(z):
        for right in z[i + 1 :]:
            value = right - left
            if value in differences:
                return None
            differences.add(value)
    return differences, weighted_sums


def valid_gap(
    differences: set[int], weighted_sums: dict[int, int], gap: int
) -> bool:
    return not differences.intersection(gap + value for value in weighted_sums)


def staircase(z: tuple[int, ...], gap: int) -> list[int]:
    width = z[-1]
    length = gap + 2 * width
    q = defaultdict(int)
    for value in z:
        q[width - value] += 1
        q[gap + width + value] -= 1

    running = 0
    r: list[int] = []
    for n in range(length + 1):
        running += q[n]
        if n < length:
            r.append(running)
    assert running == 0
    assert r == r[::-1]
    assert min(r) == 1
    return r


def positive_autocorrelation(values: list[int]) -> list[int]:
    length = len(values)
    return [
        sum(values[j] * values[j + lag] for j in range(length - lag))
        for lag in range(length + 1)
    ]


def tail_slack(
    differences: set[int], weighted_sums: dict[int, int], gap: int, length: int
) -> list[int]:
    difference_at = [0] * (length + 1)
    sum_at = [0] * (length + 1)
    for value in differences:
        difference_at[value] = 2
    for value, weight in weighted_sums.items():
        sum_at[gap + value] = weight

    difference_tail = 0
    sum_tail = 0
    slack = [0] * length
    for n in range(length - 1, -1, -1):
        difference_tail += difference_at[n + 1]
        sum_tail += sum_at[n + 1]
        slack[n] = sum_tail - difference_tail
    return slack


def pair_count_slack(z: tuple[int, ...], gap: int, n: int) -> int:
    return sum(
        abs(left - right) <= n < gap + left + right
        for left in z
        for right in z
    )


def sign(value: int) -> int:
    return (value > 0) - (value < 0)


def sign_changes(values: Iterable[int]) -> int:
    signs = [sign(value) for value in values if value]
    return sum(left != right for left, right in zip(signs, signs[1:]))


def sign_runs(values: Iterable[int]) -> list[int]:
    signs = [sign(value) for value in values if value]
    if not signs:
        return []
    runs = [signs[0]]
    for value in signs[1:]:
        if value != runs[-1]:
            runs.append(value)
    return runs


def routh_right_half_plane_count(coefficients: list[int]) -> int:
    """Return the open-right-half-plane root count by an exact Routh table."""
    degree = len(coefficients) - 1
    columns = (degree + 2) // 2
    values = [Fraction(value) for value in coefficients]
    even_row = values[0::2]
    odd_row = values[1::2]
    rows = [
        even_row + [Fraction(0)] * (columns - len(even_row)),
        odd_row + [Fraction(0)] * (columns - len(odd_row)),
    ]
    for _ in range(2, degree + 1):
        two_above = rows[-2]
        one_above = rows[-1]
        if one_above[0] == 0:
            raise ArithmeticError("zero Routh pivot")
        row = [
            (
                one_above[0] * two_above[j + 1]
                - two_above[0] * one_above[j + 1]
            )
            / one_above[0]
            for j in range(columns - 1)
        ] + [Fraction(0)]
        if not any(row):
            raise ArithmeticError("zero Routh row")
        rows.append(row)

    first_column_signs = [sign(row[0]) for row in rows]
    assert 0 not in first_column_signs
    return sum(
        left != right
        for left, right in zip(first_column_signs, first_column_signs[1:])
    )


def exact_newman_zero_count(z: tuple[int, ...]) -> dict[str, int | bool | str]:
    """Count roots of P in |x|<1 via an exact Cayley/Routh calculation."""
    t = sp.symbols("t", real=True)
    width = z[-1]
    transformed = sp.Poly(
        sum((1 + t) ** value * (1 - t) ** (width - value) for value in z),
        t,
        domain=sp.ZZ,
    )

    # Degree loss is exactly a root of P at -1, hence a unit-circle root.
    if transformed.degree() < width:
        return {
            "unit_circle_root": True,
            "root_at_minus_one": True,
            "inside_count_defined": False,
        }

    y = sp.symbols("y", real=True)
    real_part = 0
    imag_part = 0
    for (power,), coefficient in transformed.terms():
        if power % 2 == 0:
            real_part += coefficient * (-1) ** (power // 2) * y**power
        else:
            imag_part += coefficient * (-1) ** ((power - 1) // 2) * y**power
    common = sp.gcd(sp.Poly(real_part, y), sp.Poly(imag_part, y))
    imaginary_axis_roots = (
        0 if common.degree() == 0 else int(common.count_roots(-sp.oo, sp.oo))
    )
    if imaginary_axis_roots:
        return {
            "unit_circle_root": True,
            "root_at_minus_one": False,
            "cayley_axis_roots": imaginary_axis_roots,
            "inside_count_defined": False,
        }

    coefficients = [int(value) for value in transformed.all_coeffs()]
    # P-roots in the disk map to the left half-plane.  Replacing t by -t
    # lets the standard Routh sign-variation count read that number directly.
    reflected_coefficients = [
        value * (-1) ** (width - index)
        for index, value in enumerate(coefficients)
    ]
    try:
        inside = routh_right_half_plane_count(reflected_coefficients)
        method = "exact rational Routh table after Cayley transform"
    except ArithmeticError:
        leading = abs(coefficients[0])
        bound = 2 + max(abs(value) for value in coefficients[1:]) // leading
        inside = int(
            transformed.count_roots(-bound - bound * sp.I, 0 + bound * sp.I)
        )
        method = "exact Cauchy-index rectangle after Cayley transform"
    return {
        "unit_circle_root": False,
        "inside_count_defined": True,
        "inside_count": inside,
        "degree": width,
        "twice_center_deviation": abs(2 * inside - width),
        "method": method,
    }


def audit_pair(z_values: Iterable[int], gap: int) -> dict[str, object]:
    z = tuple(z_values)
    p = len(z)
    width = z[-1]
    length = gap + 2 * width
    data = sidon_data(z)
    assert data is not None
    differences, weighted_sums = data
    assert valid_gap(differences, weighted_sums, gap)

    r = staircase(z, gap)
    twice_h = positive_autocorrelation(r)
    slack = tail_slack(differences, weighted_sums, gap, length)
    assert slack == [twice_h[n] - twice_h[n + 1] for n in range(length)]
    assert slack == [pair_count_slack(z, gap, n) for n in range(length)]
    assert min(slack) >= 1

    extended_slack = slack + [0]
    twice_curvature = [0] * (length + 1)
    twice_curvature[0] = 2 * p
    for n in range(1, length + 1):
        twice_curvature[n] = extended_slack[n] - extended_slack[n - 1]

    expected = [0] * (length + 1)
    expected[0] = 2 * p
    for value in differences:
        expected[value] = 2
    for value, weight in weighted_sums.items():
        expected[gap + value] = -weight
    assert twice_curvature == expected

    total_variation = sum(abs(value) for value in twice_curvature[1:])
    assert total_variation == 2 * p * p - p

    hankel_2 = [
        twice_h[n] * twice_h[n + 2] - twice_h[n + 1] ** 2
        for n in range(length - 1)
    ]
    hankel_signs = sign_runs(hankel_2)
    inversion_span = width - gap
    arc_slack = slack[gap:width]
    assert arc_slack
    minimum_arc_slack = min(arc_slack)

    return {
        "p": p,
        "G": gap,
        "W": width,
        "W_minus_G": inversion_span,
        "global_twice_slope_total_variation": total_variation,
        "global_twice_slope_total_variation_formula": "2*p^2-p",
        "curvature_sign_reversals": sign_changes(twice_curvature[1:]),
        "curvature_sign_runs": sign_runs(twice_curvature[1:]),
        "curvature_reversals_le_2p": (
            sign_changes(twice_curvature[1:]) <= 2 * p
        ),
        "reversal_span_le_p_times_reversals": (
            inversion_span
            <= p * max(1, sign_changes(twice_curvature[1:]))
        ),
        "minimum_twice_slope": min(slack),
        "minimum_arc_twice_slope": minimum_arc_slack,
        "minimum_arc_twice_slope_index": gap + arc_slack.index(minimum_arc_slack),
        "arc_floor_p_minus_1": minimum_arc_slack >= p - 1,
        "arc_twice_slope": arc_slack,
        "arc_twice_slope_area": sum(arc_slack),
        "arc_area_over_p_cubed": str(Fraction(sum(arc_slack), p**3)),
        "hankel_2_log_concave": all(value <= 0 for value in hankel_2),
        "hankel_2_log_convex": all(value >= 0 for value in hankel_2),
        "hankel_2_sign_reversals": sign_changes(hankel_2),
        "hankel_2_sign_runs": hankel_signs,
        "first_positive_hankel_2_index": next(
            (n for n, value in enumerate(hankel_2) if value > 0), None
        ),
        "first_negative_hankel_2_index": next(
            (n for n, value in enumerate(hankel_2) if value < 0), None
        ),
    }


def stored_translation_audit() -> dict[str, object]:
    families = []
    all_pairs = []
    for record in STORED_WITNESSES:
        z = tuple(record["Z"])
        data = sidon_data(z)
        assert data is not None
        differences, weighted_sums = data
        valid_gaps = [
            gap
            for gap in range(1, z[-1])
            if valid_gap(differences, weighted_sums, gap)
        ]
        pair_audits = [audit_pair(z, gap) for gap in valid_gaps]
        all_pairs.extend(pair_audits)
        zero_data = exact_newman_zero_count(z)
        reciprocal_z = tuple(sorted(z[-1] - value for value in z))
        reciprocal_zero_data = exact_newman_zero_count(reciprocal_z)
        assert bool(zero_data["unit_circle_root"]) == bool(
            reciprocal_zero_data["unit_circle_root"]
        )
        if not bool(zero_data["unit_circle_root"]):
            assert (
                int(zero_data["inside_count"])
                + int(reciprocal_zero_data["inside_count"])
                == z[-1]
            )
            zero_data["reciprocal_inside_count"] = reciprocal_zero_data[
                "inside_count"
            ]
        families.append(
            {
                "p": len(z),
                "Z": list(z),
                "recorded_G": record["G"],
                "valid_dangerous_G": valid_gaps,
                "valid_dangerous_shift_count": len(valid_gaps),
                "newman_zero_data": zero_data,
                "pairs": pair_audits,
            }
        )
    return {
        "families": families,
        "summary": summarize_pairs(all_pairs),
    }


def summarize_pairs(pairs: list[dict[str, object]]) -> dict[str, object]:
    assert pairs
    max_reversals = max(int(pair["curvature_sign_reversals"]) for pair in pairs)
    max_hankel_reversals = max(
        int(pair["hankel_2_sign_reversals"]) for pair in pairs
    )
    max_area_ratio = max(
        Fraction(str(pair["arc_area_over_p_cubed"])) for pair in pairs
    )
    return {
        "pair_count": len(pairs),
        "global_total_variation_formula_verified": all(
            int(pair["global_twice_slope_total_variation"])
            == 2 * int(pair["p"]) ** 2 - int(pair["p"])
            for pair in pairs
        ),
        "maximum_curvature_sign_reversals": max_reversals,
        "curvature_reversals_le_2p_minus_1": all(
            int(pair["curvature_sign_reversals"]) <= 2 * int(pair["p"]) - 1
            for pair in pairs
        ),
        "curvature_reversals_le_2p": all(
            bool(pair["curvature_reversals_le_2p"]) for pair in pairs
        ),
        "span_le_p_times_reversals": all(
            bool(pair["reversal_span_le_p_times_reversals"]) for pair in pairs
        ),
        "arc_floor_p_minus_1": all(bool(pair["arc_floor_p_minus_1"]) for pair in pairs),
        "maximum_arc_area_over_p_cubed": str(max_area_ratio),
        "all_hankel_2_log_concave": all(
            bool(pair["hankel_2_log_concave"]) for pair in pairs
        ),
        "all_hankel_2_log_convex": all(
            bool(pair["hankel_2_log_convex"]) for pair in pairs
        ),
        "hankel_2_at_most_one_sign_reversal": max_hankel_reversals <= 1,
        "maximum_hankel_2_sign_reversals": max_hankel_reversals,
    }


def doubled_erdos_turan_audit(primes: list[int]) -> dict[str, object]:
    """Audit a dense Sidon dilation with every odd G support-disjoint."""
    records = []
    for p in primes:
        assert sp.isprime(p)
        base = tuple(2 * p * i + (i * i) % p for i in range(p))
        z = tuple(2 * value for value in base)
        data = sidon_data(z)
        assert data is not None
        differences, weighted_sums = data
        width = z[-1]
        assert width == 4 * p * (p - 1) + 2
        assert all(value % 2 == 0 for value in z)
        valid_odd_gaps = list(range(1, width, 2))
        assert all(
            valid_gap(differences, weighted_sums, gap)
            for gap in valid_odd_gaps
        )
        pair = audit_pair(z, 1)
        records.append(
            {
                "p": p,
                "W": width,
                "G": 1,
                "W_minus_G": width - 1,
                "W_minus_G_over_p_squared": str(Fraction(width - 1, p * p)),
                "valid_odd_G_count": len(valid_odd_gaps),
                "all_odd_G_below_W_valid": True,
                "curvature_sign_reversals_at_G_1": pair[
                    "curvature_sign_reversals"
                ],
                "hankel_2_sign_reversals_at_G_1": pair[
                    "hankel_2_sign_reversals"
                ],
                "minimum_arc_twice_slope_at_G_1": pair[
                    "minimum_arc_twice_slope"
                ],
                "arc_twice_slope_area_at_G_1": pair["arc_twice_slope_area"],
                "arc_area_over_p_fourth": str(
                    Fraction(int(pair["arc_twice_slope_area"]), p**4)
                ),
            }
        )
    return {
        "definition": (
            "a_i=2*p*i+(i^2 mod p), Z=2*{a_i}, G odd; "
            "D(Z) is even and G+S(Z) is odd"
        ),
        "symbolic_width": "W=4*p*(p-1)+2",
        "symbolic_span_at_G_1": "W-G=4*p^2-4*p+1",
        "unconditional_little_o_span_candidate": False,
        "records": records,
    }


def radix_strict_tail_audit(max_p: int) -> dict[str, object]:
    """Verify the sharp u_n=1 point in an arbitrarily large-p Sidon family."""
    records = []
    for p in range(3, max_p + 1):
        z = (0, *(2 * 4**power for power in range(p - 1)))
        data = sidon_data(z)
        assert data is not None
        differences, weighted_sums = data
        assert valid_gap(differences, weighted_sums, 1)
        width = z[-1]
        n = width // 2 + 1
        value = pair_count_slack(z, 1, n)
        assert 1 <= n < width
        assert value == 1
        records.append(
            {
                "p": p,
                "W": width,
                "G": 1,
                "sharp_index": n,
                "twice_slope_at_sharp_index": value,
            }
        )
    return {
        "definition": "Z={0} union {2*4^j:0<=j<=p-2}, G=1",
        "sharp_global_tail_floor": 1,
        "records": records,
    }


def exhaustive_audit(max_width: int) -> dict[str, object]:
    pairs: list[dict[str, object]] = []
    rulers = 0
    zero_records = []
    first_failures: dict[str, dict[str, object]] = {}
    for width in range(1, max_width + 1):
        for interior_size in range(width):
            for middle in combinations(range(1, width), interior_size):
                z = (0, *middle, width)
                data = sidon_data(z)
                if data is None:
                    continue
                rulers += 1
                differences, weighted_sums = data
                zero_records.append({"Z": list(z), **exact_newman_zero_count(z)})
                for gap in range(1, width):
                    if not valid_gap(differences, weighted_sums, gap):
                        continue
                    record = audit_pair(z, gap)
                    pairs.append(record)
                    checks = {
                        "curvature_reversals_le_2p_minus_1": (
                            int(record["curvature_sign_reversals"])
                            <= 2 * len(z) - 1
                        ),
                        "curvature_reversals_le_2p": bool(
                            record["curvature_reversals_le_2p"]
                        ),
                        "span_le_p_times_reversals": bool(
                            record["reversal_span_le_p_times_reversals"]
                        ),
                        "arc_floor_p_minus_1": bool(record["arc_floor_p_minus_1"]),
                        "hankel_2_log_concave": bool(record["hankel_2_log_concave"]),
                        "hankel_2_at_most_one_sign_reversal": (
                            int(record["hankel_2_sign_reversals"]) <= 1
                        ),
                    }
                    for name, passed in checks.items():
                        if not passed and name not in first_failures:
                            first_failures[name] = {"Z": list(z), **record}
    return {
        "max_width": max_width,
        "sidon_ruler_count": rulers,
        "valid_pair_count": len(pairs),
        "summary": summarize_pairs(pairs),
        "summary_by_p": {
            str(p): summarize_pairs(
                [pair for pair in pairs if int(pair["p"]) == p]
            )
            for p in sorted({int(pair["p"]) for pair in pairs})
        },
        "first_failures": first_failures,
        "zero_distribution": {
            "ruler_count": len(zero_records),
            "unit_circle_root_count": sum(
                bool(record["unit_circle_root"]) for record in zero_records
            ),
            "balanced_count_candidate": all(
                bool(record["unit_circle_root"])
                or int(record["inside_count"]) == int(record["degree"]) // 2
                for record in zero_records
            ),
            "center_deviation_le_p_candidate": all(
                bool(record["unit_circle_root"])
                or int(record["twice_center_deviation"])
                <= len(record["Z"])
                for record in zero_records
            ),
            "first_unbalanced": next(
                (
                    record
                    for record in zero_records
                    if not bool(record["unit_circle_root"])
                    and int(record["inside_count"]) != int(record["degree"]) // 2
                ),
                None,
            ),
            "first_center_deviation_gt_p": next(
                (
                    record
                    for record in zero_records
                    if not bool(record["unit_circle_root"])
                    and int(record["twice_center_deviation"]) > len(record["Z"])
                ),
                None,
            ),
        },
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
        "exact_arithmetic": True,
        "sympy_version": sp.__version__,
        "candidate_definitions": {
            "translation_family": (
                "fixed Z and every support-disjoint shift 1 <= G < W"
            ),
            "twice_slope": (
                "u_n=2s_n=# ordered (i,j) with |z_i-z_j|<=n<G+z_i+z_j"
            ),
            "total_variation": "sum_{n=1}^L |u_n-u_{n-1}|",
            "hankel_2": "H_n H_{n+2}-H_{n+1}^2 for H=2h",
            "weighted_arc_floor": "u_n >= p-1 for G <= n < W",
            "zero_centering": "|2*N_D(P)-W| <= p when P has no unit root",
        },
        "stored_translation_families": stored_translation_audit(),
        "doubled_erdos_turan_family": doubled_erdos_turan_audit(
            [3, 5, 7, 11, 13, 17, 19, 23]
        ),
        "radix_strict_tail_family": radix_strict_tail_audit(9),
        "exhaustive": exhaustive_audit(args.max_width),
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
