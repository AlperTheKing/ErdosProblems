#!/usr/bin/env python3
"""LP-relaxation gate for the C30 unconditional one-step image inequality.

For a cutoff X, source variables s_n describe a forward-closed allowed set S.
Image variables f_n and witness variables linearize F(S), and q_n linearizes
the seed-2 boundary indicator (1-f_m)f_{2m-1}.  The script minimizes

    sum_{hard n <= X} f_n + sum_{2m-1 <= X} q_{2m-1}.

The desired inequality H_F(X) <= Q_F(X) is equivalent to this minimum being
at least the number of hard-shaped values.  Passing this LP is stronger than
the Boolean theorem and would expose a Farkas-dual proof.  Failure supplies a
fractional obstruction, not a counterexample to the Boolean statement.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def admissible_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    out: list[tuple[int, int]] = []
    a = 2
    while a * a < product:
        if product % a == 0:
            b = product // a
            if allowed(a) and allowed(b):
                out.append((a, b))
        a += 1
    return out


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    parent = (n + 1) // 3
    return not (allowed(parent) and parent != 3)


@dataclass
class LPBuilder:
    names: list[str]
    bounds: list[tuple[float, float]]
    rows: list[int]
    cols: list[int]
    data: list[float]
    rhs: list[float]
    row_names: list[str]

    def __init__(self) -> None:
        self.names = []
        self.bounds = []
        self.rows = []
        self.cols = []
        self.data = []
        self.rhs = []
        self.row_names = []

    def var(self, name: str, lo: float = 0.0, hi: float = 1.0) -> int:
        idx = len(self.names)
        self.names.append(name)
        self.bounds.append((lo, hi))
        return idx

    def le(self, terms: dict[int, float], rhs: float, name: str) -> None:
        row = len(self.rhs)
        for col, value in terms.items():
            if value:
                self.rows.append(row)
                self.cols.append(col)
                self.data.append(value)
        self.rhs.append(rhs)
        self.row_names.append(name)

    def matrix(self):
        return coo_matrix(
            (self.data, (self.rows, self.cols)),
            shape=(len(self.rhs), len(self.names)),
            dtype=float,
        ).tocsr()


def solve(limit: int) -> dict:
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pairs = {n: admissible_pairs(n) for n in values}
    hard = [n for n in values if hard_shape(n, pairs[n])]

    lp = LPBuilder()
    s: dict[int, int] = {}
    f: dict[int, int] = {}
    for n in values:
        fixed_seed = n in (2, 3)
        s[n] = lp.var(f"s_{n}", 1.0 if fixed_seed else 0.0, 1.0)
        if fixed_seed:
            f[n] = lp.var(f"f_{n}", 1.0, 1.0)
        elif not pairs[n]:
            f[n] = lp.var(f"f_{n}", 0.0, 0.0)
        else:
            f[n] = lp.var(f"f_{n}")

    witnesses: dict[int, list[int]] = {n: [] for n in values}
    for n in values:
        if n in (2, 3):
            continue
        for j, (a, b) in enumerate(pairs[n]):
            # Forward closure of S: s_a + s_b - s_n <= 1.
            lp.le(
                {s[a]: 1.0, s[b]: 1.0, s[n]: -1.0},
                1.0,
                f"closure_{n}_{a}_{b}",
            )
            w = lp.var(f"w_{n}_{j}")
            witnesses[n].append(w)
            # Convex hull of w = s_a AND s_b.
            lp.le({w: 1.0, s[a]: -1.0}, 0.0, f"w_le_left_{n}_{j}")
            lp.le({w: 1.0, s[b]: -1.0}, 0.0, f"w_le_right_{n}_{j}")
            lp.le(
                {s[a]: 1.0, s[b]: 1.0, w: -1.0},
                1.0,
                f"w_ge_sum_{n}_{j}",
            )
            # f_n >= w.
            lp.le({w: 1.0, f[n]: -1.0}, 0.0, f"f_ge_w_{n}_{j}")
        if witnesses[n]:
            # f_n <= sum_j w_j.
            terms = {f[n]: 1.0}
            terms.update({w: -1.0 for w in witnesses[n]})
            lp.le(terms, 0.0, f"f_le_sum_{n}")

    q: dict[int, int] = {}
    for m in values:
        child = 2 * m - 1
        if child > limit:
            continue
        q[child] = lp.var(f"q_{child}")
        z = q[child]
        # Convex hull of z = (1-f_m) AND f_child.
        lp.le({z: 1.0, f[m]: 1.0}, 1.0, f"q_le_notparent_{child}")
        lp.le({z: 1.0, f[child]: -1.0}, 0.0, f"q_le_child_{child}")
        lp.le(
            {f[child]: 1.0, f[m]: -1.0, z: -1.0},
            0.0,
            f"q_ge_difference_{child}",
        )

    c = np.zeros(len(lp.names), dtype=float)
    for n in hard:
        c[f[n]] += 1.0
    for z in q.values():
        c[z] += 1.0

    result = linprog(
        c,
        A_ub=lp.matrix(),
        b_ub=np.asarray(lp.rhs),
        bounds=lp.bounds,
        method="highs",
        options={"presolve": True},
    )
    payload = {
        "limit": limit,
        "status": int(result.status),
        "message": result.message,
        "variables": len(lp.names),
        "constraints": len(lp.rhs),
        "hard_count": len(hard),
    }
    if result.success:
        objective = float(result.fun)
        payload["objective"] = objective
        payload["fractional_excess"] = len(hard) - objective
        frac = []
        for i, value in enumerate(result.x):
            if 1e-8 < value < 1 - 1e-8:
                frac.append([lp.names[i], float(value)])
        payload["fractional_variables"] = len(frac)
        payload["fractional_sample"] = frac[:80]
        dual_rows = []
        for name, marginal in zip(lp.row_names, result.ineqlin.marginals):
            if abs(marginal) > 1e-8:
                dual_rows.append([name, float(marginal)])
        lower = []
        upper = []
        for name, marginal in zip(lp.names, result.lower.marginals):
            if abs(marginal) > 1e-8:
                lower.append([name, float(marginal)])
        for name, marginal in zip(lp.names, result.upper.marginals):
            if abs(marginal) > 1e-8:
                upper.append([name, float(marginal)])
        payload["dual_nonzero_rows"] = len(dual_rows)
        payload["dual_rows"] = dual_rows[:300]
        payload["dual_nonzero_lower_bounds"] = len(lower)
        payload["dual_lower_bounds"] = lower[:200]
        payload["dual_nonzero_upper_bounds"] = len(upper)
        payload["dual_upper_bounds"] = upper[:200]
        if limit <= 2000:
            source_members = [n for n in values if result.x[s[n]] > 0.5]
            image_members = [n for n in values if result.x[f[n]] > 0.5]
            hard_holes = [n for n in hard if result.x[f[n]] < 0.5]
            boundaries = [
                child for child, z in q.items() if result.x[z] > 0.5
            ]
            payload["source_members"] = source_members
            payload["image_members"] = image_members
            payload["hard_holes"] = hard_holes
            payload["boundaries"] = boundaries
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, default=[54, 100, 200, 500])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = [solve(limit) for limit in args.limits]
    text = json.dumps(rows, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
