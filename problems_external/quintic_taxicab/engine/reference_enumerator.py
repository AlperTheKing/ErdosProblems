#!/usr/bin/env python3
"""Slow exact Fraction/isqrt reference for bounded Q5-TORSOR boxes.

This is calibration code, not a proof of nonexistence and not a main search
engine.  It enumerates reduced

    t = p/q,  1 <= p <= P, 1 <= q <= Q,
    u = n/d, -N <= n <= N, 1 <= d <= D,

retaining ``abs(u) < t``.  It checks the registered discriminant equation,
both signs of Y, the rational-square Z gate, the positivity bound, denominator
clearing, and the final integer certificate.  Every arithmetic operation is
performed with ``Fraction``, integers, and ``math.isqrt``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


MAX_DECLARED_CASES = 2_000_000


class BoundsError(ValueError):
    """Raised when a calibration box is malformed or exceeds the safety cap."""


@dataclass(frozen=True)
class BoxBounds:
    p_max: int
    q_max: int
    u_num_max: int
    u_den_max: int

    @property
    def declared_case_cap(self) -> int:
        return self.p_max * self.q_max * (2 * self.u_num_max + 1) * self.u_den_max

    def validate(self) -> None:
        values = (self.p_max, self.q_max, self.u_den_max)
        if any(value < 1 for value in values) or self.u_num_max < 0:
            raise BoundsError("require P,Q,D >= 1 and N >= 0")
        if self.declared_case_cap > MAX_DECLARED_CASES:
            raise BoundsError(
                f"declared box cap {self.declared_case_cap} exceeds "
                f"calibration limit {MAX_DECLARED_CASES}"
            )


def fraction_text(value: Fraction) -> str:
    """Return a stable exact representation."""

    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def rational_square_root(value: Fraction) -> Fraction | None:
    """Return the nonnegative exact square root, or ``None``."""

    if value < 0:
        return None
    numerator_root = math.isqrt(value.numerator)
    denominator_root = math.isqrt(value.denominator)
    if (
        numerator_root * numerator_root != value.numerator
        or denominator_root * denominator_root != value.denominator
    ):
        return None
    return Fraction(numerator_root, denominator_root)


def reduced_positive_fractions(numerator_max: int, denominator_max: int) -> Iterable[Fraction]:
    """Yield each reduced positive p/q in the declared rectangle once."""

    for denominator in range(1, denominator_max + 1):
        for numerator in range(1, numerator_max + 1):
            if math.gcd(numerator, denominator) == 1:
                yield Fraction(numerator, denominator)


def reduced_signed_fractions(numerator_max: int, denominator_max: int) -> Iterable[Fraction]:
    """Yield each reduced n/d in the signed declared rectangle once."""

    for denominator in range(1, denominator_max + 1):
        for numerator in range(-numerator_max, numerator_max + 1):
            if math.gcd(abs(numerator), denominator) == 1:
                yield Fraction(numerator, denominator)


def fifth_form(t: Fraction, u: Fraction) -> Fraction:
    """Return 16 times the sum of the fifth powers of (t-u)/2,(t+u)/2."""

    return t**5 + 10 * t**3 * u**2 + 5 * t * u**4


def discriminant_radicand(t: Fraction, u: Fraction) -> Fraction:
    """Return ``80*T^6 + 20*T*L`` from Q5-TORSOR."""

    T = t + 1
    return 80 * T**6 + 20 * T * fifth_form(t, u)


def z_from_y(t: Fraction, y: Fraction) -> Fraction:
    T = t + 1
    return (y - 10 * T**3) / (10 * T)


def clear_to_primitive_integers(values: Sequence[Fraction]) -> tuple[int, ...]:
    """Clear denominators and divide by the common positive gcd."""

    if not values:
        raise ValueError("cannot clear an empty sequence")
    common_denominator = math.lcm(*(value.denominator for value in values))
    integers = tuple(
        value.numerator * (common_denominator // value.denominator) for value in values
    )
    common_gcd = 0
    for value in integers:
        common_gcd = math.gcd(common_gcd, abs(value))
    if common_gcd == 0:
        raise ValueError("cannot primitive-normalize an all-zero sequence")
    return tuple(value // common_gcd for value in integers)


def _integer_certificate_valid(values: Sequence[int]) -> bool:
    """Independent final gate used only by this reference implementation."""

    if len(values) != 4 or any(value <= 0 for value in values):
        return False
    a, b, c, d = values
    return a**5 + b**5 == c**5 + d**5 and not set((a, b)).intersection((c, d))


def _fraction_record(value: Fraction) -> dict[str, str]:
    return {
        "text": fraction_text(value),
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
    }


def evaluate_specialization(t: Fraction, u: Fraction) -> dict[str, Any]:
    """Evaluate one admissible specialization and both possible Y signs."""

    if t <= 0 or abs(u) >= t:
        raise ValueError("specialization must satisfy t > 0 and |u| < t")
    T = t + 1
    L = fifth_form(t, u)
    radicand = discriminant_radicand(t, u)
    y_root = rational_square_root(radicand)
    sign_records: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    if y_root is not None:
        y_values = (y_root,) if y_root == 0 else (y_root, -y_root)
        for y in y_values:
            z = z_from_y(t, y)
            v_root = rational_square_root(z)
            z_nonnegative = z >= 0
            z_below_bound = z < T**2
            z_square = v_root is not None
            sign_record: dict[str, Any] = {
                "y": _fraction_record(y),
                "z": _fraction_record(z),
                "z_nonnegative": z_nonnegative,
                "z_rational_square": z_square,
                "z_below_T_squared": z_below_bound,
                "passes_torsor_gates": z_square and z_nonnegative and z_below_bound,
            }
            if v_root is not None:
                sign_record["v_nonnegative"] = _fraction_record(v_root)

            if z_square and z_nonnegative and z_below_bound:
                v = v_root
                rational_values = (
                    (t - u) / 2,
                    (t + u) / 2,
                    (T - v) / 2,
                    (T + v) / 2,
                )
                integer_values = clear_to_primitive_integers(rational_values)
                equality = (
                    rational_values[0] ** 5 + rational_values[1] ** 5
                    == rational_values[2] ** 5 + rational_values[3] ** 5
                )
                positive = all(value > 0 for value in rational_values)
                cross_disjoint = not set(rational_values[:2]).intersection(rational_values[2:])
                integer_valid = _integer_certificate_valid(integer_values)
                candidate = {
                    "rational_quadruple": [
                        _fraction_record(value) for value in rational_values
                    ],
                    "integer_quadruple": list(integer_values),
                    "rational_equality": equality,
                    "rational_positive": positive,
                    "rational_cross_disjoint": cross_disjoint,
                    "integer_certificate_valid": integer_valid,
                }
                sign_record["candidate"] = candidate
                candidates.append(candidate)
            sign_records.append(sign_record)

    return {
        "t": _fraction_record(t),
        "u": _fraction_record(u),
        "T": _fraction_record(T),
        "L": _fraction_record(L),
        "radicand": _fraction_record(radicand),
        "radicand_rational_square": y_root is not None,
        "y_nonnegative": _fraction_record(y_root) if y_root is not None else None,
        "signs": sign_records,
        "candidates": candidates,
    }


def enumerate_box(bounds: BoxBounds, emit_points: bool = False) -> dict[str, Any]:
    """Exhaust one finite calibration rectangle exactly."""

    bounds.validate()
    t_values = list(reduced_positive_fractions(bounds.p_max, bounds.q_max))
    u_values = list(reduced_signed_fractions(bounds.u_num_max, bounds.u_den_max))
    counts = {
        "reduced_t_values": len(t_values),
        "reduced_u_values": len(u_values),
        "pairs_considered": 0,
        "admissible_specializations": 0,
        "radicand_squares": 0,
        "y_signs_tested": 0,
        "nonnegative_z": 0,
        "z_squares": 0,
        "bounded_z_squares": 0,
        "candidate_records": 0,
        "verified_integer_certificates": 0,
    }
    quartic_points: list[dict[str, Any]] = []
    certificates: dict[tuple[int, int, int, int], dict[str, Any]] = {}

    for t in t_values:
        for u in u_values:
            counts["pairs_considered"] += 1
            if abs(u) >= t:
                continue
            counts["admissible_specializations"] += 1
            record = evaluate_specialization(t, u)
            if not record["radicand_rational_square"]:
                continue
            counts["radicand_squares"] += 1
            counts["y_signs_tested"] += len(record["signs"])
            for sign in record["signs"]:
                if sign["z_nonnegative"]:
                    counts["nonnegative_z"] += 1
                if sign["z_rational_square"]:
                    counts["z_squares"] += 1
                if sign["passes_torsor_gates"]:
                    counts["bounded_z_squares"] += 1
            for candidate in record["candidates"]:
                counts["candidate_records"] += 1
                if candidate["integer_certificate_valid"]:
                    key = tuple(candidate["integer_quadruple"])
                    certificates[key] = candidate
            if emit_points:
                quartic_points.append(record)

    counts["verified_integer_certificates"] = len(certificates)
    return {
        "schema_version": 1,
        "engine": "q5_torsor_fraction_isqrt_reference",
        "status": "HIT" if certificates else "NO_HIT",
        "scope": "finite_calibration_box_only",
        "bounds": {
            "P": bounds.p_max,
            "Q": bounds.q_max,
            "N": bounds.u_num_max,
            "D": bounds.u_den_max,
            "declared_case_cap": bounds.declared_case_cap,
        },
        "counts": counts,
        "quartic_points": quartic_points if emit_points else [],
        "certificates": list(certificates.values()),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p-max", type=int, required=True, metavar="P")
    parser.add_argument("--q-max", type=int, required=True, metavar="Q")
    parser.add_argument("--u-num-max", type=int, required=True, metavar="N")
    parser.add_argument("--u-den-max", type=int, required=True, metavar="D")
    parser.add_argument("--emit-points", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        report = enumerate_box(
            BoxBounds(args.p_max, args.q_max, args.u_num_max, args.u_den_max),
            emit_points=args.emit_points,
        )
    except BoundsError as exc:
        parser.error(str(exc))

    text = json.dumps(
        report,
        indent=2 if args.pretty else None,
        sort_keys=True,
        separators=None if args.pretty else (",", ":"),
    ) + "\n"
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
