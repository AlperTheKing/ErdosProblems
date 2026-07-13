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
from exact_rationalize_multirepair import add_independent, coeff_at, solve_square
from probe_rung2_multirepair_lp_lb import collapsed_source_values


def parse_forced(value) -> Fraction:
    if value is None:
        return Fraction(0)
    return Fraction(str(value))


def parse_used(report):
    used = []
    for item in report["history"][-1]["used"]:
        c = int(item["source_col"])
        forced = parse_forced(item.get("forced_lb", "0"))
        used.append((c, forced))
    return used


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--repair-report", type=Path, required=True)
    ap.add_argument("--candidate-tol", type=float, default=1e-9)
    ap.add_argument("--fallback-all-touched", action="store_true")
    ap.add_argument("--source-out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    dim, source_cols, _selected_rows = fullcheck.read_core_maps(args.core)
    sol = fullcheck.read_solution(args.solution, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    residual = base.compute_residual(prepared, columns, source_cols, sol)
    report = json.loads(args.repair_report.read_text(encoding="utf-8"))
    used = parse_used(report)

    fixed = {c: lb for c, lb in used if lb > 0}
    free_cols = [c for c, lb in used if lb == 0]

    fixed_residual = residual[:]
    for c, val in fixed.items():
        for row, coeff in columns[c].terms:
            fixed_residual[row] -= coeff * val

    delta_float = [0.0] * len(residual)
    touched = set()
    for item in report["history"][-1]["used"]:
        c = int(item["source_col"])
        t = float(item["t"])
        for row, coeff in columns[c].terms:
            touched.add(row)
            delta_float[row] += float(coeff) * t
    new_float = [float(r) - d for r, d in zip(residual, delta_float)]

    active = set(report["initial_negative_rows"])
    for hist in report["history"]:
        active.update(hist.get("violated_prefix", []))
    near = {i for i, v in enumerate(new_float) if abs(v) <= args.candidate_tol}
    candidate_rows = sorted(
        (active | (near & touched)),
        key=lambda r: (abs(new_float[r]), 0 if r in active else 1, r),
    )
    if args.fallback_all_touched:
        seen_rows = set(candidate_rows)
        candidate_rows.extend(
            r
            for r in sorted(touched, key=lambda x: (abs(new_float[x]), 0 if x in active else 1, x))
            if r not in seen_rows
        )

    echelon = []
    selected = []
    selected_vecs = []
    selected_rhs = []
    for row in candidate_rows:
        vec = [coeff_at(columns, c, row) for c in free_cols]
        if not any(vec):
            continue
        if add_independent(echelon, vec):
            selected.append(row)
            selected_vecs.append(vec)
            selected_rhs.append(fixed_residual[row])
            if len(selected) == len(free_cols):
                break
    if len(selected) != len(free_cols):
        raise RuntimeError(f"selected only {len(selected)} independent rows for {len(free_cols)} free columns")

    free_vals = solve_square(selected_vecs, selected_rhs)
    increments = dict(fixed)
    increments.update(dict(zip(free_cols, free_vals)))

    repaired_residual = residual[:]
    for c, val in increments.items():
        if not val:
            continue
        for row, coeff in columns[c].terms:
            repaired_residual[row] -= coeff * val

    vals = collapsed_source_values(source_cols, sol)
    for c, val in increments.items():
        vals[c] = vals.get(c, Fraction(0)) + val

    args.source_out.parent.mkdir(parents=True, exist_ok=True)
    with args.source_out.open("w", encoding="utf-8") as f:
        for c in sorted(vals):
            val = vals[c]
            if val:
                f.write(json.dumps({"source_col": c, "num": val.numerator, "den": val.denominator}, sort_keys=True) + "\n")

    negative_rows = [(i, x) for i, x in enumerate(repaired_residual) if x < 0]
    negative_vals = [(c, x) for c, x in vals.items() if x < 0]
    negative_inc = [(c, x) for c, x in increments.items() if x < 0]
    payload = {
        "schema": "exact_rationalize_multirepair_lbfix_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "core": str(args.core),
        "core_solution": str(args.solution),
        "repair_report": str(args.repair_report),
        "source_solution": str(args.source_out),
        "fixed_count": len(fixed),
        "free_count": len(free_cols),
        "selected_rows": selected,
        "increment_negative_count": len(negative_inc),
        "solution_negative_count": len(negative_vals),
        "full_negative_residual_count": len(negative_rows),
        "full_min_residual": str(min(repaired_residual) if repaired_residual else Fraction(0)),
        "negative_rows_prefix": [
            {"row": int(row), "beta": list(prepared.betas[row]), "residual": str(val)}
            for row, val in negative_rows[:20]
        ],
        "negative_solution_prefix": [
            {"source_col": int(c), "value": str(val)}
            for c, val in negative_vals[:20]
        ],
        "exact_ok": not negative_rows and not negative_vals and not negative_inc,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "exact_ok": payload["exact_ok"],
        "fixed_count": payload["fixed_count"],
        "free_count": payload["free_count"],
        "increment_negative_count": payload["increment_negative_count"],
        "solution_negative_count": payload["solution_negative_count"],
        "full_negative_residual_count": payload["full_negative_residual_count"],
        "full_min_residual": payload["full_min_residual"],
        "summary": str(args.summary),
        "source_solution": str(args.source_out),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
