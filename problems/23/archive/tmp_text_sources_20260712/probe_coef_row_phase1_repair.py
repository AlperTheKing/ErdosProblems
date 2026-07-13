import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import hstack, lil_matrix

sys.path.append("problems/23/writeup")
sys.path.append("tmp")
import _codex_eq_odl1_rung2_full_residual_check as fullcheck
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import probe_rung2_multirepair_lp as base
from probe_rung2_multirepair_lp_lb import collapsed_source_values


def build_phase1(columns, residual, guard_rows, hard_rows, candidate_cols, lower_bounds):
    guard_rows = list(guard_rows)
    hard_rows = set(hard_rows)
    hard_pos = {r: i for i, r in enumerate(r for r in guard_rows if r in hard_rows)}
    row_index = {r: i for i, r in enumerate(guard_rows)}
    col_index = {c: j for j, c in enumerate(candidate_cols)}
    y_count = len(candidate_cols)
    u_count = len(hard_pos)

    mat_y = lil_matrix((len(guard_rows), y_count), dtype=float)
    scales = []
    for r in guard_rows:
        rr = residual[r]
        scales.append(max(1.0, abs(float(rr))))
    for c, j in col_index.items():
        for row, coeff in columns[c].terms:
            i = row_index.get(row)
            if i is not None:
                mat_y[i, j] = float(coeff) / scales[i]

    mat_u = lil_matrix((len(guard_rows), u_count), dtype=float)
    for r, upos in hard_pos.items():
        mat_u[row_index[r], upos] = -1.0 / scales[row_index[r]]

    mat = hstack([mat_y, mat_u], format="csr")
    b = np.array([float(residual[r]) / scales[i] for i, r in enumerate(guard_rows)], dtype=float)
    c = np.zeros(y_count + u_count, dtype=float)
    c[y_count:] = 1.0
    bounds = [(float(lower_bounds.get(col, Fraction(0))), None) for col in candidate_cols]
    bounds.extend((0.0, None) for _ in range(u_count))
    return mat, b, c, bounds, hard_pos


def build_margin(columns, residual, guard_rows, candidate_cols, lower_bounds, y_penalty):
    guard_rows = list(guard_rows)
    row_index = {r: i for i, r in enumerate(guard_rows)}
    col_index = {c: j for j, c in enumerate(candidate_cols)}
    y_count = len(candidate_cols)

    mat_y = lil_matrix((len(guard_rows), y_count), dtype=float)
    scales = []
    for r in guard_rows:
        rr = residual[r]
        scales.append(max(1.0, abs(float(rr))))
    for c, j in col_index.items():
        for row, coeff in columns[c].terms:
            i = row_index.get(row)
            if i is not None:
                mat_y[i, j] = float(coeff) / scales[i]

    mat_t = lil_matrix((len(guard_rows), 1), dtype=float)
    for i in range(len(guard_rows)):
        mat_t[i, 0] = 1.0 / scales[i]

    mat = hstack([mat_y, mat_t], format="csr")
    b = np.array([float(residual[r]) / scales[i] for i, r in enumerate(guard_rows)], dtype=float)
    c = np.empty(y_count + 1, dtype=float)
    c[:y_count] = y_penalty
    c[y_count] = -1.0
    bounds = [(float(lower_bounds.get(col, Fraction(0))), None) for col in candidate_cols]
    bounds.append((0.0, None))
    return mat, b, c, bounds


