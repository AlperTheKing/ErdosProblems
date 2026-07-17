#!/usr/bin/env python3
"""LP-relaxation probe for the C23 unconditional one-step image lemma.

This is a discovery gate only.  It keeps the standard convex-hull
linearizations of pair support and seed-2 boundary indicators, together
with every forward-closure inequality and the valid inclusion F(S) <= S.
The variables are continuous in [0,1].
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
class Builder:
    names: list[str]
    lower: list[float]
    upper: list[float]
    rows: list[int]
    cols: list[int]
    data: list[float]
    rhs: list[float]
    row_names: list[str]

    @classmethod
    def empty(cls) -> "Builder":
        return cls([], [], [], [], [], [], [], [])

    def variable(self, name: str, lower: float = 0.0, upper: float = 1.0) -> int:
        index = len(self.names)
        self.names.append(name)
        self.lower.append(lower)
        self.upper.append(upper)
        return index

    def inequality(
        self,
        terms: dict[int, float],
        rhs: float,
        name: str,
    ) -> None:
        row = len(self.rhs)
        for variable, coefficient in terms.items():
            if coefficient:
                self.rows.append(row)
                self.cols.append(variable)
                self.data.append(coefficient)
        self.rhs.append(rhs)
        self.row_names.append(name)


def solve(limit: int, include_dual: bool = False) -> dict:
    values = [value for value in range(2, limit + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    hard = [value for value in values if hard_shape(value, pairs[value])]
    builder = Builder.empty()

    s = {value: builder.variable(f"s_{value}") for value in values}
    f = {value: builder.variable(f"f_{value}") for value in values}
    for seed in (2, 3):
        builder.lower[s[seed]] = builder.upper[s[seed]] = 1.0
        builder.lower[f[seed]] = builder.upper[f[seed]] = 1.0

    witnesses: dict[int, list[int]] = {}
    for value in values:
        local: list[int] = []
        if value not in (2, 3):
            for pair_index, (left, right) in enumerate(pairs[value]):
                # Forward closure: s_left + s_right - s_value <= 1.
                builder.inequality(
                    {s[left]: 1, s[right]: 1, s[value]: -1},
                    1,
                    f"closure_{value}_{left}_{right}",
                )
                witness = builder.variable(f"w_{value}_{pair_index}")
                local.append(witness)
                # Convex hull of witness = s_left AND s_right.
                builder.inequality(
                    {witness: 1, s[left]: -1}, 0, f"and_left_{value}_{pair_index}"
                )
                builder.inequality(
                    {witness: 1, s[right]: -1}, 0, f"and_right_{value}_{pair_index}"
                )
                builder.inequality(
                    {witness: -1, s[left]: 1, s[right]: 1},
                    1,
                    f"and_lower_{value}_{pair_index}",
                )
                # Every witness supports the image value.
                builder.inequality(
                    {witness: 1, f[value]: -1},
                    0,
                    f"support_lower_{value}_{pair_index}",
                )
            if local:
                # The image value has no support beyond these witnesses.
                terms = {f[value]: 1}
                for witness in local:
                    terms[witness] = terms.get(witness, 0) - 1
                builder.inequality(terms, 0, f"support_upper_{value}")
            else:
                builder.lower[f[value]] = builder.upper[f[value]] = 0.0
            # Valid for every integral source and useful in the relaxation.
            builder.inequality(
                {f[value]: 1, s[value]: -1}, 0, f"image_subset_{value}"
            )
        witnesses[value] = local

    boundaries: dict[int, int] = {}
    for parent in values:
        child = 2 * parent - 1
        if child > limit:
            continue
        boundary = builder.variable(f"q_{child}")
        boundaries[child] = boundary
        # Convex hull of q = (1 - f_parent) AND f_child.
        builder.inequality(
            {boundary: 1, f[parent]: 1}, 1, f"boundary_parent_{child}"
        )
        builder.inequality(
            {boundary: 1, f[child]: -1}, 0, f"boundary_child_{child}"
        )
        builder.inequality(
            {boundary: -1, f[parent]: -1, f[child]: 1},
            0,
            f"boundary_lower_{child}",
        )

    objective = np.zeros(len(builder.names))
    for value in hard:
        objective[f[value]] += 1.0
    for boundary in boundaries.values():
        objective[boundary] += 1.0

    matrix = coo_matrix(
        (builder.data, (builder.rows, builder.cols)),
        shape=(len(builder.rhs), len(builder.names)),
    ).tocsr()
    result = linprog(
        objective,
        A_ub=matrix,
        b_ub=np.asarray(builder.rhs),
        bounds=list(zip(builder.lower, builder.upper)),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)

    minimum_cost = float(result.fun)
    excess = len(hard) - minimum_cost
    fractional = [
        {"name": name, "value": float(value)}
        for name, value in zip(builder.names, result.x)
        if 1e-8 < value < 1 - 1e-8
    ]
    output = {
        "limit": limit,
        "allowed_values": len(values),
        "hard_shapes": len(hard),
        "variables": len(builder.names),
        "inequalities": len(builder.rhs),
        "minimum_f_plus_q": minimum_cost,
        "maximum_relaxed_H_minus_Q": excess,
        "fractional_variable_count": len(fractional),
        "fractional_variables_first_40": fractional[:40],
        "solver_status": result.message,
    }
    if include_dual:
        output["dual"] = {
            "inequalities": [
                {
                    "name": builder.row_names[index],
                    "marginal": float(marginal),
                    "slack": float(result.ineqlin.residual[index]),
                    "rhs": builder.rhs[index],
                }
                for index, marginal in enumerate(result.ineqlin.marginals)
                if abs(marginal) > 1e-9
            ],
            "lower_bounds": [
                {
                    "name": builder.names[index],
                    "marginal": float(marginal),
                    "residual": float(result.lower.residual[index]),
                    "bound": builder.lower[index],
                }
                for index, marginal in enumerate(result.lower.marginals)
                if abs(marginal) > 1e-9
            ],
            "upper_bounds": [
                {
                    "name": builder.names[index],
                    "marginal": float(marginal),
                    "residual": float(result.upper.residual[index]),
                    "bound": builder.upper[index],
                }
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
            row["maximum_relaxed_H_minus_Q"],
            row["fractional_variable_count"],
        )


if __name__ == "__main__":
    main()
