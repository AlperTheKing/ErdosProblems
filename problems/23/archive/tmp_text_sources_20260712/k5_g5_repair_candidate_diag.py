import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")
sys.path.append("tmp")

import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as source_check


def compute_residual(prepared, columns, vals):
    residual = prepared.p_beta[:]
    for source_col, val in vals.items():
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


def main():
    solution = Path("tmp/eq_odl1_rung2_source_solution_k5_G5_near_lexlarge_192prime_highspy_basis_exact_v1.jsonl")
    prepared, columns, _mat, _b = probe.build_lp(5, 12, "near_2s_minus_1", "negative")
    vals = source_check.read_source_solution(solution)
    residual = compute_residual(prepared, columns, vals)
    neg_rows = [i for i, r in enumerate(residual) if r < 0]
    zero_rows = {i for i, r in enumerate(residual) if r == 0}
    pos_rows = {i: r for i, r in enumerate(residual) if r > 0}
    candidates = []
    for c, col in enumerate(columns):
        terms = dict(col.terms)
        if not any(terms.get(r, Fraction(0)) < 0 for r in neg_rows):
            continue
        bad_zero = [r for r, coeff in col.terms if coeff > 0 and r in zero_rows]
        if bad_zero:
            continue
        max_step = None
        for r, coeff in col.terms:
            if coeff > 0 and r in pos_rows:
                bound = pos_rows[r] / coeff
                max_step = bound if max_step is None or bound < max_step else max_step
        repair = []
        for r in neg_rows:
            coeff = terms.get(r, Fraction(0))
            if coeff < 0:
                repair.append((-residual[r]) / (-coeff))
            else:
                repair.append(None)
        feasible_single = False
        needed = max((x for x in repair if x is not None), default=None)
        if needed is not None and (max_step is None or needed <= max_step):
            feasible_single = True
        candidates.append({
            "source_col": c,
            "neg_coeffs": {str(r): str(terms.get(r, Fraction(0))) for r in neg_rows},
            "repair_steps": [str(x) if x is not None else None for x in repair],
            "max_step": str(max_step) if max_step is not None else None,
            "feasible_single": feasible_single,
            "term_count": len(col.terms),
        })
    candidates.sort(key=lambda x: (not x["feasible_single"], x["term_count"], x["source_col"]))
    out = {
        "neg_rows": neg_rows,
        "neg_residuals": {str(r): str(residual[r]) for r in neg_rows},
        "zero_rows": len(zero_rows),
        "positive_rows": len(pos_rows),
        "candidate_count": len(candidates),
        "feasible_single_count": sum(1 for x in candidates if x["feasible_single"]),
        "candidates_prefix": candidates[:30],
    }
    path = Path("tmp/k5_g5_repair_candidate_diag_v1.json")
    path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "candidate_count": out["candidate_count"],
        "feasible_single_count": out["feasible_single_count"],
        "neg_rows": neg_rows,
        "out": str(path),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
