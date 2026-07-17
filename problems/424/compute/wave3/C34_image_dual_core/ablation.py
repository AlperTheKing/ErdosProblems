#!/usr/bin/env python3
"""Constraint-ablation study for the C34 LP relaxation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

from lp_probe import allowed, admissible_pairs, hard_shape, build


ABLATIONS = {
    "none": (),
    "closure": ("closure_",),
    "and_lower": ("and_lo_",),
    "and_upper": ("and_l_", "and_r_"),
    "or_lower": ("or_lo_",),
    "or_upper": ("or_hi_",),
    "q_lower": ("q_lower_",),
    "q_upper": ("q_not_parent_", "q_child_"),
}


def solve(limit: int, ablation: str) -> dict:
    model, c, constant, _ = build(limit)
    removed_prefixes = ABLATIONS[ablation]
    rows = [
        row
        for row in model.rows
        if not any(row.name.startswith(prefix) for prefix in removed_prefixes)
    ]
    row_i = []
    col_i = []
    data = []
    rhs = []
    for row_index, row in enumerate(rows):
        rhs.append(row.rhs)
        for variable, coefficient in row.terms.items():
            row_i.append(row_index)
            col_i.append(variable)
            data.append(coefficient)
    matrix = coo_matrix(
        (data, (row_i, col_i)),
        shape=(len(rows), len(model.names)),
    ).tocsr()
    result = linprog(
        c,
        A_ub=matrix,
        b_ub=np.asarray(rhs),
        bounds=model.bounds,
        method="highs-ds",
    )
    payload = {
        "limit": limit,
        "ablation": ablation,
        "status": int(result.status),
        "removed_row_count": len(model.rows) - len(rows),
    }
    if result.success:
        x = np.asarray(result.x)
        payload["maximum_excess"] = constant - float(result.fun)
        payload["fractional_variable_count"] = int(
            np.count_nonzero((x > 1e-8) & (x < 1.0 - 1e-8))
        )
        payload["positive_variables"] = [
            [model.names[index], float(value)]
            for index, value in enumerate(x)
            if value > 1e-8
        ]
    return payload


def hard_cutoffs(stop: int) -> list[int]:
    return [
        value
        for value in range(4, stop + 1)
        if allowed(value) and hard_shape(value, admissible_pairs(value))
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stop", type=int, default=500)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = {}
    cutoffs = hard_cutoffs(args.stop)
    for ablation in ABLATIONS:
        first_positive = None
        for limit in cutoffs:
            result = solve(limit, ablation)
            if result.get("maximum_excess", 0.0) > 1e-8:
                first_positive = result
                break
        results[ablation] = {
            "tested": len(cutoffs) if first_positive is None else cutoffs.index(first_positive["limit"]) + 1,
            "first_positive": first_positive,
        }
        print(
            f"ablation={ablation} first_positive="
            f"{None if first_positive is None else first_positive['limit']} "
            f"excess={None if first_positive is None else first_positive['maximum_excess']}"
        )
    payload = {"schema_version": 1, "stop": args.stop, "results": results}
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
