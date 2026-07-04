import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_full_residual_check as fullcheck
import _codex_eq_odl1_rung2_scipy_core_probe as probe


def compute_residual(prepared, columns, source_cols, sol):
    residual = prepared.p_beta[:]
    for val, source_col in zip(sol, source_cols):
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


def build_row_to_neg_cols(columns):
    out = {}
    for j, col in enumerate(columns):
        for row, coeff in col.terms:
            if coeff < 0:
                out.setdefault(row, []).append(j)
    return out


def solve_active(columns, residual, active_rows, candidate_cols):
    row_index = {r: i for i, r in enumerate(active_rows)}
    col_index = {c: j for j, c in enumerate(candidate_cols)}
    mat = lil_matrix((len(active_rows), len(candidate_cols)), dtype=float)
    scales = []
    for r in active_rows:
        rr = residual[r]
        scales.append(float(-rr) if rr < 0 else 1.0)
    for c, j in col_index.items():
        for row, coeff in columns[c].terms:
            i = row_index.get(row)
            if i is not None:
                mat[i, j] = float(coeff) / scales[i]
    b = np.array([float(residual[r]) / scales[i] for i, r in enumerate(active_rows)], dtype=float)
    return linprog(
        np.ones(len(candidate_cols), dtype=float),
        A_ub=mat.tocsr(),
        b_ub=b,
        bounds=(0, None),
        method="highs",
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--threshold", type=float, default=-1e-12)
    ap.add_argument("--max-iters", type=int, default=24)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    dim, source_cols, _selected_rows = fullcheck.read_core_maps(args.core)
    sol = fullcheck.read_solution(args.solution, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    residual = compute_residual(prepared, columns, source_cols, sol)
    row_to_neg_cols = build_row_to_neg_cols(columns)

    active = sorted(i for i, x in enumerate(residual) if x < 0)
    history = []
    candidate_set = set()
    best = None

    for it in range(args.max_iters):
        for row in active:
            candidate_set.update(row_to_neg_cols.get(row, []))
        candidates = sorted(candidate_set)
        entry = {
            "iter": it,
            "active_rows": len(active),
            "candidate_cols": len(candidates),
        }
        if not candidates:
            entry["status"] = "no_candidates"
            history.append(entry)
            break
        res = solve_active(columns, residual, active, candidates)
        entry.update({
            "linprog_status": int(res.status),
            "linprog_message": res.message,
            "linprog_success": bool(res.success),
            "objective": float(res.fun) if res.success else None,
        })
        if not res.success:
            history.append(entry)
            break

        delta = [0.0] * len(residual)
        used = []
        for val, source_col in zip(res.x, candidates):
            if val <= 1e-11:
                continue
            used.append((source_col, float(val)))
            for row, coeff in columns[source_col].terms:
                delta[row] += float(coeff) * float(val)
        new_float = [float(r) - d for r, d in zip(residual, delta)]
        violated = [i for i, v in enumerate(new_float) if v < args.threshold]
        entry.update({
            "used_cols": len(used),
            "min_residual_float": min(new_float),
            "violated_count": len(violated),
            "violated_prefix": violated[:200],
            "used": [
                {
                    "source_col": c,
                    "t": v,
                    "kind": getattr(columns[c], "kind", None),
                    "name": getattr(columns[c], "name", None),
                    "multiplier_exp": list(getattr(columns[c], "multiplier_exp", ())) if getattr(columns[c], "multiplier_exp", None) is not None else None,
                }
                for c, v in used
            ],
        })
        history.append(entry)
        best = {"used": used, "violated": violated, "new_float": new_float}
        if not violated:
            break
        active = sorted(set(active).union(violated))

    out = {
        "schema": "rung2_multirepair_lp_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "core": str(args.core),
        "solution": str(args.solution),
        "threshold": args.threshold,
        "initial_negative_rows": sorted(i for i, x in enumerate(residual) if x < 0),
        "history": history,
    }
    if best is not None:
        out["final_used_count"] = len(best["used"])
        out["final_violated_count"] = len(best["violated"])
        out["final_min_residual_float"] = min(best["new_float"])
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "out": str(args.out),
        "final_used_count": out.get("final_used_count"),
        "final_violated_count": out.get("final_violated_count"),
        "final_min_residual_float": out.get("final_min_residual_float"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
