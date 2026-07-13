import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_full_residual_check as fullcheck
import _codex_eq_odl1_rung2_scipy_core_probe as probe


def compute_residual(prepared, columns, source_cols, sol):
    residual = prepared.p_beta[:]
    for val, source_col in zip(sol, source_cols):
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


def coeff_at(columns, source_col, row):
    for rr, coeff in columns[source_col].terms:
        if rr == row:
            return coeff
    return Fraction(0)


def add_independent(echelon, vec):
    v = list(vec)
    for pivot, row in echelon:
        if v[pivot]:
            factor = v[pivot]
            v = [a - factor * b for a, b in zip(v, row)]
    if not any(v):
        return False
    pivot = next(i for i, x in enumerate(v) if x)
    factor = v[pivot]
    v = [x / factor for x in v]
    for idx, (old_pivot, row) in enumerate(echelon):
        if row[pivot]:
            factor = row[pivot]
            echelon[idx] = (old_pivot, [a - factor * b for a, b in zip(row, v)])
    echelon.append((pivot, v))
    echelon.sort(key=lambda x: x[0])
    return True


def solve_square(rows, rhs):
    n = len(rows)
    mat = [list(row) + [b] for row, b in zip(rows, rhs)]
    pivots = []
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, n):
            if mat[i][c]:
                piv = i
                break
        if piv is None:
            continue
        mat[r], mat[piv] = mat[piv], mat[r]
        fac = mat[r][c]
        mat[r] = [x / fac for x in mat[r]]
        for i in range(n):
            if i != r and mat[i][c]:
                fac = mat[i][c]
                mat[i] = [a - fac * b for a, b in zip(mat[i], mat[r])]
        pivots.append(c)
        r += 1
        if r == n:
            break
    if len(pivots) != n:
        raise ValueError(f"rank {len(pivots)} != {n}")
    sol = [Fraction(0) for _ in range(n)]
    for i, c in enumerate(pivots):
        sol[c] = mat[i][-1]
    return sol


def parse_used(report):
    last = report["history"][-1]
    return [(int(item["source_col"]), float(item["t"])) for item in last["used"]]


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
    residual = compute_residual(prepared, columns, source_cols, sol)
    report = json.loads(args.repair_report.read_text(encoding="utf-8"))
    used = parse_used(report)
    used_cols = [c for c, _ in used]
    n = len(used_cols)

    delta_float = [0.0] * len(residual)
    touched = set()
    for source_col, t in used:
        for row, coeff in columns[source_col].terms:
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
        vec = [coeff_at(columns, c, row) for c in used_cols]
        if not any(vec):
            continue
        if add_independent(echelon, vec):
            selected.append(row)
            selected_vecs.append(vec)
            selected_rhs.append(residual[row])
            if len(selected) == n:
                break
    if len(selected) != n:
        raise RuntimeError(f"selected only {len(selected)} independent rows for {n} columns")

    increments_list = solve_square(selected_vecs, selected_rhs)
    increments = dict(zip(used_cols, increments_list))

    repaired_residual = residual[:]
    for source_col, val in increments.items():
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            repaired_residual[row] -= coeff * val

    vals = {}
    for val, source_col in zip(sol, source_cols):
        vals[source_col] = vals.get(source_col, Fraction(0)) + val
    for source_col, val in increments.items():
        vals[source_col] = vals.get(source_col, Fraction(0)) + val

    args.source_out.parent.mkdir(parents=True, exist_ok=True)
    with args.source_out.open("w", encoding="utf-8") as f:
        for source_col in sorted(vals):
            val = vals[source_col]
            if val:
                f.write(json.dumps({
                    "source_col": source_col,
                    "num": val.numerator,
                    "den": val.denominator,
                }, sort_keys=True) + "\n")

    negative_rows = [(i, x) for i, x in enumerate(repaired_residual) if x < 0]
    payload = {
        "schema": "exact_rationalize_multirepair_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "core": str(args.core),
        "core_solution": str(args.solution),
        "repair_report": str(args.repair_report),
        "source_solution": str(args.source_out),
        "used_source_cols": used_cols,
        "selected_rows": selected,
        "increments": {
            str(source_col): {"num": val.numerator, "den": val.denominator}
            for source_col, val in increments.items()
        },
        "increment_negative_count": sum(1 for val in increments.values() if val < 0),
        "solution_negative_count": sum(1 for val in vals.values() if val < 0),
        "full_negative_residual_count": len(negative_rows),
        "full_min_residual": str(min(repaired_residual) if repaired_residual else Fraction(0)),
        "negative_rows_prefix": [
            {"row": int(row), "beta": list(prepared.betas[row]), "residual": str(val)}
            for row, val in negative_rows[:20]
        ],
        "exact_ok": sum(1 for val in vals.values() if val < 0) == 0 and len(negative_rows) == 0,
    }
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
