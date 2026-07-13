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


def fmt_fraction(x: Fraction) -> str:
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


def collapsed_source_values(source_cols, sol):
    vals = {}
    for val, source_col in zip(sol, source_cols):
        vals[source_col] = vals.get(source_col, Fraction(0)) + val
    return vals


def coeff_map(columns, source_col):
    return dict(columns[source_col].terms)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--basis", type=Path, required=True)
    ap.add_argument("--out-core", type=Path, required=True)
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

    col_maps = {c: coeff_map(columns, c) for c in basic_cols}
    terms = []
    rhs = []
    for local_row, r in enumerate(upper_rows):
        if r < row_count:
            row_margin = margin if not margin_rows or r in margin_rows else Fraction(0)
            rhs.append(residual[r] - row_margin)
            for local_col, c in enumerate(basic_cols):
                coeff = col_maps[c].get(r, Fraction(0))
                if coeff:
                    terms.append((local_row, local_col, coeff))
        else:
            source_col = negative_source[r - row_count]
            rhs.append(vals0[source_col] - source_margin)
            for local_col, c in enumerate(basic_cols):
                if c == source_col:
                    terms.append((local_row, local_col, Fraction(-1)))

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
        "schema": "highspy_basis_increment_core_v1",
        "basis": str(args.basis),
        "core": str(args.core),
        "solution": str(args.solution),
        "out_core": str(args.out_core),
        "dimension": len(basic_cols),
        "terms": len(terms),
        "upper_rows_count": len(upper_rows),
        "negative_source_count": len(negative_source),
        "row_count": row_count,
        "margin": str(margin),
        "margin_rows": sorted(margin_rows),
        "source_margin": str(source_margin),
    }
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
