#!/usr/bin/env python3
"""LP relaxation probe for the unconditional image inequality.

This mirrors C33's CP-SAT formulation, but replaces every Boolean variable by
the interval [0,1].  It is a discovery tool: floating-point LP output is never
treated as a proof.  The emitted active rows and dual values are intended for
exact rational reconstruction.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def admissible_pairs(value: int) -> list[tuple[int, int]]:
    product = value + 1
    out = []
    left = 2
    while left * left < product:
        if product % left == 0:
            right = product // left
            if allowed(left) and allowed(right):
                out.append((left, right))
        left += 1
    return out


def hard_shape(value: int, pairs: list[tuple[int, int]]) -> bool:
    if value % 2 or not pairs:
        return False
    if (value + 1) % 3:
        return True
    parent = (value + 1) // 3
    return not (allowed(parent) and parent != 3)


@dataclass
class Row:
    name: str
    terms: dict[int, float]
    rhs: float


class Model:
    def __init__(self) -> None:
        self.names: list[str] = []
        self.index: dict[str, int] = {}
        self.bounds: list[tuple[float, float]] = []
        self.rows: list[Row] = []

    def var(self, name: str, lo: float = 0.0, hi: float = 1.0) -> int:
        if name in self.index:
            raise ValueError(name)
        idx = len(self.names)
        self.names.append(name)
        self.index[name] = idx
        self.bounds.append((lo, hi))
        return idx

    def le(self, name: str, terms: dict[int, float], rhs: float) -> None:
        clean = {idx: value for idx, value in terms.items() if value}
        self.rows.append(Row(name, clean, rhs))


def build(limit: int) -> tuple[Model, np.ndarray, float, dict]:
    values = [value for value in range(2, limit + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    hard_values = [value for value in values if hard_shape(value, pairs[value])]

    model = Model()
    s = {}
    f = {}
    for value in values:
        seed = value in (2, 3)
        s[value] = model.var(f"s_{value}", 1.0 if seed else 0.0, 1.0)
        f[value] = model.var(f"f_{value}", 1.0 if seed else 0.0, 1.0)

    witnesses: dict[int, list[int]] = {}
    for value in values:
        if value in (2, 3):
            witnesses[value] = []
            continue
        local = []
        for pair_index, (left, right) in enumerate(pairs[value]):
            model.le(
                f"closure_{value}_{left}_{right}",
                {s[left]: 1.0, s[right]: 1.0, s[value]: -1.0},
                1.0,
            )
            w = model.var(f"w_{value}_{pair_index}")
            local.append(w)
            model.le(f"and_l_{value}_{pair_index}", {w: 1.0, s[left]: -1.0}, 0.0)
            model.le(f"and_r_{value}_{pair_index}", {w: 1.0, s[right]: -1.0}, 0.0)
            model.le(
                f"and_lo_{value}_{pair_index}",
                {s[left]: 1.0, s[right]: 1.0, w: -1.0},
                1.0,
            )
        witnesses[value] = local
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

    # linprog minimizes c*x.  The desired maximum is
    # |hard| - sum_hard f_h - sum_child q_child.
    c = np.zeros(len(model.names), dtype=float)
    for value in hard_values:
        c[f[value]] += 1.0
    for variable in q.values():
        c[variable] += 1.0
    objective_constant = float(len(hard_values))
    meta = {
        "values": values,
        "hard_values": hard_values,
        "pairs": {str(k): v for k, v in pairs.items()},
        "following_vars": {str(k): v for k, v in f.items()},
        "boundary_vars": {str(k): v for k, v in q.items()},
    }
    return model, c, objective_constant, meta


def solve(limit: int, output: Path) -> dict:
    model, c, constant, meta = build(limit)
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
        options={"presolve": True},
    )
    payload = {
        "schema_version": 1,
        "limit": limit,
        "status": int(result.status),
        "message": result.message,
        "variables": len(model.names),
        "inequalities": len(model.rows),
    }
    if not result.success:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
        return payload

    x = np.asarray(result.x)
    residual = np.asarray(rhs) - matrix @ x
    dual = np.asarray(result.ineqlin.marginals)
    lower_dual = np.asarray(result.lower.marginals)
    upper_dual = np.asarray(result.upper.marginals)
    lp_excess = constant - float(result.fun)
    active_rows = []
    for index, (slack, marginal) in enumerate(zip(residual, dual)):
        if abs(slack) <= 1e-8 or abs(marginal) >= 1e-9:
            active_rows.append(
                {
                    "name": model.rows[index].name,
                    "slack": float(slack),
                    "dual": float(marginal),
                }
            )
    active_bounds = []
    for index, value in enumerate(x):
        if abs(lower_dual[index]) >= 1e-9 or abs(upper_dual[index]) >= 1e-9:
            active_bounds.append(
                {
                    "name": model.names[index],
                    "value": float(value),
                    "lower_dual": float(lower_dual[index]),
                    "upper_dual": float(upper_dual[index]),
                }
            )
    fractional = [
        {"name": model.names[i], "value": float(value)}
        for i, value in enumerate(x)
        if 1e-8 < value < 1.0 - 1e-8
    ]
    payload.update(
        {
            "minimum_linear_part": float(result.fun),
            "maximum_excess": lp_excess,
            "fractional_variable_count": len(fractional),
            "fractional_variables": fractional,
            "active_rows": active_rows,
            "active_bounds": active_bounds,
            "objective_dual_check": {
                "primal_min": float(result.fun),
                "inequality_rhs_dot_dual": float(np.dot(rhs, dual)),
                "lower_rhs_dot_dual": float(
                    sum(model.bounds[i][0] * lower_dual[i] for i in range(len(x)))
                ),
                "upper_rhs_dot_dual": float(
                    sum(model.bounds[i][1] * upper_dual[i] for i in range(len(x)))
                ),
            },
            "meta": meta,
        }
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = solve(args.limit, args.output)
    print(
        f"limit={args.limit} status={payload['status']} "
        f"lp_excess={payload.get('maximum_excess')} "
        f"fractional={payload.get('fractional_variable_count')}"
    )


if __name__ == "__main__":
    main()
