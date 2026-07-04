import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_modular_replay as replay
from _codex_eq_odl1_rung2_source_solution_check import read_source_solution


def compute_residual(prepared, columns, vals):
    residual = prepared.p_beta[:]
    for source_col, val in vals.items():
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


def build_row_to_neg_cols(columns):
    out = {}
    for c, col in enumerate(columns):
        for row, coeff in col.terms:
            if coeff < 0:
                out.setdefault(row, []).append(c)
    return out


def solve_correction(columns, residual, active_rows, candidate_cols, residual_buffer):
    row_index = {r: i for i, r in enumerate(active_rows)}
    col_index = {c: j for j, c in enumerate(candidate_cols)}
    mat = lil_matrix((len(active_rows), len(candidate_cols)), dtype=float)
    scales = [max(1.0, abs(float(residual[r]))) for r in active_rows]
    for c, j in col_index.items():
        for row, coeff in columns[c].terms:
            i = row_index.get(row)
            if i is not None:
                mat[i, j] = float(coeff) / scales[i]
    b = np.array([(float(residual[r]) - residual_buffer) / scales[i] for i, r in enumerate(active_rows)], dtype=float)
    return linprog(np.ones(len(candidate_cols), dtype=float), A_ub=mat.tocsr(), b_ub=b, bounds=(0, None), method="highs")


def frac_from_float(x, den_token):
    f = Fraction(str(float(x)))
    if den_token == "decimal":
        return f
    return f.limit_denominator(int(den_token))


def apply_increment(residual, vals, columns, c, val):
    if not val:
        return
    vals[c] = vals.get(c, Fraction(0)) + val
    for row, coeff in columns[c].terms:
        residual[row] -= coeff * val


def write_source(path, vals):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for c in sorted(vals):
            val = vals[c]
            if val:
                f.write(json.dumps({"source_col": int(c), "num": val.numerator, "den": val.denominator}, sort_keys=True) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--source-out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--corr-den", default="1000000000000,decimal")
    ap.add_argument("--max-iters", type=int, default=20)
    ap.add_argument("--residual-buffer", type=float, default=0.0)
    args = ap.parse_args()

    vals = read_source_solution(args.solution)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    residual = compute_residual(prepared, columns, vals)
    row_to_neg_cols = build_row_to_neg_cols(columns)
    candidate_set = set()
    history = []
    den_tokens = [x.strip() for x in args.corr_den.split(",") if x.strip()]

    for it in range(args.max_iters):
        active = [i for i, x in enumerate(residual) if x < 0]
        entry = {"iter": it, "active_rows": len(active), "min_residual": str(min(residual) if residual else Fraction(0))}
        if not active:
            entry["status"] = "exact_clean"
            history.append(entry)
            break
        for row in active:
            candidate_set.update(row_to_neg_cols.get(row, []))
        candidates = sorted(candidate_set)
        entry["candidate_cols"] = len(candidates)
        if not candidates:
            entry["status"] = "no_candidates"
            history.append(entry)
            break
        res = solve_correction(columns, residual, active, candidates, args.residual_buffer)
        entry.update({"linprog_status": int(res.status), "linprog_success": bool(res.success), "objective": float(res.fun) if res.success else None})
        if not res.success:
            entry["linprog_message"] = res.message
            history.append(entry)
            break

        best = None
        for den in den_tokens:
            trial_residual = residual[:]
            trial_vals = dict(vals)
            used = []
            for c, x in zip(candidates, res.x):
                if x <= 1e-13:
                    continue
                val = frac_from_float(float(x), den)
                if val <= 0:
                    continue
                apply_increment(trial_residual, trial_vals, columns, c, val)
                used.append(c)
            payload = {
                "den": den,
                "used": used,
                "residual": trial_residual,
                "vals": trial_vals,
                "neg_rows": sum(1 for x in trial_residual if x < 0),
                "neg_vals": sum(1 for x in trial_vals.values() if x < 0),
                "min_residual": min(trial_residual) if trial_residual else Fraction(0),
            }
            key = (payload["neg_rows"], payload["neg_vals"], payload["min_residual"])
            if best is None or key < (best["neg_rows"], best["neg_vals"], best["min_residual"]):
                best = payload
        assert best is not None
        residual = best["residual"]
        vals = best["vals"]
        entry.update({"chosen_den": best["den"], "used_cols": len(best["used"]), "post_negative_rows": best["neg_rows"], "post_negative_vals": best["neg_vals"], "post_min_residual": str(best["min_residual"])})
        history.append(entry)
        if best["neg_rows"] == 0 and best["neg_vals"] == 0:
            break

    negative_rows = [(i, x) for i, x in enumerate(residual) if x < 0]
    negative_vals = [(c, x) for c, x in vals.items() if x < 0]
    exact_ok = not negative_rows and not negative_vals
    if exact_ok:
        write_source(args.source_out, vals)
    payload = {
        "schema": "source_negative_correction_probe_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "solution": str(args.solution),
        "residual_buffer": args.residual_buffer,
        "source_solution": str(args.source_out) if exact_ok else None,
        "history": history,
        "solution_negative_count": len(negative_vals),
        "full_negative_residual_count": len(negative_rows),
        "full_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "negative_rows_prefix": [{"row": int(r), "beta": list(prepared.betas[r]), "residual": replay.fmt_fraction(x)} for r, x in negative_rows[:20]],
        "exact_ok": exact_ok,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"exact_ok": exact_ok, "full_negative_residual_count": len(negative_rows), "solution_negative_count": len(negative_vals), "full_min_residual": payload["full_min_residual"], "summary": str(args.summary), "source_solution": payload["source_solution"]}, sort_keys=True))


if __name__ == "__main__":
    main()


