#!/usr/bin/env python3
"""LP image inequality with only the exact grounded core forced into S."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

from lp_probe import (
    Model,
    admissible_pairs,
    allowed,
    hard_shape,
)


def grounded_core(
    values: list[int],
    pairs: dict[int, list[tuple[int, int]]],
) -> set[int]:
    ground = {2, 3}
    for value in values:
        if value in ground:
            continue
        if any(left in ground and right in ground for left, right in pairs[value]):
            ground.add(value)
    return ground


def build_ground(limit: int) -> tuple[Model, np.ndarray, float, dict]:
    values = [value for value in range(2, limit + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    hard_values = [value for value in values if hard_shape(value, pairs[value])]
    ground = grounded_core(values, pairs)

    model = Model()
    s = {}
    f = {}
    for value in values:
        forced = value in ground
        s[value] = model.var(f"s_{value}", 1.0 if forced else 0.0, 1.0)
        seed = value in (2, 3)
        f[value] = model.var(f"f_{value}", 1.0 if seed else 0.0, 1.0)

    for value in values:
        if value in (2, 3):
            continue
        local = []
        for pair_index, (left, right) in enumerate(pairs[value]):
            w = model.var(f"w_{value}_{pair_index}")
            local.append(w)
            model.le(f"and_l_{value}_{pair_index}", {w: 1.0, s[left]: -1.0}, 0.0)
            model.le(f"and_r_{value}_{pair_index}", {w: 1.0, s[right]: -1.0}, 0.0)
            model.le(
                f"and_lo_{value}_{pair_index}",
                {s[left]: 1.0, s[right]: 1.0, w: -1.0},
                1.0,
            )
        if local:
            for pair_index, w in enumerate(local):
                model.le(f"or_lo_{value}_{pair_index}", {w: 1.0, f[value]: -1.0}, 0.0)
            terms = {f[value]: 1.0}
            for w in local:
                terms[w] = terms.get(w, 0.0) - 1.0
            model.le(f"or_hi_{value}", terms, 0.0)
        else:
            model.bounds[f[value]] = (0.0, 0.0)

    q = {}
    for parent in values:
        child = 2 * parent - 1
        if child > limit:
            continue
        q[child] = model.var(f"qf_{child}")
        model.le(f"q_not_parent_{child}", {q[child]: 1.0, f[parent]: 1.0}, 1.0)
        model.le(f"q_child_{child}", {q[child]: 1.0, f[child]: -1.0}, 0.0)
        model.le(
            f"q_lower_{child}",
            {f[child]: 1.0, f[parent]: -1.0, q[child]: -1.0},
            0.0,
        )

    c = np.zeros(len(model.names), dtype=float)
    for value in hard_values:
        c[f[value]] += 1.0
    for variable in q.values():
        c[variable] += 1.0
    meta = {
        "values": values,
        "hard_values": hard_values,
        "ground": sorted(ground),
        "following_vars": {str(k): v for k, v in f.items()},
        "boundary_vars": {str(k): v for k, v in q.items()},
    }
    return model, c, float(len(hard_values)), meta


def solve(limit: int, details: bool = True) -> dict:
    model, c, constant, meta = build_ground(limit)
    row_i = []
    col_i = []
    data = []
    rhs = []
    for row_index, row in enumerate(model.rows):
        rhs.append(row.rhs)
        for variable, coefficient in row.terms.items():
            row_i.append(row_index)
            col_i.append(variable)
            data.append(coefficient)
    matrix = coo_matrix(
        (data, (row_i, col_i)),
        shape=(len(model.rows), len(model.names)),
    ).tocsr()
    result = linprog(
        c,
        A_ub=matrix,
        b_ub=np.asarray(rhs),
        bounds=model.bounds,
        method="highs-ds",
    )
    payload = {
        "schema_version": 1,
        "limit": limit,
        "status": int(result.status),
        "message": result.message,
        "variables": len(model.names),
        "inequalities": len(model.rows),
        "ground_size": len(meta["ground"]),
    }
    if not result.success:
        return payload
    x = np.asarray(result.x)
    payload.update(
        {
            "minimum_linear_part": float(result.fun),
            "maximum_excess": constant - float(result.fun),
            "fractional_variable_count": int(
                np.count_nonzero((x > 1e-8) & (x < 1.0 - 1e-8))
            ),
        }
    )
    if not details:
        return payload

    residual = np.asarray(rhs) - matrix @ x
    dual = np.asarray(result.ineqlin.marginals)
    lower_dual = np.asarray(result.lower.marginals)
    upper_dual = np.asarray(result.upper.marginals)
    payload["active_rows"] = [
        {
            "name": model.rows[index].name,
            "slack": float(slack),
            "dual": float(marginal),
        }
        for index, (slack, marginal) in enumerate(zip(residual, dual))
        if abs(slack) <= 1e-8 or abs(marginal) >= 1e-9
    ]
    payload["active_bounds"] = [
        {
            "name": model.names[index],
            "value": float(value),
            "lower_dual": float(lower_dual[index]),
            "upper_dual": float(upper_dual[index]),
        }
        for index, value in enumerate(x)
        if abs(lower_dual[index]) >= 1e-9 or abs(upper_dual[index]) >= 1e-9
    ]
    payload["meta"] = meta
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--limit", type=int)
    mode.add_argument("--stop", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit is not None:
        payload = solve(args.limit, True)
    else:
        cutoffs = [
            value
            for value in range(4, args.stop + 1)
            if allowed(value) and hard_shape(value, admissible_pairs(value))
        ]
        first_positive = None
        minimum_margin = None
        for value in cutoffs:
            result = solve(value, False)
            margin = -result["maximum_excess"]
            minimum_margin = margin if minimum_margin is None else min(minimum_margin, margin)
            if result["maximum_excess"] > 1e-8:
                first_positive = result
                break
        payload = {
            "schema_version": 1,
            "stop": args.stop,
            "tested": len(cutoffs) if first_positive is None else cutoffs.index(first_positive["limit"]) + 1,
            "first_positive": first_positive,
            "minimum_margin": minimum_margin,
        }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({k: payload[k] for k in payload if k in {"limit", "stop", "tested", "status", "maximum_excess", "fractional_variable_count", "first_positive", "minimum_margin"}}))


if __name__ == "__main__":
    main()
