import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

from sympy import QQ
from sympy.polys.matrices import DomainMatrix

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


def coeff_map(columns, source_col):
    return dict(columns[source_col].terms)


def qq_to_fraction(x):
    return Fraction(int(x.numerator), int(x.denominator))


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

    if len(basic_cols) != len(upper_rows):
        raise RuntimeError(f"basis not square: {len(basic_cols)} cols vs {len(upper_rows)} rows")

    col_maps = {c: coeff_map(columns, c) for c in basic_cols}
    mat_rows = []
    rhs_rows = []
    for r in upper_rows:
        if r < row_count:
            mat_rows.append([QQ.convert(col_maps[c].get(r, Fraction(0))) for c in basic_cols])
            rhs_rows.append([QQ.convert(residual[r])])
        else:
            source_col = negative_source[r - row_count]
            mat_rows.append([QQ(-1) if c == source_col else QQ(0) for c in basic_cols])
            rhs_rows.append([QQ.convert(vals0[source_col])])

    a = DomainMatrix.from_list(mat_rows, QQ)
    b = DomainMatrix.from_list(rhs_rows, QQ)
    x = a.lu_solve(b)
    x_rows = x.to_list()
    sol_basis = [qq_to_fraction(x_rows[i][0]) for i in range(len(basic_cols))]
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
        "schema": "exact_from_highspy_basis_domainmatrix_v1",
        "basis": str(args.basis),
        "source_solution": str(args.source_out),
        "basic_cols_count": len(basic_cols),
        "upper_rows_count": len(upper_rows),
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
