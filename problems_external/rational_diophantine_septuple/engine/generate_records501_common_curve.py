#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from math import gcd, isqrt, prod
from pathlib import Path


VALUES = {
    "a": Fraction(17, 120),
    "b": Fraction(122, 255),
    "c": Fraction(728, 2295),
    "d": Fraction(1325, 408),
    "e": Fraction(5643, 680),
}
F = Fraction(-237800, 2019651)
G = Fraction(35224, 15)
EXPECTED_COEFFICIENTS = [
    38967557760000,
    486447135120000,
    1482193736218800,
    1104168410441550,
    287422413162436,
    22578550394400,
]


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def rational_square_root(value: Fraction) -> Fraction | None:
    if value < 0:
        return None
    numerator_root = isqrt(value.numerator)
    denominator_root = isqrt(value.denominator)
    if numerator_root * numerator_root != value.numerator:
        return None
    if denominator_root * denominator_root != value.denominator:
        return None
    return Fraction(numerator_root, denominator_root)


def multiply_polynomials(left: list[int], right: list[int]) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            result[i + j] += left_value * right_value
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=False)

    quintuple_roots: dict[str, str] = {}
    labels = list(VALUES)
    for i, left_label in enumerate(labels):
        for right_label in labels[i + 1 :]:
            root = rational_square_root(VALUES[left_label] * VALUES[right_label] + 1)
            assert root is not None
            quintuple_roots[left_label + right_label] = fraction_text(root)

    extension_roots: dict[str, dict[str, str]] = {"f": {}, "g": {}}
    for extension_label, extension in (("f", F), ("g", G)):
        for label, value in VALUES.items():
            root = rational_square_root(extension * value + 1)
            assert root is not None
            extension_roots[extension_label][label] = fraction_text(root)

    assert len(set(VALUES.values()) | {F, G}) == 7
    assert all(value != 0 for value in set(VALUES.values()) | {F, G})
    incompatibility = F * G + 1
    assert incompatibility == Fraction(-98187911, 356409)
    assert incompatibility < 0

    denominator_product = prod(value.denominator for value in VALUES.values())
    assert denominator_product == 2 * 3121200**2
    y_scale = 6242400
    assert y_scale**2 == 2 * denominator_product

    coefficients = [2]
    factors: list[dict[str, int | str]] = []
    magma_factors: list[str] = []
    for label, value in VALUES.items():
        numerator = value.numerator
        denominator = value.denominator
        assert gcd(numerator, denominator) == 1 and denominator > 0
        coefficients = multiply_polynomials(coefficients, [denominator, numerator])
        factors.append({"label": label, "numerator": numerator, "denominator": denominator})
        magma_factors.append(f"({denominator}+({numerator})*x)")
    assert coefficients == EXPECTED_COEFFICIENTS
    magma_polynomial = "2*" + "*".join(magma_factors)

    common_header = "\n".join(
        [
            "Q := Rationals();",
            "P<x> := PolynomialRing(Q);",
            'label := "RECORDS501_502_COMMON";',
            f"f := {magma_polynomial};",
            'print "LABEL", label;',
            'print "DEGREE", Degree(f);',
            'print "COEFFICIENTS", Coefficients(f);',
            'print "DISCRIMINANT_NONZERO", Discriminant(f) ne 0;',
            "C := HyperellipticCurve(f);",
            "J := Jacobian(C);",
        ]
    )
    rank_code = common_header + "\n" + "\n".join(
        [
            "lower, upper := RankBounds(J);",
            'print "RANK_BOUNDS", lower, upper;',
            'print "DONE";',
            "",
        ]
    )
    points_code = common_header + "\n" + "\n".join(
        [
            "pts, complete, height_return := RationalPointsGenus2(C);",
            'print "POINT_COUNT", #pts;',
            'print "POINTS", pts;',
            'print "COMPLETE", complete;',
            'print "HEIGHT_RETURN", height_return;',
            'print "DONE";',
            "",
        ]
    )

    rank_path = run_dir / "input_rank.m"
    points_path = run_dir / "input_points.m"
    rank_path.write_text(rank_code, encoding="ascii", newline="\n")
    points_path.write_text(points_code, encoding="ascii", newline="\n")

    model = {
        "run_id": run_dir.name,
        "fixed_quintuple": {label: fraction_text(value) for label, value in VALUES.items()},
        "known_extensions": {"f": fraction_text(F), "g": fraction_text(G)},
        "quintuple_roots": quintuple_roots,
        "extension_roots": extension_roots,
        "known_extension_product_plus_one": fraction_text(incompatibility),
        "factors": factors,
        "twist_q": 2,
        "denominator_product": denominator_product,
        "y_scale": y_scale,
        "coefficients_low_to_high": coefficients,
        "rank_input_sha256": sha256(rank_path),
        "points_input_sha256": sha256(points_path),
    }
    model_path = run_dir / "model.json"
    model_path.write_text(json.dumps(model, indent=2) + "\n", encoding="ascii", newline="\n")

    manifest = {
        "run_id": run_dir.name,
        "objective": "Determine every rational extension of the records 501/502 common quintuple through one genus-2 curve",
        "status": "READY",
        "bridge": "Every extension maps to C_Q; a complete point list plus exact individual-square filtering and one compatibility edge yields a septuple",
        "model_sha256": sha256(model_path),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "rank_input_sha256": sha256(rank_path),
        "points_input_sha256": sha256(points_path),
        "computer_algebra_system": "Magma V2.29-8",
        "calculator_url": "https://magma.maths.usyd.edu.au/calc/",
        "calculator_limit_seconds_per_job": 60,
        "first_job": "RankBounds(Jacobian(C_Q))",
        "conditional_second_job": "RationalPointsGenus2(C_Q) only if the proven upper rank is at most one",
        "point_acceptance": "Only complete=true is exhaustive; when complete=false, ignore the searched-height return",
        "exit": "An exact compatible pair proves existence; otherwise rank upper>1, timeout, or incomplete points stops the final catalogue lane without inference",
    }
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="ascii", newline="\n")

    print(json.dumps({"run_dir": str(run_dir), "manifest_sha256": sha256(manifest_path), "model": model}, indent=2))


if __name__ == "__main__":
    main()
