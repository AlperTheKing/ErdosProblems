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
from probe_rung2_multirepair_lp_lb import collapsed_source_values


def float_to_fraction(x: float, max_den: int | None) -> Fraction:
    f = Fraction(str(float(x)))
    return f if max_den is None else f.limit_denominator(max_den)


def build_row_to_neg_cols(columns):
    out = {}
    for j, col in enumerate(columns):
        for row, coeff in col.terms:
            if coeff < 0:
                out.setdefault(row, []).append(j)
    return out


def solve_correction(columns, residual, active_rows, candidate_cols):
    row_index = {r: i for i, r in enumerate(active_rows)}
    col_index = {c: j for j, c in enumerate(candidate_cols)}
    mat = lil_matrix((len(active_rows), len(candidate_cols)), dtype=float)
    scales = []
    for r in active_rows:
        scales.append(max(1.0, abs(float(residual[r]))))
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


def apply_increment(residual, vals, columns, c, val):
    if not val:
        return
    vals[c] = vals.get(c, Fraction(0)) + val
    for row, coeff in columns[c].terms:
        residual[row] -= coeff * val


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--repair-report", type=Path, required=True)
    ap.add_argument("--base-den", default="10000000")
    ap.add_argument("--corr-den", default="10000000000,100000000000,decimal")
    ap.add_argument("--max-iters", type=int, default=30)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--source-out", type=Path)
    args = ap.parse_args()

    base_den = None if args.base_den == "decimal" else int(args.base_den)
    corr_denoms = [None if tok.strip() == "decimal" else int(tok) for tok in args.corr_den.split(",") if tok.strip()]

    dim, source_cols, _selected_rows = fullcheck.read_core_maps(args.core)
    sol = fullcheck.read_solution(args.solution, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    report = json.loads(args.repair_report.read_text(encoding="utf-8"))
    neg_source = report.get("negative_source_columns", {})
    lower_bounds = {int(k): -Fraction(v) for k, v in neg_source.items()}

    residual = base.compute_residual(prepared, columns, source_cols, sol)
    vals = collapsed_source_values(source_cols, sol)
    increments: dict[int, Fraction] = {}
    for item in report["history"][-1]["used"]:
        c = int(item["source_col"])
        val = float_to_fraction(float(item["t"]), base_den)
        lb = lower_bounds.get(c, Fraction(0))
        if val < lb:
            val = lb
        increments[c] = increments.get(c, Fraction(0)) + val
        apply_increment(residual, vals, columns, c, val)

    row_to_neg_cols = build_row_to_neg_cols(columns)
    candidate_set = set()
    history = []

    for it in range(args.max_iters):
        active = [i for i, x in enumerate(residual) if x < 0]
        entry = {
            "iter": it,
            "active_rows": len(active),
            "min_residual": str(min(residual) if residual else Fraction(0)),
        }
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
        res = solve_correction(columns, residual, active, candidates)
        entry.update({
            "linprog_status": int(res.status),
            "linprog_message": res.message,
            "linprog_success": bool(res.success),
            "objective": float(res.fun) if res.success else None,
        })
        if not res.success:
            history.append(entry)
            break

        best_payload = None
        for den in corr_denoms:
            trial_residual = residual[:]
            trial_vals = dict(vals)
            trial_inc = {}
            used = []
            for c, x in zip(candidates, res.x):
                if x <= 1e-13:
                    continue
                val = float_to_fraction(float(x), den)
                if not val:
                    continue
                trial_inc[c] = trial_inc.get(c, Fraction(0)) + val
                apply_increment(trial_residual, trial_vals, columns, c, val)
                used.append(c)
            neg_rows = sum(1 for x in trial_residual if x < 0)
            neg_vals = sum(1 for x in trial_vals.values() if x < 0)
            payload = {
                "den": "decimal" if den is None else den,
                "used": used,
                "increments": trial_inc,
                "residual": trial_residual,
                "vals": trial_vals,
                "negative_rows": neg_rows,
                "negative_vals": neg_vals,
                "min_residual": min(trial_residual) if trial_residual else Fraction(0),
            }
            if best_payload is None or (
                payload["negative_rows"],
                payload["negative_vals"],
                payload["min_residual"],
            ) < (
                best_payload["negative_rows"],
                best_payload["negative_vals"],
                best_payload["min_residual"],
            ):
                best_payload = payload
        assert best_payload is not None
        for c, val in best_payload["increments"].items():
            increments[c] = increments.get(c, Fraction(0)) + val
        residual = best_payload["residual"]
        vals = best_payload["vals"]
        entry.update({
            "chosen_den": best_payload["den"],
            "used_cols": len(best_payload["used"]),
            "post_negative_rows": best_payload["negative_rows"],
            "post_negative_vals": best_payload["negative_vals"],
            "post_min_residual": str(best_payload["min_residual"]),
        })
        history.append(entry)
        if best_payload["negative_rows"] == 0 and best_payload["negative_vals"] == 0:
            break

    negative_rows = [(i, x) for i, x in enumerate(residual) if x < 0]
    negative_vals = [(c, x) for c, x in vals.items() if x < 0]
    payload = {
        "schema": "exact_negative_correction_probe_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "core": str(args.core),
        "solution": str(args.solution),
        "repair_report": str(args.repair_report),
        "base_den": args.base_den,
        "history": history,
        "used_count": sum(1 for v in increments.values() if v),
        "solution_negative_count": len(negative_vals),
        "full_negative_residual_count": len(negative_rows),
        "full_min_residual": str(min(residual) if residual else Fraction(0)),
        "negative_rows_prefix": [
            {"row": int(row), "beta": list(prepared.betas[row]), "residual": str(val)}
            for row, val in negative_rows[:20]
        ],
        "exact_ok": not negative_rows and not negative_vals,
    }
    if args.source_out and payload["exact_ok"]:
        args.source_out.parent.mkdir(parents=True, exist_ok=True)
        with args.source_out.open("w", encoding="utf-8") as f:
            for c in sorted(vals):
                val = vals[c]
                if val:
                    f.write(json.dumps({"source_col": c, "num": val.numerator, "den": val.denominator}, sort_keys=True) + "\n")
        payload["source_solution"] = str(args.source_out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "exact_ok": payload["exact_ok"],
        "used_count": payload["used_count"],
        "solution_negative_count": payload["solution_negative_count"],
        "full_negative_residual_count": payload["full_negative_residual_count"],
        "full_min_residual": payload["full_min_residual"],
        "summary": str(args.out),
        "source_solution": payload.get("source_solution"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
