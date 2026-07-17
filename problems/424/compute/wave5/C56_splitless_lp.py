#!/usr/bin/env python3
"""LP gate for H_T(X) <= Q_T(X) on splitless-free closed sets T.

This deliberately drops the image variables from C56_image_lp_dual.py.
Every structural splitless nonseed is fixed outside T, while T is required
to contain 2,3 and be forward closed.  Passing is a stronger and cleaner
linear statement than the C30 one-step image inequality.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("c56_image", HERE / "C56_image_lp_dual.py")
assert SPEC and SPEC.loader
C56 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C56
SPEC.loader.exec_module(C56)


def solve(limit: int) -> dict:
    values = [n for n in range(2, limit + 1) if C56.allowed(n)]
    pairs = {n: C56.admissible_pairs(n) for n in values}
    hard = [n for n in values if C56.hard_shape(n, pairs[n])]
    splitless = [n for n in values if n not in (2, 3) and not pairs[n]]

    lp = C56.LPBuilder()
    t: dict[int, int] = {}
    for n in values:
        if n in (2, 3):
            t[n] = lp.var(f"t_{n}", 1.0, 1.0)
        elif n in splitless:
            t[n] = lp.var(f"t_{n}", 0.0, 0.0)
        else:
            t[n] = lp.var(f"t_{n}")

    for n in values:
        for a, b in pairs[n]:
            lp.le(
                {t[a]: 1.0, t[b]: 1.0, t[n]: -1.0},
                1.0,
                f"closure_{n}_{a}_{b}",
            )

    q: dict[int, int] = {}
    for m in values:
        child = 2 * m - 1
        if child > limit:
            continue
        z = lp.var(f"q_{child}")
        q[child] = z
        lp.le({z: 1.0, t[m]: 1.0}, 1.0, f"q_le_notparent_{child}")
        lp.le({z: 1.0, t[child]: -1.0}, 0.0, f"q_le_child_{child}")
        lp.le(
            {t[child]: 1.0, t[m]: -1.0, z: -1.0},
            0.0,
            f"q_ge_difference_{child}",
        )

    c = np.zeros(len(lp.names), dtype=float)
    for n in hard:
        c[t[n]] += 1.0
    for z in q.values():
        c[z] += 1.0
    result = linprog(
        c,
        A_ub=lp.matrix(),
        b_ub=np.asarray(lp.rhs),
        bounds=lp.bounds,
        method="highs",
    )
    out = {
        "limit": limit,
        "status": int(result.status),
        "message": result.message,
        "variables": len(lp.names),
        "constraints": len(lp.rhs),
        "hard_count": len(hard),
        "splitless_count": len(splitless),
    }
    if result.success:
        out["objective"] = float(result.fun)
        out["fractional_excess"] = len(hard) - float(result.fun)
        fractional = [
            [lp.names[i], float(x)]
            for i, x in enumerate(result.x)
            if 1e-8 < x < 1 - 1e-8
        ]
        out["fractional_variables"] = len(fractional)
        out["fractional_sample"] = fractional[:100]
        dual = [
            [name, float(y)]
            for name, y in zip(lp.row_names, result.ineqlin.marginals)
            if abs(y) > 1e-8
        ]
        out["dual_nonzero_rows"] = len(dual)
        out["dual_rows"] = dual[:400]
        if limit <= 2000:
            out["members"] = [n for n in values if result.x[t[n]] > 0.5]
            out["hard_holes"] = [n for n in hard if result.x[t[n]] < 0.5]
            out["boundaries"] = [child for child, z in q.items() if result.x[z] > 0.5]
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limits", nargs="+", type=int, default=[54, 100, 200, 500])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = [solve(n) for n in args.limits]
    text = json.dumps(rows, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
