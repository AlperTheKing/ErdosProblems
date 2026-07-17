#!/usr/bin/env python3
"""Exact rational verifier for a grounded-core C34 LP dual."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from ground_core_lp import build_ground


def rational(value: float, tolerance: float = 1e-7) -> Fraction:
    answer = Fraction(value).limit_denominator(1_000_000)
    if abs(float(answer) - value) > tolerance:
        raise AssertionError((value, answer))
    return answer


def verify(lp_path: Path, cert_path: Path) -> dict:
    source = json.loads(lp_path.read_text(encoding="ascii"))
    model, c_float, constant, meta = build_ground(int(source["limit"]))
    c = [rational(value) for value in c_float]
    rows = {row.name: row for row in model.rows}

    row_duals = {
        entry["name"]: rational(entry["dual"])
        for entry in source["active_rows"]
        if rational(entry["dual"])
    }
    lower_duals = {
        entry["name"]: rational(entry["lower_dual"])
        for entry in source["active_bounds"]
        if rational(entry["lower_dual"])
    }
    upper_duals = {
        entry["name"]: rational(entry["upper_dual"])
        for entry in source["active_bounds"]
        if rational(entry["upper_dual"])
    }
    if any(value > 0 for value in row_duals.values()):
        raise AssertionError("positive <=-row dual")
    if any(value < 0 for value in lower_duals.values()):
        raise AssertionError("negative lower-bound dual")
    if any(value > 0 for value in upper_duals.values()):
        raise AssertionError("positive upper-bound dual")

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
        (model.names[index], actual, required)
        for index, (actual, required) in enumerate(zip(stationarity, c))
        if actual != required
    ]
    if failures:
        raise AssertionError(failures[:10])
    primal = rational(source["minimum_linear_part"])
    required = Fraction(int(constant))
    if dual_objective != primal or dual_objective < required:
        raise AssertionError((dual_objective, primal, required))

    certificate = {
        "schema_version": 1,
        "limit": int(source["limit"]),
        "ground_size": len(meta["ground"]),
        "dual_objective": str(dual_objective),
        "required_lower_bound": str(required),
        "row_duals": {name: str(value) for name, value in row_duals.items()},
        "lower_bound_duals": {name: str(value) for name, value in lower_duals.items()},
        "upper_bound_duals": {name: str(value) for name, value in upper_duals.items()},
        "exact_stationarity": True,
    }
    cert_path.write_text(json.dumps(certificate, indent=2) + "\n", encoding="ascii")
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lp", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    args = parser.parse_args()
    certificate = verify(args.lp, args.certificate)
    print(
        f"limit={certificate['limit']} exact_ground_dual=PASS "
        f"objective={certificate['dual_objective']} "
        f"rows={len(certificate['row_duals'])}"
    )


if __name__ == "__main__":
    main()
