#!/usr/bin/env python3
"""Reconstruct and exactly verify a C34 LP dual certificate."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from lp_probe import build


def rational(value: float, tolerance: float = 1e-7) -> Fraction:
    answer = Fraction(value).limit_denominator(1_000_000)
    if abs(float(answer) - value) > tolerance:
        raise AssertionError((value, answer))
    return answer


def verify(lp_path: Path, cert_path: Path) -> dict:
    source = json.loads(lp_path.read_text(encoding="ascii"))
    limit = int(source["limit"])
    model, c_float, constant, _ = build(limit)
    c = [rational(value) for value in c_float]
    rows = {row.name: row for row in model.rows}

    row_duals = {}
    for entry in source["active_rows"]:
        value = rational(entry["dual"])
        if value:
            if value > 0:
                raise AssertionError((entry["name"], value))
            row_duals[entry["name"]] = value

    lower_duals = {}
    upper_duals = {}
    for entry in source["active_bounds"]:
        lo = rational(entry["lower_dual"])
        hi = rational(entry["upper_dual"])
        if lo:
            if lo < 0:
                raise AssertionError((entry["name"], lo))
            lower_duals[entry["name"]] = lo
        if hi:
            if hi > 0:
                raise AssertionError((entry["name"], hi))
            upper_duals[entry["name"]] = hi

    stationarity = [Fraction(0) for _ in model.names]
    dual_objective = Fraction(0)
    for name, multiplier in row_duals.items():
        row = rows[name]
        dual_objective += multiplier * rational(row.rhs)
        for variable, coefficient in row.terms.items():
            stationarity[variable] += multiplier * rational(coefficient)
    for name, multiplier in lower_duals.items():
        variable = model.index[name]
        stationarity[variable] += multiplier
        dual_objective += multiplier * rational(model.bounds[variable][0])
    for name, multiplier in upper_duals.items():
        variable = model.index[name]
        stationarity[variable] += multiplier
        dual_objective += multiplier * rational(model.bounds[variable][1])

    failures = [
        {
            "variable": model.names[index],
            "actual": str(actual),
            "required": str(required),
        }
        for index, (actual, required) in enumerate(zip(stationarity, c))
        if actual != required
    ]
    target = Fraction(int(constant))
    primal_minimum = rational(source["minimum_linear_part"])
    if failures:
        raise AssertionError(failures[:10])
    if dual_objective != primal_minimum:
        raise AssertionError((dual_objective, primal_minimum))
    if dual_objective < target:
        raise AssertionError((dual_objective, target))

    certificate = {
        "schema_version": 1,
        "limit": limit,
        "claim": "For the C34 LP, sum_hard f_h + sum q_child >= hard_count.",
        "hard_count": int(constant),
        "dual_objective": str(dual_objective),
        "required_lower_bound": str(target),
        "row_duals": {name: str(value) for name, value in row_duals.items()},
        "lower_bound_duals": {
            name: str(value) for name, value in lower_duals.items()
        },
        "upper_bound_duals": {
            name: str(value) for name, value in upper_duals.items()
        },
        "exact_stationarity": True,
    }
    cert_path.write_text(
        json.dumps(certificate, indent=2) + "\n", encoding="ascii"
    )
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lp", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    args = parser.parse_args()
    certificate = verify(args.lp, args.certificate)
    print(
        f"limit={certificate['limit']} exact_dual=PASS "
        f"objective={certificate['dual_objective']} "
        f"rows={len(certificate['row_duals'])}"
    )


if __name__ == "__main__":
    main()


