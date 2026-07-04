import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_full_residual_check as fullcheck
import _codex_eq_odl1_rung2_scipy_core_probe as probe


CORE = Path("tmp/eq_odl1_rung2_dynamic_markowitz_k8_G3_near_lexlarge_v1.jsonl")
SOLUTION = Path("tmp/eq_odl1_rung2_dynamic_markowitz_k8_G3_near_lexlarge_192prime_solution_v1.jsonl")
SUMMARY = Path("tmp/eq_odl1_rung2_full_residual_check_dynamic_markowitz_k8_G3_near_lexlarge_192prime_v1.json")


def coeff_at(col, row):
    for i, c in col.terms:
        if i == row:
            return c
    return Fraction(0)


def compute_residual(prepared, columns, source_cols, sol):
    residual = prepared.p_beta[:]
    for val, source_col in zip(sol, source_cols):
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


dim, source_cols, _selected_rows = fullcheck.read_core_maps(CORE)
sol = fullcheck.read_solution(SOLUTION, dim)
prepared, columns, _mat, _b_ub = probe.build_lp(8, 10, "near_2s_minus_1", "negative")
residual = compute_residual(prepared, columns, source_cols, sol)
neg_rows = [x["row"] for x in json.loads(SUMMARY.read_text())["negative_rows_prefix"]]

items = []
for source_col, col in enumerate(columns):
    vec = [coeff_at(col, r) for r in neg_rows]
    if not any(c < 0 for c in vec):
        continue
    pos_bounds = []
    for row, coeff in col.terms:
        if coeff > 0:
            pos_bounds.append((residual[row] / coeff, row, coeff))
    min_bound = min(pos_bounds, default=(None, None, None), key=lambda x: x[0])
    items.append({
        "source_col": source_col,
        "already_in_core": source_col in set(source_cols),
        "kind": getattr(col, "kind", None),
        "name": getattr(col, "name", None),
        "multiplier_exp": list(getattr(col, "multiplier_exp", ())) if getattr(col, "multiplier_exp", None) is not None else None,
        "terms": len(col.terms),
        "bad_coeffs": [str(c) for c in vec],
        "helps": [neg_rows[i] for i, c in enumerate(vec) if c < 0],
        "min_pos_bound": str(min_bound[0]) if min_bound[0] is not None else None,
        "limiting_row": min_bound[1],
        "limiting_coeff": str(min_bound[2]) if min_bound[2] is not None else None,
    })

out = {
    "neg_rows": neg_rows,
    "neg_residuals": [str(residual[r]) for r in neg_rows],
    "candidate_count": len(items),
    "items": items,
}
Path("tmp/probe_k8_g3_multirepair_candidates_v1.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps({
    "neg_rows": neg_rows,
    "candidate_count": len(items),
    "items_prefix": items[:20],
}, indent=2))
