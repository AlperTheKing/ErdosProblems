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


def build_and_solve(columns, residual, source_vals, h_rows, g_rows, h_source, candidates):
    y_index = {c: j for j, c in enumerate(candidates)}
    u_rows = sorted(h_rows)
    u_source = sorted(h_source)
    row_slack_offset = len(candidates)
    source_slack_offset = row_slack_offset + len(u_rows)
    nvars = len(candidates) + len(u_rows) + len(u_source)

    constraints = []
    rhs = []

    # Residual constraints: residual[r] - A_r y + u_r >= 0.
    for r in sorted(g_rows):
        constraints.append(("res", r))
        rhs.append(float(residual[r]))

    # Source coefficient constraints: s0[c] + y_c + u_c >= 0.
    for c in u_source:
        constraints.append(("src", c))
        rhs.append(float(source_vals[c]))

    mat = lil_matrix((len(constraints), nvars), dtype=float)
    row_pos = {r: i for i, (kind, r) in enumerate(constraints) if kind == "res"}
    h_row_pos = {r: i for i, r in enumerate(u_rows)}
    h_src_pos = {c: i for i, c in enumerate(u_source)}

    for c, j in y_index.items():
        for row, coeff in columns[c].terms:
            i = row_pos.get(row)
            if i is not None:
                mat[i, j] = float(coeff)
    for r, sp in h_row_pos.items():
        i = row_pos[r]
        mat[i, row_slack_offset + sp] = -1.0
    for c, sp in h_src_pos.items():
        i = constraints.index(("src", c))
        if c in y_index:
            mat[i, y_index[c]] = -1.0
        mat[i, source_slack_offset + sp] = -1.0

    objective = np.zeros(nvars, dtype=float)
    objective[row_slack_offset:] = 1.0
    bounds = [(0, None)] * nvars
    return linprog(objective, A_ub=mat.tocsr(), b_ub=np.array(rhs, dtype=float), bounds=bounds, method="highs")


def parse_int_list(text):
    if not text:
        return []
    return [int(x) for x in text.split(",") if x.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--threshold", type=float, default=-1e-12)
    ap.add_argument("--max-iters", type=int, default=40)
    ap.add_argument("--hard-rows", default="")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    dim, source_cols, _selected_rows = fullcheck.read_core_maps(args.core)
    sol = fullcheck.read_solution(args.solution, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    residual = base.compute_residual(prepared, columns, source_cols, sol)
    source_vals = collapsed_source_values(source_cols, sol)
    row_to_neg_cols = base.build_row_to_neg_cols(columns)

    hard_rows = set(parse_int_list(args.hard_rows))
    h_rows = set(i for i, x in enumerate(residual) if x < 0) | hard_rows
    g_rows = set(h_rows)
    h_source = set(c for c, v in source_vals.items() if v < 0)
    candidates = set(h_source)
    history = []
    best = None

    for it in range(args.max_iters):
        for row in g_rows:
            candidates.update(row_to_neg_cols.get(row, []))
        cand = sorted(candidates)
        res = build_and_solve(columns, residual, source_vals, h_rows, g_rows, h_source, cand)
        entry = {
            "iter": it,
            "h_rows": len(h_rows),
            "g_rows": len(g_rows),
            "h_source": len(h_source),
            "candidate_cols": len(cand),
            "linprog_status": int(res.status),
            "linprog_message": res.message,
            "linprog_success": bool(res.success),
            "objective": float(res.fun) if res.success else None,
        }
        if not res.success:
            history.append(entry)
            break

        y = res.x[: len(cand)]
        repaired = residual[:]
        final_source = dict(source_vals)
        used = []
        for val, col in zip(y, cand):
            if val <= 1e-11:
                continue
            used.append((col, float(val)))
            final_source[col] = final_source.get(col, Fraction(0)) + Fraction(str(float(val)))
            for row, coeff in columns[col].terms:
                repaired[row] -= coeff * Fraction(str(float(val)))

        # Float residuals are used only for separation/oracle control.
        repaired_float = [float(x) for x in repaired]
        source_float = {c: float(v) for c, v in final_source.items()}
        viol_rows = [i for i, v in enumerate(repaired_float) if v < args.threshold]
        viol_source = [c for c, v in source_float.items() if v < args.threshold]
        entry.update({
            "used_cols": len(used),
            "violated_rows": len(viol_rows),
            "violated_source": len(viol_source),
            "min_residual_float": min(repaired_float),
            "min_source_float": min(source_float.values()) if source_float else 0.0,
            "violated_rows_prefix": viol_rows[:200],
            "violated_source_prefix": viol_source[:200],
            "used": [{"source_col": c, "t": v} for c, v in used],
        })
        history.append(entry)
        best = {"used": used, "viol_rows": viol_rows, "viol_source": viol_source}
        if not viol_rows and not viol_source and float(res.fun) <= 1e-9:
            break
        before = (len(h_rows), len(g_rows), len(h_source))
        h_rows.update(viol_rows)
        g_rows.update(viol_rows)
        h_source.update(viol_source)
        if before == (len(h_rows), len(g_rows), len(h_source)):
            break

    out = {
        "schema": "rung2_coef_row_phase1_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "core": str(args.core),
        "solution": str(args.solution),
        "threshold": args.threshold,
        "initial_negative_rows": sorted(i for i, x in enumerate(residual) if x < 0),
        "initial_negative_source": sorted(c for c, v in source_vals.items() if v < 0),
        "hard_rows": sorted(hard_rows),
        "history": history,
    }
    if best is not None:
        out["final_used_count"] = len(best["used"])
        out["final_violated_rows"] = len(best["viol_rows"])
        out["final_violated_source"] = len(best["viol_source"])
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "out": str(args.out),
        "final_used_count": out.get("final_used_count"),
        "final_violated_rows": out.get("final_violated_rows"),
        "final_violated_source": out.get("final_violated_source"),
        "last": history[-1] if history else None,
    }, sort_keys=True))


if __name__ == "__main__":
    main()


