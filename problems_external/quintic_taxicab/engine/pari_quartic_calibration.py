#!/usr/bin/env python3
"""Fail-closed PARI 2.15.4 calibration for one quintic torsor quartic.

This program is deliberately a calibration tool, not a search harness.  It
enumerates one explicitly bounded specialization t = p/q with PARI's
``hyperellratpoints`` and independently repeats the same finite x-coordinate
box with ``Fraction`` and ``isqrt`` arithmetic.  Every returned quartic point
is checked with both signs before it is allowed through the Z-square,
positivity, fifth-power, and cross-disjointness gates.

For t = p/q and T = t + 1, PARI enumerates the integral model

    Yprime^2 = A*w^4 + B*w^2 + C,

where Yprime = q^3*Y and

    A = 100*p*(p+q)*q^4,
    B = 200*(p+q)*p^3*q^2,
    C = 80*(p+q)^6 + 20*(p+q)*p^5.

The ``--libpari`` argument is required so that no ambient GP/PARI installation
can silently replace the audited bundled library.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


SCHEMA = "quintic-taxicab-pari-calibration-v1"
EXPECTED_PARI_VERSION = (2, 15, 4)
MAX_CALIBRATION_BOUND = 1_000
PARI_STACK_BYTES = 256_000_000
PARI_MAX_PRIME = 2_000_000
RATIONAL_TOKEN = re.compile(r"[+-]?\d+(?:/[+-]?\d+)?")


class CalibrationError(RuntimeError):
    """Any condition that must terminate the calibration without a PASS."""


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def rational_square_root(value: Fraction) -> Fraction | None:
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


def parse_pari_fraction(token: str) -> Fraction:
    token = token.strip()
    if RATIONAL_TOKEN.fullmatch(token) is None:
        raise CalibrationError(f"unexpected PARI rational token: {token!r}")
    if "/" in token:
        numerator_text, denominator_text = token.split("/", 1)
        denominator = int(denominator_text)
        if denominator == 0:
            raise CalibrationError("PARI emitted a zero denominator")
        return Fraction(int(numerator_text), denominator)
    return Fraction(int(token), 1)


def parse_pari_points(raw: str) -> list[tuple[Fraction, Fraction]]:
    """Parse only a flat PARI vector of two-rational vectors."""

    text = raw.strip()
    if text == "[]":
        return []
    if len(text) < 4 or text[0] != "[" or text[-1] != "]":
        raise CalibrationError(f"unexpected PARI point vector: {raw!r}")

    body = text[1:-1]
    point_pattern = re.compile(
        r"\[\s*([+-]?\d+(?:/[+-]?\d+)?)\s*,\s*"
        r"([+-]?\d+(?:/[+-]?\d+)?)\s*\]"
    )
    points: list[tuple[Fraction, Fraction]] = []
    cursor = 0
    while cursor < len(body):
        match = point_pattern.match(body, cursor)
        if match is None:
            raise CalibrationError(
                f"unparsed PARI point-vector suffix: {body[cursor:]!r}"
            )
        points.append(
            (parse_pari_fraction(match.group(1)), parse_pari_fraction(match.group(2)))
        )
        cursor = match.end()
        if cursor == len(body):
            break
        comma = re.match(r"\s*,\s*", body[cursor:])
        if comma is None:
            raise CalibrationError(
                f"unexpected PARI point separator: {body[cursor:]!r}"
            )
        cursor += comma.end()

    if len(points) != len(set(points)):
        raise CalibrationError("PARI emitted duplicate affine points")
    return points


def quartic_coefficients(p: int, q: int) -> tuple[int, int, int]:
    return (
        100 * p * (p + q) * q**4,
        200 * (p + q) * p**3 * q**2,
        80 * (p + q) ** 6 + 20 * (p + q) * p**5,
    )


def quartic_rhs(coefficients: tuple[int, int, int], w: Fraction) -> Fraction:
    a4, a2, a0 = coefficients
    return a4 * w**4 + a2 * w**2 + a0


def independently_enumerate_points(
    coefficients: tuple[int, int, int], numerator_bound: int, denominator_bound: int
) -> set[tuple[Fraction, Fraction]]:
    points: set[tuple[Fraction, Fraction]] = set()
    for denominator in range(1, denominator_bound + 1):
        for numerator in range(-numerator_bound, numerator_bound + 1):
            if math.gcd(abs(numerator), denominator) != 1:
                continue
            w = Fraction(numerator, denominator)
            y = rational_square_root(quartic_rhs(coefficients, w))
            if y is None:
                continue
            points.add((w, y))
            if y:
                points.add((w, -y))
    return points


def verify_integer_quadruple(values: tuple[int, int, int, int]) -> dict[str, Any]:
    a, b, c, d = values
    positivity = all(value > 0 for value in values)
    equality = a**5 + b**5 == c**5 + d**5
    cross_disjoint = set((a, b)).isdisjoint((c, d))
    return {
        "values": list(values),
        "positivity": positivity,
        "fifth_power_equality": equality,
        "cross_disjoint": cross_disjoint,
        "accepted": positivity and equality and cross_disjoint,
    }


def clear_denominators(values: tuple[Fraction, ...]) -> tuple[int, ...]:
    scale = math.lcm(*(value.denominator for value in values))
    integers = tuple(int(value * scale) for value in values)
    common = math.gcd(*integers)
    if common == 0:
        raise CalibrationError("cannot normalize an all-zero quadruple")
    return tuple(value // abs(common) for value in integers)


def evaluate_signed_branch(
    p: int,
    q: int,
    coefficients: tuple[int, int, int],
    w: Fraction,
    y_prime: Fraction,
    sign_label: int,
) -> dict[str, Any]:
    t = Fraction(p, q)
    capital_t = t + 1
    y = y_prime / q**3
    direct_rhs = (
        80 * capital_t**6
        + 20
        * capital_t
        * (t**5 + 10 * t**3 * w**2 + 5 * t * w**4)
    )
    if y * y != direct_rhs:
        raise CalibrationError("scaled quartic point failed the direct torsor equation")
    if y_prime * y_prime != quartic_rhs(coefficients, w):
        raise CalibrationError("PARI point failed the integral quartic equation")

    z = (y - 10 * capital_t**3) / (10 * capital_t)
    z_root = rational_square_root(z)
    basic_gates = {
        "abs_w_lt_t": abs(w) < t,
        "z_nonnegative": z >= 0,
        "z_lt_T_squared": z < capital_t**2,
        "z_rational_square": z_root is not None,
    }

    result: dict[str, Any] = {
        "sign_test": sign_label,
        "w": fraction_text(w),
        "Y_prime": fraction_text(y_prime),
        "Y": fraction_text(y),
        "Z": fraction_text(z),
        "gates": basic_gates,
        "status": "REJECTED",
    }
    if not all(basic_gates.values()):
        return result

    assert z_root is not None
    v = z_root
    rational_values = (
        (t - w) / 2,
        (t + w) / 2,
        (capital_t - v) / 2,
        (capital_t + v) / 2,
    )
    positivity = all(value > 0 for value in rational_values)
    rational_equality = (
        rational_values[0] ** 5 + rational_values[1] ** 5
        == rational_values[2] ** 5 + rational_values[3] ** 5
    )
    rational_cross_disjoint = set(rational_values[:2]).isdisjoint(rational_values[2:])
    result["v"] = fraction_text(v)
    result["rational_values"] = [fraction_text(value) for value in rational_values]
    result["gates"].update(
        {
            "positive_abcd": positivity,
            "rational_fifth_power_equality": rational_equality,
            "rational_cross_disjoint": rational_cross_disjoint,
        }
    )
    if not (positivity and rational_equality and rational_cross_disjoint):
        return result

    integer_values = clear_denominators(rational_values)
    integer_verification = verify_integer_quadruple(integer_values)  # exact replay
    result["integer_candidate"] = integer_verification
    if not integer_verification["accepted"]:
        raise CalibrationError("rational gates passed but integer replay disagreed")
    result["status"] = "TORSOR_CERTIFICATE_CANDIDATE"
    return result


class PariSession:
    def __init__(self, library_path: Path) -> None:
        self.library_path = library_path
        self.lib: ctypes.CDLL | None = None

    def __enter__(self) -> "PariSession":
        if not self.library_path.is_file():
            raise CalibrationError(f"libpari is not a file: {self.library_path}")
        os.environ["LD_LIBRARY_PATH"] = str(self.library_path.parent)
        try:
            lib = ctypes.CDLL(str(self.library_path))
        except OSError as exc:
            raise CalibrationError(f"cannot load libpari: {exc}") from exc
        lib.pari_init.argtypes = [ctypes.c_size_t, ctypes.c_ulong]
        lib.pari_init.restype = None
        lib.gp_read_str.argtypes = [ctypes.c_char_p]
        lib.gp_read_str.restype = ctypes.c_void_p
        lib.GENtostr.argtypes = [ctypes.c_void_p]
        lib.GENtostr.restype = ctypes.c_char_p
        lib.pari_close.argtypes = []
        lib.pari_close.restype = None
        lib.pari_init(PARI_STACK_BYTES, PARI_MAX_PRIME)
        self.lib = lib
        return self

    def evaluate(self, expression: str) -> str:
        if self.lib is None:
            raise CalibrationError("PARI session is not initialized")
        value = self.lib.gp_read_str(expression.encode("ascii"))
        if not value:
            raise CalibrationError(f"PARI returned NULL for expression: {expression}")
        text = self.lib.GENtostr(value)
        if not text:
            raise CalibrationError("GENtostr returned NULL")
        return text.decode("ascii")

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self.lib is not None:
            self.lib.pari_close()
            self.lib = None


def parse_version(raw: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]", raw.strip())
    if match is None:
        raise CalibrationError(f"unexpected PARI version output: {raw!r}")
    return tuple(int(group) for group in match.groups())  # type: ignore[return-value]


def run_calibration(args: argparse.Namespace) -> dict[str, Any]:
    if args.p <= 0 or args.q <= 0:
        raise CalibrationError("p and q must be positive")
    if math.gcd(args.p, args.q) != 1:
        raise CalibrationError("p/q must be reduced")
    if not (1 <= args.denominator_bound <= args.numerator_bound):
        raise CalibrationError("bounds must satisfy 1 <= D <= N")
    if args.numerator_bound > MAX_CALIBRATION_BOUND:
        raise CalibrationError(
            f"N exceeds the calibration-only cap {MAX_CALIBRATION_BOUND}"
        )

    library_path = Path(args.libpari).expanduser().resolve(strict=False)
    coefficients = quartic_coefficients(args.p, args.q)
    polynomial = (
        f"{coefficients[0]}*x^4+{coefficients[1]}*x^2+{coefficients[2]}"
    )

    with PariSession(library_path) as pari:
        version = parse_version(pari.evaluate("version()"))
        if version != EXPECTED_PARI_VERSION:
            raise CalibrationError(
                f"expected PARI {EXPECTED_PARI_VERSION}, received {version}"
            )
        gcd_degree_raw = pari.evaluate(
            f"poldegree(gcd({polynomial},deriv({polynomial})))"
        )
        try:
            gcd_degree = int(gcd_degree_raw)
        except ValueError as exc:
            raise CalibrationError(
                f"unexpected squarefreeness output: {gcd_degree_raw!r}"
            ) from exc
        if gcd_degree != 0:
            raise CalibrationError(
                f"specialized quartic is not squarefree (gcd degree {gcd_degree})"
            )
        expression = (
            f"hyperellratpoints({polynomial},"
            f"[{args.numerator_bound},{args.denominator_bound}])"
        )
        raw_points = pari.evaluate(expression)

    pari_points_list = parse_pari_points(raw_points)
    pari_points = set(pari_points_list)
    independent_points = independently_enumerate_points(
        coefficients, args.numerator_bound, args.denominator_bound
    )
    if pari_points != independent_points:
        missing = sorted(independent_points - pari_points)
        extra = sorted(pari_points - independent_points)
        raise CalibrationError(
            "PARI/Fraction point-set disagreement: "
            f"missing={[(fraction_text(x), fraction_text(y)) for x, y in missing]}, "
            f"extra={[(fraction_text(x), fraction_text(y)) for x, y in extra]}"
        )

    absolute_point_keys = sorted({(w, abs(y_prime)) for w, y_prime in pari_points})
    branches: list[dict[str, Any]] = []
    for w, absolute_y_prime in absolute_point_keys:
        branches.append(
            evaluate_signed_branch(
                args.p, args.q, coefficients, w, absolute_y_prime, +1
            )
        )
        branches.append(
            evaluate_signed_branch(
                args.p, args.q, coefficients, w, -absolute_y_prime, -1
            )
        )

    candidates = [
        branch["integer_candidate"]
        for branch in branches
        if branch["status"] == "TORSOR_CERTIFICATE_CANDIDATE"
    ]
    return {
        "schema": SCHEMA,
        "mode": "CALIBRATION_ONLY",
        "status": "PASS",
        "input": {
            "p": args.p,
            "q": args.q,
            "t": fraction_text(Fraction(args.p, args.q)),
            "numerator_bound_N": args.numerator_bound,
            "denominator_bound_D": args.denominator_bound,
        },
        "engine": {
            "name": "PARI hyperellratpoints via explicit bundled shared library",
            "libpari": str(library_path),
            "libpari_sha256": hashlib.sha256(library_path.read_bytes()).hexdigest().upper(),
            "pari_version": list(version),
            "pari_stack_bytes": PARI_STACK_BYTES,
            "pari_max_prime": PARI_MAX_PRIME,
            "expression": expression,
        },
        "integral_quartic": {
            "variable": "w",
            "coefficients_A4_A2_A0": list(coefficients),
            "equation": f"Y_prime^2={polynomial}",
            "scaling": "Y_prime=q^3*Y",
        },
        "point_set_agreement": True,
        "pari_point_count": len(pari_points),
        "independent_point_count": len(independent_points),
        "points": [
            {"w": fraction_text(w), "Y_prime": fraction_text(y_prime)}
            for w, y_prime in sorted(pari_points)
        ],
        "signed_branch_count": len(branches),
        "both_Y_signs_tested": len(branches) == 2 * len(absolute_point_keys),
        "branches": branches,
        "torsor_certificate_candidates": candidates,
    }


def write_json_atomic(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
    ) as handle:
        temporary_path = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary_path, path)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--libpari", required=True, help="explicit PARI 2.15.4 .so path")
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--q", type=int, required=True)
    parser.add_argument("--numerator-bound", "--N", type=int, required=True)
    parser.add_argument("--denominator-bound", "--D", type=int, required=True)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()
    try:
        record = run_calibration(args)
        exit_code = 0
    except Exception as exc:  # fail closed, including malformed PARI output
        record = {
            "schema": SCHEMA,
            "mode": "CALIBRATION_ONLY",
            "status": "FAIL_CLOSED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        exit_code = 2

    if args.output is not None:
        try:
            write_json_atomic(args.output, record)
        except Exception as exc:
            fallback = {
                "schema": SCHEMA,
                "mode": "CALIBRATION_ONLY",
                "status": "FAIL_CLOSED",
                "error_type": type(exc).__name__,
                "error": f"cannot atomically write output: {exc}",
            }
            print(json.dumps(fallback, indent=2, sort_keys=True), file=sys.stderr)
            return 2
    print(json.dumps(record, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
