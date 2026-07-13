import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_full_residual_check as fullcheck
import _codex_eq_odl1_rung2_scipy_core_probe as probe


CORE = Path("tmp/eq_odl1_rung2_dynamic_markowitz_k8_G3_near_lexlarge_v1.jsonl")
SOLUTION = Path("tmp/eq_odl1_rung2_dynamic_markowitz_k8_G3_near_lexlarge_192prime_solution_v1.jsonl")
OUT = Path("tmp/probe_k8_g3_repair_lp_scaled_tight_v1.json")


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
    A = lil_matrix((len(active_rows), len(candidate_cols)), dtype=float)
    scales = []
    for r in active_rows:
        rr = residual[r]
        scales.append(float(-rr) if rr < 0 else 1.0)
    for c, j in col_index.items():
        for row, coeff in columns[c].terms:
            i = row_index.get(row)
            if i is not None:
                A[i, j] = float(coeff) / scales[i]
    b = np.array([float(residual[r]) / scales[i] for i, r in enumerate(active_rows)], dtype=float)
    cvec = np.ones(len(candidate_cols), dtype=float)
    return linprog(cvec, A_ub=A.tocsr(), b_ub=b, bounds=(0, None), method="highs")


dim, source_cols, _selected_rows = fullcheck.read_core_maps(CORE)
sol = fullcheck.read_solution(SOLUTION, dim)
prepared, columns, _mat, _b_ub = probe.build_lp(8, 10, "near_2s_minus_1", "negative")
residual = compute_residual(prepared, columns, source_cols, sol)
row_to_neg_cols = build_row_to_neg_cols(columns)

active = sorted(i for i, x in enumerate(residual) if x < 0)
history = []
candidate_set = set()

best = None
for it in range(20):
    for row in active:
        candidate_set.update(row_to_neg_cols.get(row, []))
    candidates = sorted(candidate_set)
    if not candidates:
        history.append({"iter": it, "status": "no_candidates", "active_rows": len(active)})
        break
    res = solve_active(columns, residual, active, candidates)
    entry = {
        "iter": it,
        "active_rows": len(active),
        "candidate_cols": len(candidates),
        "linprog_status": int(res.status),
        "linprog_message": res.message,
        "linprog_success": bool(res.success),
        "objective": float(res.fun) if res.success else None,
    }
    if not res.success:
        history.append(entry)
        break
    x = res.x
    # Check all rows in sparse update form.
    delta = [0.0] * len(residual)
    used = []
    for val, c in zip(x, candidates):
        if val <= 1e-11:
            continue
        used.append((c, float(val)))
        for row, coeff in columns[c].terms:
            delta[row] += float(coeff) * float(val)
    new_float = [float(r) - d for r, d in zip(residual, delta)]
    violated = [i for i, v in enumerate(new_float) if v < -1e-12]
    entry.update({
        "used_cols": len(used),
        "min_residual_float": min(new_float),
        "violated_count": len(violated),
        "violated_prefix": violated[:30],
        "used_prefix": [
            {
                "source_col": c,
                "t": v,
                "kind": getattr(columns[c], "kind", None),
                "name": getattr(columns[c], "name", None),
                "multiplier_exp": list(getattr(columns[c], "multiplier_exp", ())) if getattr(columns[c], "multiplier_exp", None) is not None else None,
            }
            for c, v in used[:30]
        ],
    })
    history.append(entry)
    best = {"candidates": candidates, "x": x, "used": used, "violated": violated, "new_float": new_float}
    if not violated:
        break
    old = set(active)
    old.update(violated)
    active = sorted(old)

result = {
    "schema": "probe_k8_g3_repair_lp_tight_v1",
    "violation_threshold": -1e-12,
    "initial_negative_rows": sorted(i for i, x in enumerate(residual) if x < 0),
    "history": history,
}
if best is not None:
    result["final_used_count"] = len(best["used"])
    result["final_violated_count"] = len(best["violated"])
    result["final_min_residual_float"] = min(best["new_float"])
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))


