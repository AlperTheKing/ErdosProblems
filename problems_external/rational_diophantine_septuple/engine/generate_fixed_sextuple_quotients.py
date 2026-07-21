"""Generate exact integral cubic quotients for the two Gibbs sextuples."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import combinations
from math import isqrt
from pathlib import Path


VALUES = {
    "A": Fraction(243, 560),
    "C": Fraction(1100, 63),
    "E": Fraction(95, 112),
    "B": Fraction(1147, 5040),
    "D": Fraction(7820, 567),
    "G": Fraction(196, 45),
    "H": Fraction(38269, 6480),
}

SEXTUPLES = {
    "S_G": ("A", "C", "E", "B", "D", "G"),
    "S_H": ("A", "C", "E", "B", "D", "H"),
}

ACE_COEFFICIENTS = (2568913, 1535181310080, 59427518261760000)


def factor_integer(value: int) -> dict[int, int]:
    factors: dict[int, int] = {}
    n = value
    prime = 2
    while prime * prime <= n:
        while n % prime == 0:
            factors[prime] = factors.get(prime, 0) + 1
            n //= prime
        prime = 3 if prime == 2 else prime + 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def denominator_valuation(value: Fraction, prime: int) -> int:
    denominator = value.denominator
    exponent = 0
    while denominator % prime == 0:
        denominator //= prime
        exponent += 1
    return exponent


def minimum_integral_scale(a2: Fraction, a4: Fraction, a6: Fraction) -> int:
    primes: set[int] = set()
    for coefficient in (a2, a4, a6):
        primes.update(factor_integer(coefficient.denominator))
    scale = 1
    for prime in sorted(primes):
        v2 = denominator_valuation(a2, prime)
        v4 = denominator_valuation(a4, prime)
        v6 = denominator_valuation(a6, prime)
        exponent = max((v2 + 1) // 2, (v4 + 3) // 4, (v6 + 5) // 6)
        scale *= prime**exponent
    return scale


def rational_square(value: Fraction) -> bool:
    if value < 0:
        return False
    numerator_root = isqrt(value.numerator)
    denominator_root = isqrt(value.denominator)
    return (
        numerator_root * numerator_root == value.numerator
        and denominator_root * denominator_root == value.denominator
    )


def assert_sextuple(labels: tuple[str, ...]) -> None:
    values = [VALUES[label] for label in labels]
    if len(set(values)) != 6 or any(value == 0 for value in values):
        raise AssertionError("sextuple values must be distinct and nonzero")
    for left, right in combinations(values, 2):
        if not rational_square(left * right + 1):
            raise AssertionError("declared sextuple failed an exact pair check")


def model_for(labels: tuple[str, str, str]) -> dict[str, object]:
    a, b, c = (VALUES[label] for label in labels)
    leading = a * b * c
    quadratic = a * b + a * c + b * c
    linear = a + b + c
    rational_a2 = quadratic
    rational_a4 = leading * linear
    rational_a6 = leading * leading
    scale = minimum_integral_scale(rational_a2, rational_a4, rational_a6)
    integral_a2 = rational_a2 * scale**2
    integral_a4 = rational_a4 * scale**4
    integral_a6 = rational_a6 * scale**6
    if any(value.denominator != 1 for value in (integral_a2, integral_a4, integral_a6)):
        raise AssertionError("integral scaling failed")
    x_scale = leading * scale**2
    return {
        "degree": 3,
        "triple": "".join(labels),
        "values": [str(value) for value in (a, b, c)],
        "scale_d": scale,
        "x_integral_equals_x_original_times": str(x_scale),
        "ainvariants": [
            0,
            int(integral_a2),
            0,
            int(integral_a4),
            int(integral_a6),
        ],
    }


def quartic_model_for(labels: tuple[str, str, str, str]) -> dict[str, object]:
    roots = [VALUES[label] for label in labels]
    e1 = sum(roots, Fraction(0))
    e2 = sum((left * right for left, right in combinations(roots, 2)), Fraction(0))
    e3 = sum(
        (first * second * third for first, second, third in combinations(roots, 3)),
        Fraction(0),
    )
    e4 = roots[0] * roots[1] * roots[2] * roots[3]
    a, b, c, d, e = e4, e3, e2, e1, Fraction(1)
    invariant_i = 12 * a * e - 3 * b * d + c * c
    invariant_j = (
        72 * a * c * e
        + 9 * b * c * d
        - 27 * a * d * d
        - 27 * b * b * e
        - 2 * c * c * c
    )
    rational_a4 = -27 * invariant_i
    rational_a6 = -27 * invariant_j
    scale = minimum_integral_scale(Fraction(0), rational_a4, rational_a6)
    integral_a4 = rational_a4 * scale**4
    integral_a6 = rational_a6 * scale**6
    if integral_a4.denominator != 1 or integral_a6.denominator != 1:
        raise AssertionError("quartic Jacobian integral scaling failed")
    return {
        "degree": 4,
        "quadruple": "".join(labels),
        "values": [str(value) for value in roots],
        "quartic_coefficients_descending": [
            str(value) for value in (a, b, c, d, e)
        ],
        "invariant_i": str(invariant_i),
        "invariant_j": str(invariant_j),
        "scale_d": scale,
        "ainvariants": [0, 0, 0, int(integral_a4), int(integral_a6)],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()

    records: list[dict[str, object]] = []
    for sextuple_name, labels in SEXTUPLES.items():
        assert_sextuple(labels)
        for triple in combinations(labels, 3):
            record = model_for(triple)
            record["sextuple"] = sextuple_name
            records.append(record)
        for quadruple in combinations(labels, 4):
            record = quartic_model_for(quadruple)
            record["sextuple"] = sextuple_name
            records.append(record)

    ace = next(
        record
        for record in records
        if record["degree"] == 3 and record["triple"] == "ACE"
    )
    if tuple(ace["ainvariants"][index] for index in (1, 3, 4)) != ACE_COEFFICIENTS:
        raise AssertionError("ACE calibration coefficients do not match")
    if ace["scale_d"] != 336:
        raise AssertionError("ACE calibration scale does not match")
    if ace["x_integral_equals_x_original_times"] != "5078700/7":
        raise AssertionError("ACE calibration x-map does not match")

    unique_models = {
        tuple(record["ainvariants"]): record for record in records
    }
    report = {
        "status": "PASS",
        "implementation": "exact-fraction-minimal-integral-scaling",
        "sextuple_pair_checks": 30,
        "cubic_quotient_records": sum(record["degree"] == 3 for record in records),
        "quartic_quotient_records": sum(record["degree"] == 4 for record in records),
        "quotient_records": len(records),
        "unique_integral_models": len(unique_models),
        "ace_calibration": {
            "scale_d": ace["scale_d"],
            "x_integral_equals_x_original_times": ace[
                "x_integral_equals_x_original_times"
            ],
            "ainvariants": ace["ainvariants"],
        },
        "records": records,
    }
    arguments.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "quotient_records": report["quotient_records"],
                "unique_integral_models": report["unique_integral_models"],
                "ace_calibration": report["ace_calibration"],
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
