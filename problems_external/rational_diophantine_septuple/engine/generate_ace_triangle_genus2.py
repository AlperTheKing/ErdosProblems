"""Generate the seven exact ACE-triangle genus-2 quotient models."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
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

SUBSETS = (
    ("A", "C", "E", "G", "B"),
    ("A", "C", "E", "G", "D"),
    ("A", "C", "E", "B", "D"),
    ("A", "C", "E", "G", "B", "D"),
    ("A", "C", "E", "B", "H"),
    ("A", "C", "E", "D", "H"),
    ("A", "C", "E", "B", "D", "H"),
)

EXPECTED_SCALES = {
    "ACEGB": (5, 2116800),
    "ACEGD": (1, 317520),
    "ACEBD": (7, 8890560),
    "ACEGBD": (35, 133358400),
    "ACEBH": (5, 25401600),
    "ACEDH": (1, 3810240),
    "ACEBDH": (35, 1600300800),
}


def multiply_polynomials(left: list[int], right: list[int]) -> list[int]:
    output = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            output[left_index + right_index] += left_value * right_value
    return output


def squarefree_part(value: int) -> int:
    part = 1
    n = value
    prime = 2
    while prime * prime <= n:
        exponent = 0
        while n % prime == 0:
            n //= prime
            exponent += 1
        if exponent % 2:
            part *= prime
        prime = 3 if prime == 2 else prime + 2
    if n > 1:
        part *= n
    return part


def build_record(labels: tuple[str, ...]) -> dict[str, object]:
    label = "".join(labels)
    if len(set(labels)) != len(labels):
        raise AssertionError("repeated factor label")
    values = [VALUES[item] for item in labels]
    denominator_product = 1
    integral_product = [1]
    for value in values:
        denominator_product *= value.denominator
        integral_product = multiply_polynomials(
            integral_product, [value.denominator, value.numerator]
        )
    twist = squarefree_part(denominator_product)
    square_part = denominator_product // twist
    square_root = isqrt(square_part)
    if square_root * square_root != square_part:
        raise AssertionError("denominator decomposition failed")
    y_scale = twist * square_root
    expected = EXPECTED_SCALES[label]
    if (twist, y_scale) != expected:
        raise AssertionError(
            f"{label} scale mismatch: {(twist, y_scale)} != {expected}"
        )
    integral_coefficients = [twist * value for value in integral_product]
    if integral_coefficients[-1] == 0 or len(integral_coefficients) not in (6, 7):
        raise AssertionError("model is not degree five or six")
    factors = [
        f"({value.denominator}+({value.numerator})*x)" for value in values
    ]
    magma_code = "\n".join(
        [
            "Q := Rationals();",
            "P<x> := PolynomialRing(Q);",
            f'label := "{label}";',
            f"f := {twist}*" + "*".join(factors) + ";",
            "print \"LABEL\", label;",
            "print \"DEGREE\", Degree(f);",
            "print \"DISCRIMINANT_NONZERO\", Discriminant(f) ne 0;",
            "C := HyperellipticCurve(f);",
            "J := Jacobian(C);",
            "lower, upper := RankBounds(J);",
            "print \"RANK_BOUNDS\", lower, upper;",
            "print \"DONE\";",
            "",
        ]
    )
    return {
        "label": label,
        "factor_labels": list(labels),
        "factor_values": [str(value) for value in values],
        "degree": len(labels),
        "twist_q": twist,
        "y_integral_equals_y_original_times": y_scale,
        "integral_coefficients_ascending": integral_coefficients,
        "magma_code": magma_code,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    arguments = parser.parse_args()
    arguments.output_dir.mkdir(parents=True, exist_ok=True)

    records = [build_record(labels) for labels in SUBSETS]
    if len({record["label"] for record in records}) != 7:
        raise AssertionError("genus-2 labels are not unique")
    for record in records:
        (arguments.output_dir / f"input_{record['label']}.m").write_text(
            str(record["magma_code"]), encoding="utf-8", newline="\n"
        )

    report = {
        "status": "PASS",
        "implementation": "exact-fraction-integral-hyperelliptic-model",
        "curve_count": len(records),
        "records": records,
    }
    (arguments.output_dir / "models.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "curve_count": report["curve_count"],
                "labels": [record["label"] for record in records],
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
