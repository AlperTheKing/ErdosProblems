import argparse
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


def apply_increments(residual, vals, columns, increments):
    out_res = residual[:]
    out_vals = dict(vals)
    for c, val in increments.items():
        if not val:
            continue
        out_vals[c] = out_vals.get(c, Fraction(0)) + val
        for row, coeff in columns[c].terms:
            out_res[row] -= coeff * val
    return out_res, out_vals


def clean(residual, vals):
    return all(x >= 0 for x in residual) and all(x >= 0 for x in vals.values())


def gain(col, row):
    return -dict(col.terms).get(row, Fraction(0))


def safe_candidates(columns, neg_rows, zero_rows):
    out = []
    for c, col in enumerate(columns):
        gains = [gain(col, r) for r in neg_rows]
        if not any(g > 0 for g in gains):
            continue
        if any(coeff > 0 and row in zero_rows for row, coeff in col.terms):
            continue
        out.append(c)
    return out


def pair_points(c1, c2, rows, deficits, columns):
    g00, g10 = gain(columns[c1], rows[0]), gain(columns[c1], rows[1])
    g01, g11 = gain(columns[c2], rows[0]), gain(columns[c2], rows[1])
    points = []

    def add(x, y, why):
        if x >= 0 and y >= 0:
            points.append((x, y, why))

    for c, g0, g1, idx in [(c1, g00, g10, 0), (c2, g01, g11, 1)]:
        if g0 > 0 and g1 > 0:
            need = max(deficits[0] / g0, deficits[1] / g1)
            add(need if idx == 0 else Fraction(0), need if idx == 1 else Fraction(0), "single_covers_both")
    det = g00 * g11 - g01 * g10
    if det:
        add((deficits[0] * g11 - deficits[1] * g01) / det,
            (g00 * deficits[1] - g10 * deficits[0]) / det,
            "two_active_equalities")
    if g00 > 0 and g11 > 0:
        add(deficits[0] / g00, deficits[1] / g11, "diagonal_01")
    if g10 > 0 and g01 > 0:
        add(deficits[1] / g10, deficits[0] / g01, "diagonal_10")
    return points


def find_repair(residual, vals, columns, neg_rows):
    zero_rows = {i for i, r in enumerate(residual) if r == 0}
    deficits = [-residual[r] for r in neg_rows]
    candidates = safe_candidates(columns, neg_rows, zero_rows)
    best = None

    def consider(increments, why):
        nonlocal best
        trial_res, trial_vals = apply_increments(residual, vals, columns, increments)
        if not clean(trial_res, trial_vals):
            return
        score = (
            len(increments),
            sum(v.numerator.bit_length() + v.denominator.bit_length() for v in increments.values()),
            sorted(increments),
        )
        payload = (score, increments, trial_res, trial_vals, why)
        if best is None or score < best[0]:
            best = payload

    if len(neg_rows) == 1:
        row = neg_rows[0]
        for c in candidates:
            g = gain(columns[c], row)
            if g <= 0:
                continue
            consider({c: deficits[0] / g}, "single_active_row")
    elif len(neg_rows) == 2:
        for i, c1 in enumerate(candidates):
            for c2 in candidates[i:]:
                for x, y, why in pair_points(c1, c2, neg_rows, deficits, columns):
                    inc = {}
                    if x:
                        inc[c1] = inc.get(c1, Fraction(0)) + x
                    if y:
                        inc[c2] = inc.get(c2, Fraction(0)) + y
                    consider(inc, why)
    return candidates, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--source-solution", type=Path, required=True)
    ap.add_argument("--source-out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    prepared, columns, _mat, _b = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    vals = source_check.read_source_solution(args.source_solution)
    residual = compute_residual(prepared, columns, vals)
    neg_rows = [i for i, r in enumerate(residual) if r < 0]
    candidates, best = find_repair(residual, vals, columns, neg_rows)

    out = {
        "schema": "exact_small_residual_repair_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "source_solution_in": str(args.source_solution),
        "neg_rows": neg_rows,
        "candidate_count": len(candidates),
        "found": best is not None,
    }
    if best is not None:
        _score, increments, trial_res, trial_vals, why = best
        args.source_out.parent.mkdir(parents=True, exist_ok=True)
        with args.source_out.open("w", encoding="utf-8") as f:
            for c in sorted(trial_vals):
                val = trial_vals[c]
                if val:
                    f.write(json.dumps({"source_col": c, "num": val.numerator, "den": val.denominator}, sort_keys=True) + "\n")
        out.update({
            "why": why,
            "increments": {str(c): str(v) for c, v in increments.items()},
            "increment_count": len(increments),
            "source_solution": str(args.source_out),
            "full_min_residual": str(min(trial_res)),
            "full_negative_residual_count": sum(1 for x in trial_res if x < 0),
            "solution_negative_count": sum(1 for x in trial_vals.values() if x < 0),
        })
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: out.get(k) for k in ["found", "increment_count", "full_negative_residual_count", "solution_negative_count", "source_solution"]}, sort_keys=True))


if __name__ == "__main__":
    main()