def apply_solution(columns, residual, candidate_cols, y_values):
    delta = [0.0] * len(residual)
    used = []
    for val, source_col in zip(y_values, candidate_cols):
        if val <= 1e-11:
            continue
        used.append((source_col, float(val)))
        for row, coeff in columns[source_col].terms:
            delta[row] += float(coeff) * float(val)
    return [float(r) - d for r, d in zip(residual, delta)], used


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--seed-report", type=Path)
    ap.add_argument("--threshold", type=float, default=-1e-12)
    ap.add_argument("--max-iters", type=int, default=80)
    ap.add_argument("--time-limit", type=float, default=None)
    ap.add_argument("--phase2-margin", action="store_true")
    ap.add_argument("--margin-y-penalty", type=float, default=1e-12)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    dim, source_cols, _selected_rows = fullcheck.read_core_maps(args.core)
    sol = fullcheck.read_solution(args.solution, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    residual = base.compute_residual(prepared, columns, source_cols, sol)
    row_to_neg_cols = base.build_row_to_neg_cols(columns)
    source_vals = collapsed_source_values(source_cols, sol)
    lower_bounds = {c: -v for c, v in source_vals.items() if v < 0}

    initial_negative = sorted(i for i, x in enumerate(residual) if x < 0)
    hard = set(initial_negative)
    active = set(initial_negative)
    candidate_set = set(lower_bounds)

    if args.seed_report and args.seed_report.exists():
        seed = json.loads(args.seed_report.read_text(encoding="utf-8"))
        for hist in seed.get("history", []):
            active.update(int(r) for r in hist.get("violated_prefix", []))
        if seed.get("history"):
            for item in seed["history"][-1].get("used", []):
                candidate_set.add(int(item["source_col"]))

    history = []
    best = None
    options = {}
    if args.time_limit is not None:
        options["time_limit"] = args.time_limit

    for it in range(args.max_iters):
        for row in active:
            candidate_set.update(row_to_neg_cols.get(row, []))
        candidates = sorted(candidate_set)
        guard = sorted(active | hard)
        entry = {
            "iter": it,
            "guard_rows": len(guard),
            "hard_rows": len(hard),
            "candidate_cols": len(candidates),
            "forced_lower_bounds": len(lower_bounds),
        }
        if not candidates:
            entry["status"] = "no_candidates"
            history.append(entry)
            break

        mat, b, obj, bounds, hard_pos = build_phase1(
            columns, residual, guard, hard, candidates, lower_bounds
        )
        res = linprog(
            obj,
            A_ub=mat,
            b_ub=b,
            bounds=bounds,
            method="highs",
            options=options or None,
        )
        entry.update({
            "linprog_status": int(res.status),
            "linprog_message": res.message,
            "linprog_success": bool(res.success),
            "phase1_objective": float(res.fun) if res.success else None,
        })
        if not res.success:
            history.append(entry)
            break

        y = res.x[: len(candidates)]
        margin_value = None
        if args.phase2_margin and entry["phase1_objective"] <= 1e-9:
            mat2, b2, obj2, bounds2 = build_margin(
                columns, residual, guard, candidates, lower_bounds, args.margin_y_penalty
            )
            res2 = linprog(
                obj2,
                A_ub=mat2,
                b_ub=b2,
                bounds=bounds2,
                method="highs",
                options=options or None,
            )
            entry.update({
                "phase2_status": int(res2.status),
                "phase2_message": res2.message,
                "phase2_success": bool(res2.success),
            })
            if res2.success:
                y = res2.x[: len(candidates)]
                margin_value = float(res2.x[len(candidates)])
                entry["phase2_margin"] = margin_value
            else:
                entry["phase2_margin"] = None
        new_float, used = apply_solution(columns, residual, candidates, y)
        violated = [i for i, v in enumerate(new_float) if v < args.threshold]
        entry.update({
            "used_cols": len(used),
            "slack_vars": len(hard_pos),
            "min_residual_float": min(new_float),
            "margin_value": margin_value,
            "violated_count": len(violated),
            "violated_prefix": violated[:200],
            "used": [
                {
                    "source_col": c,
                    "t": v,
                    "forced_lb": str(lower_bounds.get(c, Fraction(0))),
                    "kind": getattr(columns[c], "kind", None),
                    "name": getattr(columns[c], "name", None),
                    "multiplier_exp": list(getattr(columns[c], "multiplier_exp", ())) if getattr(columns[c], "multiplier_exp", None) is not None else None,
                }
                for c, v in used
            ],
        })
        history.append(entry)
        best = {"used": used, "violated": violated, "new_float": new_float}
        if not violated and entry["phase1_objective"] <= 1e-9:
            break
        hard.update(violated)
        active.update(violated)

    out = {
        "schema": "coef_row_phase1_repair_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "core": str(args.core),
        "solution": str(args.solution),
        "seed_report": str(args.seed_report) if args.seed_report else None,
        "threshold": args.threshold,
        "initial_negative_rows": initial_negative,
        "negative_source_columns": {str(c): str(v) for c, v in source_vals.items() if v < 0},
        "history": history,
    }
    if best is not None:
        out["final_used_count"] = len(best["used"])
        out["final_violated_count"] = len(best["violated"])
        out["final_min_residual_float"] = min(best["new_float"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "out": str(args.out),
        "final_used_count": out.get("final_used_count"),
        "final_violated_count": out.get("final_violated_count"),
        "final_min_residual_float": out.get("final_min_residual_float"),
        "last_phase1_objective": history[-1].get("phase1_objective") if history else None,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
