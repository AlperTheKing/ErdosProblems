import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as source_check


def fmt_fraction(x: Fraction) -> str:
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


def compute_residual(prepared, columns, vals):
    residual = prepared.p_beta[:]
    for source_col, val in vals.items():
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


def coeff_map(columns, source_col):
    return dict(columns[source_col].terms)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--source-solution", type=Path, required=True)
    ap.add_argument("--basis", type=Path, required=True)
    ap.add_argument("--out-core", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    vals = source_check.read_source_solution(args.source_solution)
    residual = compute_residual(prepared, columns, vals)

    basis = json.loads(args.basis.read_text(encoding="utf-8"))
    basic_cols = [int(x) for x in basis["basic_cols"]]
    upper_rows = [int(x) for x in basis["upper_rows"]]
    row_count = int(basis["row_count"])
    margin = Fraction(str(basis.get("margin", 0.0)))
    active_margin = Fraction(str(basis.get("active_margin", 0.0)))
    active_rows = {int(x) for x in basis.get("initial_negative_rows", [])}

    if len(basic_cols) != len(upper_rows):
        raise RuntimeError(f"basis not square: {len(basic_cols)} cols vs {len(upper_rows)} rows")
    if any(r < 0 or r >= row_count for r in upper_rows):
        raise RuntimeError("source-patch basis contains non-residual rows")

    col_maps = {c: coeff_map(columns, c) for c in basic_cols}
    rhs = []
    terms = []
    for local_row, r in enumerate(upper_rows):
        rhs.append(residual[r] - margin - (active_margin if r in active_rows else Fraction(0)))
        for local_col, c in enumerate(basic_cols):
            coeff = col_maps[c].get(r, Fraction(0))
            if coeff:
                terms.append((local_row, local_col, coeff))

    args.out_core.parent.mkdir(parents=True, exist_ok=True)
    with args.out_core.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "meta", "dimension": len(basic_cols), "terms": len(terms)}) + "\n")
        for local_col, source_col in enumerate(basic_cols):
            f.write(json.dumps({"type": "col", "col": local_col, "source_col": source_col}) + "\n")
        for row, value in enumerate(rhs):
            f.write(json.dumps({"type": "rhs", "row": row, "value": fmt_fraction(value)}) + "\n")
        for row, col, value in terms:
            f.write(json.dumps({"type": "term", "row": row, "col": col, "value": fmt_fraction(value)}) + "\n")

    payload = {
        "schema": "source_patch_basis_core_v1",
        "basis": str(args.basis),
        "source_solution": str(args.source_solution),
        "out_core": str(args.out_core),
        "dimension": len(basic_cols),
        "terms": len(terms),
        "upper_rows_count": len(upper_rows),
        "row_count": row_count,
        "margin": str(margin),
        "active_margin": str(active_margin),
        "active_rows": sorted(active_rows),
    }
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
