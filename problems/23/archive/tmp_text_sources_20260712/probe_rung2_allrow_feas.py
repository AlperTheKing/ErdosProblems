import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

sys.path.append("problems/23/writeup")
sys.path.append("tmp")
import _codex_eq_odl1_rung2_full_residual_check as fullcheck
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import probe_rung2_multirepair_lp as base


def collapsed_source_values(source_cols, sol):
    vals = {}
    for val, source_col in zip(sol, source_cols):
        vals[source_col] = vals.get(source_col, Fraction(0)) + val
    return vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--candidate-mode", choices=["all", "negcoeff"], default="all")
    ap.add_argument("--time-limit", type=float, default=300.0)
    ap.add_argument("--margin", type=float, default=0.0)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    dim, source_cols, _selected_rows = fullcheck.read_core_maps(args.core)
    sol = fullcheck.read_solution(args.solution, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    residual = base.compute_residual(prepared, columns, source_cols, sol)
    source_vals = collapsed_source_values(source_cols, sol)
    negative_source = sorted(c for c, v in source_vals.items() if v < 0)

    if args.candidate_mode == "all":
        candidates = list(range(len(columns)))
    else:
        cand = set(negative_source)
        for c, col in enumerate(columns):
            if any(coeff < 0 for _row, coeff in col.terms):
                cand.add(c)
        candidates = sorted(cand)
    col_index = {c: i for i, c in enumerate(candidates)}

    row_count = len(residual)
    source_offset = row_count
    total_constraints = row_count + len(negative_source)
    mat = lil_matrix((total_constraints, len(candidates)), dtype=float)
    rhs = np.zeros(total_constraints, dtype=float)

    for r, val in enumerate(residual):
        rhs[r] = float(val) - args.margin
    for c, j in col_index.items():
        for row, coeff in columns[c].terms:
            mat[row, j] = float(coeff)

    for i, c in enumerate(negative_source):
        row = source_offset + i
        rhs[row] = float(source_vals[c]) - args.margin
        j = col_index.get(c)
        if j is None:
            # Force infeasibility if the missing candidate is needed.
            rhs[row] = -1.0
        else:
            mat[row, j] = -1.0

    objective = np.ones(len(candidates), dtype=float)
    res = linprog(
        objective,
        A_ub=mat.tocsr(),
        b_ub=rhs,
        bounds=(0, None),
        method="highs",
        options={"time_limit": args.time_limit, "primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10},
    )

    out = {
        "schema": "rung2_allrow_feas_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "core": str(args.core),
        "solution": str(args.solution),
        "candidate_mode": args.candidate_mode,
        "margin": args.margin,
        "row_count": row_count,
        "column_count": len(columns),
        "candidate_count": len(candidates),
        "negative_source": negative_source,
        "linprog_status": int(res.status),
        "linprog_message": res.message,
        "linprog_success": bool(res.success),
        "objective": float(res.fun) if res.success else None,
    }

    if res.success:
        y = res.x
        repaired = [float(x) for x in residual]
        source_float = {c: float(v) for c, v in source_vals.items()}
        used = []
        for val, c in zip(y, candidates):
            if val <= 1e-11:
                continue
            used.append((c, float(val)))
            source_float[c] = source_float.get(c, 0.0) + float(val)
            for row, coeff in columns[c].terms:
                repaired[row] -= float(coeff) * float(val)
        out.update({
            "used_count": len(used),
            "min_residual_float": min(repaired),
            "negative_residual_count": sum(1 for x in repaired if x < -1e-9),
            "min_source_float": min(source_float.values()) if source_float else 0.0,
            "negative_source_count": sum(1 for x in source_float.values() if x < -1e-9),
            "used_prefix": [{"source_col": c, "t": v} for c, v in used[:500]],
        })

    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: out.get(k) for k in [
        "out", "linprog_status", "linprog_success", "objective", "used_count",
        "min_residual_float", "negative_residual_count", "min_source_float", "negative_source_count",
    ]} | {"out": str(args.out)}, sort_keys=True))


if __name__ == "__main__":
    main()


