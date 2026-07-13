import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")
sys.path.append("tmp")
import _codex_eq_odl1_rung2_full_residual_check as fullcheck
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import probe_rung2_multirepair_lp as base
from exact_rationalize_multirepair import solve_square


def collapsed_source_values(source_cols, sol):
    vals = {}
    for val, source_col in zip(sol, source_cols):
        vals[source_col] = vals.get(source_col, Fraction(0)) + val
    return vals


def coeff_at(columns, source_col, row):
    for rr, coeff in columns[source_col].terms:
        if rr == row:
            return coeff
    return Fraction(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--basis", type=Path, required=True)
    ap.add_argument("--source-out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    dim, source_cols, _selected_rows = fullcheck.read_core_maps(args.core)
    sol = fullcheck.read_solution(args.solution, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    residual = base.compute_residual(prepared, columns, source_cols, sol)
    vals0 = collapsed_source_values(source_cols, sol)
    basis = json.loads(args.basis.read_text(encoding="utf-8"))
    basic_cols = [int(x) for x in basis["basic_cols"]]
    upper_rows = [int(x) for x in basis["upper_rows"]]
    negative_source = [int(x) for x in basis["negative_source"]]
    row_count = int(basis["row_count"])
    margin = Fraction(str(basis.get("margin", 0.0)))
    margin_rows = {int(x) for x in basis.get("margin_rows", [])}
    source_margin = Fraction(str(basis.get("source_margin", margin)))

    if len(basic_cols) != len(upper_rows):
        raise RuntimeError(f"basis not square: {len(basic_cols)} cols vs {len(upper_rows)} rows")

    rows = []
    rhs = []
    for r in upper_rows:
        if r < row_count:
            rows.append([coeff_at(columns, c, r) for c in basic_cols])
            row_margin = margin if not margin_rows or r in margin_rows else Fraction(0)
            rhs.append(residual[r] - row_margin)
        else:
            source_col = negative_source[r - row_count]
            rows.append([Fraction(-1) if c == source_col else Fraction(0) for c in basic_cols])
            rhs.append(vals0[source_col] - source_margin)

    sol_basis = solve_square(rows, rhs)
    increments = dict(zip(basic_cols, sol_basis))

    repaired = residual[:]
    for c, val in increments.items():
        if val:
            for row, coeff in columns[c].terms:
                repaired[row] -= coeff * val

    vals = dict(vals0)
    for c, val in increments.items():
        vals[c] = vals.get(c, Fraction(0)) + val

    args.source_out.parent.mkdir(parents=True, exist_ok=True)
    with args.source_out.open("w", encoding="utf-8") as f:
        for c in sorted(vals):
            val = vals[c]
            if val:
                f.write(json.dumps({"source_col": c, "num": val.numerator, "den": val.denominator}, sort_keys=True) + "\n")

    neg_rows = [(i, x) for i, x in enumerate(repaired) if x < 0]
    neg_vals = [(c, x) for c, x in vals.items() if x < 0]
    payload = {
        "schema": "exact_from_highspy_basis_v1",
        "basis": str(args.basis),
        "source_solution": str(args.source_out),
        "basic_cols_count": len(basic_cols),
        "upper_rows_count": len(upper_rows),
        "margin": str(margin),
        "margin_rows": sorted(margin_rows),
        "source_margin": str(source_margin),
        "increment_negative_count": sum(1 for x in increments.values() if x < 0),
        "solution_negative_count": len(neg_vals),
        "full_negative_residual_count": len(neg_rows),
        "full_min_residual": str(min(repaired) if repaired else Fraction(0)),
        "min_solution_value": str(min(vals.values()) if vals else Fraction(0)),
        "negative_rows_prefix": [{"row": i, "residual": str(x)} for i, x in neg_rows[:20]],
        "negative_source_prefix": [{"source_col": c, "value": str(x)} for c, x in neg_vals[:20]],
    }
    payload["exact_ok"] = payload["increment_negative_count"] == 0 and payload["solution_negative_count"] == 0 and payload["full_negative_residual_count"] == 0
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "exact_ok": payload["exact_ok"],
        "increment_negative_count": payload["increment_negative_count"],
        "solution_negative_count": payload["solution_negative_count"],
        "full_negative_residual_count": payload["full_negative_residual_count"],
        "full_min_residual": payload["full_min_residual"],
        "summary": str(args.summary),
        "source_solution": str(args.source_out),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
