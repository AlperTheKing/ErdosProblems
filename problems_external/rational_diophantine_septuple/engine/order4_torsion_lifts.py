#!/usr/bin/env python3
"""Exhaust the E_plus torsion lifts for the fixed order-four quotient.

This is a conditional finite gate.  It does not assert that E_plus has rank
zero.  If an independent rank calculation proves rank zero, the certified
torsion audit plus this exhaustive lift makes the C(Q) test complete.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from math import isqrt, prod
from pathlib import Path
from typing import Any


EXPECTED_MODELS_SHA256 = (
    "93311E02A6DE4BBDBF4A2C93B2883BF83CAE9448597F9490B5B3C7D21205262E"
)
EXPECTED_TORSION_SHA256 = (
    "5525158254F582883A7F24B0DA5BE506B3DE2C40E4A1A2F808C5E9B49DA0E001"
)

A = Q(1884586446094351, 25415891646864180)
B = Q(14442883687791636, 7402559392524605)
C = Q(60340495895762708555, 14487505263205637124)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def qtext(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def sqrt_q(value: Q) -> Q | None:
    if value < 0:
        return None
    numerator = isqrt(value.numerator)
    denominator = isqrt(value.denominator)
    if numerator * numerator != value.numerator:
        return None
    if denominator * denominator != value.denominator:
        return None
    return Q(numerator, denominator)


def add_points(
    left: tuple[Q, Q] | None,
    right: tuple[Q, Q] | None,
    a2: Q,
    a4: Q,
) -> tuple[Q, Q] | None:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and y1 == -y2:
        return None
    if left == right:
        if y1 == 0:
            return None
        slope = (3 * x1 * x1 + 2 * a2 * x1 + a4) / (2 * y1)
    else:
        if x1 == x2:
            raise AssertionError("invalid vertical addition")
        slope = (y2 - y1) / (x2 - x1)
    x3 = slope * slope - a2 - x1 - x2
    y3 = -(y1 + slope * (x3 - x1))
    return x3, y3


def multiply_point(
    scalar: int,
    point: tuple[Q, Q] | None,
    a2: Q,
    a4: Q,
) -> tuple[Q, Q] | None:
    result = None
    addend = point
    while scalar:
        if scalar & 1:
            result = add_points(result, addend, a2, a4)
        addend = add_points(addend, addend, a2, a4)
        scalar //= 2
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    problem_dir = Path(__file__).resolve().parent.parent
    rank_dir = (
        problem_dir
        / "runs"
        / "order4_genus2_quotient_20260720T175340"
        / "open_source_rank"
    )
    models_path = rank_dir / "models.json"
    torsion_path = rank_dir / "torsion_audit.json"
    assert sha256(models_path) == EXPECTED_MODELS_SHA256
    assert sha256(torsion_path) == EXPECTED_TORSION_SHA256

    models = json.loads(models_path.read_text(encoding="ascii"))
    torsion = json.loads(torsion_path.read_text(encoding="ascii"))
    assert torsion["E_plus"]["certified"] is True
    assert torsion["E_plus"]["torsion_group"] == "Z/2Z x Z/4Z"
    assert torsion["E_plus"]["torsion_order"] == 8

    p, q, r = A * B, A * C, B * C
    alpha = A * B * C
    a2 = p + q + r
    a4 = p * q + p * r + q * r
    a6 = p * q * r
    assert a6 == alpha * alpha

    pair_roots = [sqrt_q(1 + value) for value in (p, q, r)]
    assert all(root is not None for root in pair_roots)
    sigma = prod((root for root in pair_roots if root is not None), start=Q(1))
    P = (Q(0), alpha)
    S = (Q(1), sigma)
    minus_S = (S[0], -S[1])
    assert multiply_point(2, P, a2, a4) == minus_S
    assert multiply_point(4, P, a2, a4) == (-p, Q(0))
    assert multiply_point(8, P, a2, a4) is None

    g_coefficients = [Q(value) for value in models["g_coefficients_low_to_high"]]
    c0, c1, c2, c3 = g_coefficients
    assert c3 == -p

    def g(value: Q) -> Q:
        return c0 + c1 * value + c2 * value * value + c3 * value**3

    A0 = q + r - 2 * p
    U0 = (1 + p) * q * r / p
    j = q + r + 2
    k = q + r - 4 * p - 2

    torsion_points: list[dict[str, Any]] = [
        {"kind": "identity", "point": None}
    ]
    for x_text in torsion["E_plus"]["rational_2_torsion_x"]:
        torsion_points.append(
            {"kind": "order_2", "point": (Q(x_text), Q(0))}
        )
    for half_index, row in enumerate(torsion["E_plus"]["order4_half_points"]):
        x_value = Q(row["x"])
        y_value = Q(row["positive_y"])
        for sign in (1, -1):
            torsion_points.append(
                {
                    "kind": "order_4",
                    "half_index": half_index,
                    "point": (x_value, sign * y_value),
                }
            )
    assert len(torsion_points) == 8

    point_records: list[dict[str, Any]] = []
    raw_lifts: list[dict[str, Any]] = []
    unique_t: set[tuple[Q, Q]] = set()
    for torsion_index, item in enumerate(torsion_points):
        point = item["point"]
        if point is None:
            point_records.append(
                {
                    "torsion_index": torsion_index,
                    "kind": item["kind"],
                    "c_lifts": 0,
                    "reason": "c3 is negative, so C has no rational point at infinity",
                }
            )
            continue

        x_plus, y_plus = point
        square_coordinate = x_plus / c3
        x_root = sqrt_q(square_coordinate)
        record: dict[str, Any] = {
            "torsion_index": torsion_index,
            "kind": item["kind"],
            "point": [qtext(x_plus), qtext(y_plus)],
            "X_squared": qtext(square_coordinate),
            "X_squared_is_square": x_root is not None,
        }
        if x_root is None:
            record["c_lifts"] = 0
            point_records.append(record)
            continue

        record["X_positive"] = qtext(x_root)
        record["c_lifts"] = 2
        point_records.append(record)
        for x_sign in (1, -1):
            X = x_sign * x_root
            W = y_plus / c3
            assert W * W == g(X * X)
            U = U0 - X * X / p
            V = W / (p * p)
            Z = X
            assert V * V == U * (U - j) * (U - k)
            assert Z * Z == p * (U0 - U)

            t_root = sqrt_q(U)
            if t_root is None:
                raw_lifts.append(
                    {
                        "torsion_index": torsion_index,
                        "C_point": [qtext(X), qtext(W)],
                        "U": qtext(U),
                        "E_lift": None,
                    }
                )
                continue

            assert U != j
            UJ = j + 4 * j * (1 + p) / (U - j)
            second_diagonal_value = p * (U0 - UJ)
            second_diagonal_root = sqrt_q(second_diagonal_value)
            for t_sign in (1, -1):
                t = t_sign * t_root
                e_u = (U - A0 - V / t) / 2
                T = (e_u - p, t * e_u)
                assert T[1] * T[1] == (T[0] + p) * (T[0] + q) * (T[0] + r)
                unique_t.add(T)

                orbit_values: list[Q] = []
                current = T
                for _ in range(4):
                    assert current is not None
                    orbit_values.append(current[0] / alpha)
                    current = add_points(current, S, a2, a4)
                assert current == T

                base_square_flags = [
                    [sqrt_q(base * value + 1) is not None for base in (A, B, C)]
                    for value in orbit_values
                ]
                orbit_pair_flags = []
                for left in range(4):
                    for right in range(left + 1, 4):
                        orbit_pair_flags.append(
                            {
                                "pair": [left, right],
                                "square": sqrt_q(
                                    orbit_values[left] * orbit_values[right] + 1
                                )
                                is not None,
                            }
                        )
                distinct = len(set(orbit_values)) == 4
                nonzero = all(value != 0 for value in orbit_values)
                base_compatible = all(all(row) for row in base_square_flags)
                orbit_compatible = all(row["square"] for row in orbit_pair_flags)
                candidate = (
                    second_diagonal_root is not None
                    and distinct
                    and nonzero
                    and base_compatible
                    and orbit_compatible
                )
                raw_lifts.append(
                    {
                        "torsion_index": torsion_index,
                        "C_point": [qtext(X), qtext(W)],
                        "U": qtext(U),
                        "U_sqrt": qtext(t),
                        "V": qtext(V),
                        "T": [qtext(T[0]), qtext(T[1])],
                        "second_diagonal_value": qtext(second_diagonal_value),
                        "second_diagonal_square": second_diagonal_root is not None,
                        "orbit": [qtext(value) for value in orbit_values],
                        "base_square_flags": base_square_flags,
                        "orbit_pair_flags": orbit_pair_flags,
                        "distinct": distinct,
                        "nonzero": nonzero,
                        "candidate": candidate,
                    }
                )

    candidate_count = sum(record.get("candidate", False) for record in raw_lifts)
    result = {
        "status": "CONDITIONAL_TORSION_LIFT_EXHAUSTED",
        "condition": "This list is complete for C(Q) only if rank(E_plus)=0 is certified.",
        "input_sha256": {
            "models.json": EXPECTED_MODELS_SHA256,
            "torsion_audit.json": EXPECTED_TORSION_SHA256,
        },
        "bridge_checks": {
            "two_P_equals_minus_S": True,
            "P_exact_order": 8,
            "S_in_2E": True,
        },
        "counts": {
            "E_plus_torsion_points": len(torsion_points),
            "torsion_points_with_C_lift": sum(
                record["c_lifts"] > 0 for record in point_records
            ),
            "signed_C_lifts": sum(record["c_lifts"] for record in point_records),
            "raw_E_lifts": sum(record.get("E_lift", True) is not None for record in raw_lifts),
            "unique_T": len(unique_t),
            "candidate_records": candidate_count,
        },
        "torsion_points": point_records,
        "raw_lifts": raw_lifts,
    }
    assert result["counts"] == {
        "E_plus_torsion_points": 8,
        "torsion_points_with_C_lift": 4,
        "signed_C_lifts": 8,
        "raw_E_lifts": 16,
        "unique_T": 8,
        "candidate_records": 0,
    }
    args.output.resolve().write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
