import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_modular_replay as replay
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as source_check


def read_increment_solution(path: Path):
    vals = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            vals[int(rec["col"])] = Fraction(int(rec["num"]), int(rec["den"]))
    return vals


def read_core_cols(path: Path):
    out = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("type") == "col":
                out[int(rec["col"])] = int(rec["source_col"])
    return out


def compute_residual(prepared, columns, vals):
    residual = prepared.p_beta[:]
    for source_col, val in vals.items():
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--source-solution", type=Path, required=True)
    ap.add_argument("--basis-core", type=Path, required=True)
    ap.add_argument("--increment-solution", type=Path, required=True)
    ap.add_argument("--source-out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    vals = source_check.read_source_solution(args.source_solution)
    local_to_source = read_core_cols(args.basis_core)
    inc_local = read_increment_solution(args.increment_solution)
    increments = {local_to_source[j]: val for j, val in inc_local.items() if val}

    for c, val in increments.items():
        vals[c] = vals.get(c, Fraction(0)) + val

    residual = compute_residual(prepared, columns, vals)

    args.source_out.parent.mkdir(parents=True, exist_ok=True)
    with args.source_out.open("w", encoding="utf-8") as f:
        for c in sorted(vals):
            val = vals[c]
            if val:
                f.write(json.dumps({"source_col": c, "num": val.numerator, "den": val.denominator}, sort_keys=True) + "\n")

    neg_rows = [(i, x) for i, x in enumerate(residual) if x < 0]
    neg_vals = [(c, x) for c, x in vals.items() if x < 0]
    payload = {
        "schema": "apply_source_patch_basis_solution_v1",
        "basis_core": str(args.basis_core),
        "increment_solution": str(args.increment_solution),
        "source_solution": str(args.source_out),
        "increment_count": sum(1 for x in increments.values() if x),
        "increment_negative_count": sum(1 for x in increments.values() if x < 0),
        "solution_negative_count": len(neg_vals),
        "full_negative_residual_count": len(neg_rows),
        "full_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "full_max_residual": replay.fmt_fraction(max(residual) if residual else Fraction(0)),
        "min_solution_value": replay.fmt_fraction(min(vals.values()) if vals else Fraction(0)),
        "negative_rows_prefix": [
            {"row": i, "residual": replay.fmt_fraction(x)}
            for i, x in neg_rows[:20]
        ],
        "negative_source_prefix": [
            {"source_col": c, "value": replay.fmt_fraction(x)}
            for c, x in neg_vals[:20]
        ],
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
