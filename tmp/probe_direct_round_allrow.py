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


def collapsed_source_values(source_cols, sol):
    vals = {}
    for val, source_col in zip(sol, source_cols):
        vals[source_col] = vals.get(source_col, Fraction(0)) + val
    return vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--oracle", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    dim, source_cols, _selected_rows = fullcheck.read_core_maps(args.core)
    sol = fullcheck.read_solution(args.solution, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    residual0 = base.compute_residual(prepared, columns, source_cols, sol)
    vals0 = collapsed_source_values(source_cols, sol)
    oracle = json.loads(args.oracle.read_text(encoding="utf-8"))
    used = [(int(item["source_col"]), float(item["t"])) for item in oracle["used_prefix"]]

    dens = [10**k for k in range(4, 13)] + [2**k for k in range(16, 45, 4)]
    results = []
    best = None
    for den in dens:
        inc = {c: Fraction(str(t)).limit_denominator(den) for c, t in used}
        residual = residual0[:]
        for c, val in inc.items():
            if val:
                for row, coeff in columns[c].terms:
                    residual[row] -= coeff * val
        vals = dict(vals0)
        for c, val in inc.items():
            vals[c] = vals.get(c, Fraction(0)) + val
        neg_rows = [(i, x) for i, x in enumerate(residual) if x < 0]
        neg_vals = [(c, x) for c, x in vals.items() if x < 0]
        rec = {
            "den": den,
            "residual_neg": len(neg_rows),
            "source_neg": len(neg_vals),
            "min_residual": str(min(residual) if residual else Fraction(0)),
            "min_source": str(min(vals.values()) if vals else Fraction(0)),
            "neg_rows_prefix": [i for i, _ in neg_rows[:20]],
            "neg_source_prefix": [c for c, _ in neg_vals[:20]],
        }
        results.append(rec)
        key = (len(neg_rows) + len(neg_vals), len(neg_rows), len(neg_vals), float(min(residual)))
        if best is None or key < best[0]:
            best = (key, rec)
        if not neg_rows and not neg_vals:
            break
    out = {"schema": "direct_round_allrow_v1", "oracle": str(args.oracle), "used_count": len(used), "results": results, "best": best[1] if best else None}
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"out": str(args.out), "used_count": len(used), "best": out["best"]}, sort_keys=True))


if __name__ == "__main__":
    main()
