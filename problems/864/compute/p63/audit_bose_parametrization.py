#!/usr/bin/env python3
"""Exact audit of the two-parameter Bose 3-minus-1 solution map."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
ALGEBRA = ROOT / "problems/864/compute/p12/algebraic_scan.py"
DEFAULT_INPUT = ROOT / "problems/864/compute/p63/natural_bose_holes_q29.json"
DEFAULT_OUTPUT = ROOT / "problems/864/compute/p63/bose_parametrization.json"


def load_algebra():
    spec = importlib.util.spec_from_file_location("p63_param_algebra", ALGEBRA)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load finite-field implementation")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def div(field, x, y):
    return field.mul(x, field.pow(y, -1))


def audit_record(algebra, q: int, record: dict[str, object]) -> dict[str, object]:
    prime, degree = algebra.prime_power(q)
    field = algebra.extension_field(prime, 2 * degree)
    theta = field.primitive()
    h = q * q - 1
    residues = []
    exponent_to_t = {}
    t_to_exponent = {}
    power = field.one
    for exponent in range(h):
        t = field.sub(power, theta)
        if field.pow(t, q) == t:
            residues.append(exponent)
            exponent_to_t[exponent] = t
            t_to_exponent[t] = exponent
        power = field.mul(power, theta)
    if len(residues) != q or len(t_to_exponent) != q:
        raise AssertionError("Bose parameter map has the wrong size")

    unit = int(record["unit"])
    base = int(record["base"])
    gamma = int(record["gamma"])
    b = int(record["b"])
    c = (gamma - base) % h
    unit_inverse = pow(unit, -1, h)
    target = ((-2 * c - b) * unit_inverse) % h
    alpha = field.pow(theta, target)
    alpha_inverse = field.pow(alpha, -1)
    theta_q = field.pow(theta, q)
    kappa = field.sub(theta, theta_q)

    formula_solutions = set()
    scalar_pairs = 0
    identity_pairs = 0
    for e1 in residues:
        a1 = field.add(theta, exponent_to_t[e1])
        for e2 in residues:
            a2 = field.add(theta, exponent_to_t[e2])
            p_value = field.mul(field.mul(a1, a2), alpha_inverse)
            p_q = field.pow(p_value, q)
            if p_value == p_q:
                scalar_pairs += 1
                if p_value == field.one:
                    identity_pairs += 1
                    for e3 in residues:
                        formula_solutions.add((e1, e2, e3, e3))
                continue

            numerator = field.add(
                field.sub(kappa, field.mul(p_value, theta)),
                field.mul(p_q, theta_q),
            )
            denominator = field.sub(p_value, p_q)
            t3 = div(field, numerator, denominator)
            if field.pow(t3, q) != t3 or t3 not in t_to_exponent:
                raise AssertionError("formula completion t3 is not in the subfield")
            a3 = field.add(theta, t3)
            a4 = field.mul(p_value, a3)
            t4 = field.sub(a4, theta)
            if field.pow(t4, q) != t4 or t4 not in t_to_exponent:
                raise AssertionError("formula completion t4 is not in the subfield")
            e3 = t_to_exponent[t3]
            e4 = t_to_exponent[t4]
            formula_solutions.add((e1, e2, e3, e4))

    brute_solutions = {
        (e1, e2, e3, e4)
        for e1 in residues
        for e2 in residues
        for e3 in residues
        for e4 in residues
        if (e1 + e2 + e3 - e4 - target) % h == 0
    }
    if formula_solutions != brute_solutions:
        raise AssertionError("parametrization and brute solution sets differ")
    predicted_count = q * q - scalar_pairs + q * identity_pairs
    if predicted_count != len(formula_solutions):
        raise AssertionError("solution-count formula failed")
    if scalar_pairs > q or identity_pairs > 2:
        raise AssertionError("exceptional-pair bounds failed")
    return {
        "q": q,
        "b": b,
        "unit": unit,
        "base": base,
        "gamma": gamma,
        "translation_c": c,
        "target_exponent": target,
        "scalar_pairs": scalar_pairs,
        "identity_pairs": identity_pairs,
        "solution_count": len(formula_solutions),
        "predicted_count": predicted_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--parameters", type=int, nargs="+", default=[3, 4, 5, 7, 8, 9, 11, 13])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    algebra = load_algebra()
    data = json.loads(args.input.read_text(encoding="ascii"))
    by_q = {int(row["q"]): row for row in data["rows"]}
    results = []
    for q in args.parameters:
        row = by_q[q]
        records = [row["minimum_hits_b1"], row["minimum_hits_b2"]]
        for record in records:
            result = audit_record(algebra, q, record)
            results.append(result)
            print(json.dumps(result, sort_keys=True))
    output = {
        "arithmetic": "exact finite fields and integers",
        "records": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
