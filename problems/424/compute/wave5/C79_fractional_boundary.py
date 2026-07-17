#!/usr/bin/env python3
"""Finite LP gate for the C79 fractional boundary inequality.

For allowed values n, let u_n lie in [0,1].  Seeds have value zero,
structural splitless nonseeds have value one, and every admissible
factorization ab=n+1 imposes u_n <= u_a+u_b.  Along the distinguished
seed-2 edge p -> 2p-1, q records at least the positive drop u_p-u_c.

The conjectured inequality is sum_h u_h <= sum_c q_c, where h ranges over
the hard-shaped values through the cutoff.  This script is a finite
floating-point discovery gate; exact acceptance is done by the companion
rational-dual replay.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def admissible_pairs(value: int) -> list[tuple[int, int]]:
    product = value + 1
    result: list[tuple[int, int]] = []
    for left in range(2, math.isqrt(product) + 1):
        if product % left:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return result


def hard_shape(value: int, pairs: list[tuple[int, int]]) -> bool:
    if value % 2 or not pairs:
        return False
    if (value + 1) % 3:
        return True
    parent = (value + 1) // 3
    return not (allowed(parent) and parent != 3)


@dataclass
class Model:
    names: list[str]
    lower: list[float]
    upper: list[float | None]
    rows: list[int]
    cols: list[int]
    data: list[int]
    rhs: list[int]
    row_names: list[str]

    @classmethod
    def empty(cls) -> "Model":
        return cls([], [], [], [], [], [], [], [])

    def variable(
        self, name: str, lower: float = 0.0, upper: float | None = 1.0
    ) -> int:
        index = len(self.names)
        self.names.append(name)
        self.lower.append(lower)
        self.upper.append(upper)
        return index

    def inequality(self, terms: dict[int, int], rhs: int, name: str) -> None:
        row = len(self.rhs)
        for variable, coefficient in terms.items():
            if coefficient:
                self.rows.append(row)
                self.cols.append(variable)
                self.data.append(coefficient)
        self.rhs.append(rhs)
        self.row_names.append(name)


def build(limit: int) -> tuple[Model, list[int], list[int], list[int]]:
    values = [value for value in range(2, limit + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    hard = [value for value in values if hard_shape(value, pairs[value])]
    splitless = [value for value in values if value not in (2, 3) and not pairs[value]]
    model = Model.empty()
    u = {value: model.variable(f"u_{value}") for value in values}

    for seed in (2, 3):
        model.lower[u[seed]] = model.upper[u[seed]] = 0.0
    for value in splitless:
        model.lower[u[value]] = model.upper[u[value]] = 1.0

    for value in values:
        for left, right in pairs[value]:
            model.inequality(
                {u[value]: 1, u[left]: -1, u[right]: -1},
                0,
                f"subadd_{value}_{left}_{right}",
            )

    boundary_variables: list[int] = []
    for parent in values:
        child = 2 * parent - 1
        if child > limit:
            continue
        # The objective minimizes q, so q<=1 is redundant.  Leaving it
        # unbounded above makes the dual boundary capacity visibly at most 1.
        q = model.variable(f"q_{child}", upper=None)
        boundary_variables.append(q)
        model.inequality(
            {u[parent]: 1, u[child]: -1, q: -1},
            0,
            f"boundary_{parent}_{child}",
        )

    objective = [0] * len(model.names)
    for value in hard:
        objective[u[value]] -= 1
    for q in boundary_variables:
        objective[q] += 1
    return model, objective, hard, splitless


def solve(limit: int, include_dual: bool = False) -> dict:
    model, objective, hard, splitless = build(limit)
    matrix = coo_matrix(
        (model.data, (model.rows, model.cols)),
        shape=(len(model.rhs), len(model.names)),
    ).tocsr()
    result = linprog(
        np.asarray(objective, dtype=float),
        A_ub=matrix,
        b_ub=np.asarray(model.rhs, dtype=float),
        bounds=list(zip(model.lower, model.upper)),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)

    maximum_excess = -float(result.fun)
    fractional = [
        {"name": name, "value": float(value)}
        for name, value in zip(model.names, result.x)
        if 1e-8 < value < 1 - 1e-8
    ]
    output = {
        "limit": limit,
        "hard_shapes": len(hard),
        "splitless_values": len(splitless),
        "variables": len(model.names),
        "inequalities": len(model.rhs),
        "minimum_boundary_minus_hard": float(result.fun),
        "maximum_fractional_hard_minus_boundary": maximum_excess,
        "fractional_variable_count": len(fractional),
        "fractional_variables_first_40": fractional[:40],
        "solver_status": result.message,
    }
    if include_dual:
        output["dual"] = {
            "inequalities": [
                {
                    "name": model.row_names[index],
                    "marginal": float(marginal),
                    "slack": float(result.ineqlin.residual[index]),
                }
                for index, marginal in enumerate(result.ineqlin.marginals)
                if abs(marginal) > 1e-9
            ],
            "lower_bounds": [
                {"name": model.names[index], "marginal": float(marginal)}
                for index, marginal in enumerate(result.lower.marginals)
                if abs(marginal) > 1e-9
            ],
            "upper_bounds": [
                {"name": model.names[index], "marginal": float(marginal)}
                for index, marginal in enumerate(result.upper.marginals)
                if abs(marginal) > 1e-9
            ],
        }
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--duals", action="store_true")
    args = parser.parse_args()
    rows = [solve(limit, include_dual=args.duals) for limit in args.limits]
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": 1, "rows": rows}, handle, indent=2)
        handle.write("\n")
    for row in rows:
        print(
            row["limit"],
            row["maximum_fractional_hard_minus_boundary"],
            row["fractional_variable_count"],
        )


if __name__ == "__main__":
    main()
