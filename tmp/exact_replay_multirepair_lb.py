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
from probe_rung2_multirepair_lp_lb import collapsed_source_values


def float_to_fraction(x: float, max_den: int | None) -> Fraction:
    f = Fraction(str(float(x)))
    return f if max_den is None else f.limit_denominator(max_den)


def compute_exact(
    prepared,
    columns,
    source_cols,
    sol,
    used_items,
    negative_source_columns,
    max_den: int | None,
):
    lower_bounds = {int(k): -Fraction(v) for k, v in negative_source_columns.items()}
    increments: dict[int, Fraction] = {}
    for item in used_items:
        c = int(item["source_col"])
        val = float_to_fraction(float(item["t"]), max_den)
        lb = lower_bounds.get(c, Fraction(0))
        if val < lb:
            val = lb
        if val:
            increments[c] = val

    repaired_residual = base.compute_residual(prepared, columns, source_cols, sol)
    for c, val in increments.items():
        for row, coeff in columns[c].terms:
            repaired_residual[row] -= coeff * val

    vals = collapsed_source_values(source_cols, sol)
    for c, val in increments.items():
        vals[c] = vals.get(c, Fraction(0)) + val

    negative_rows = [(i, x) for i, x in enumerate(repaired_residual) if x < 0]
    negative_vals = [(c, x) for c, x in vals.items() if x < 0]
    negative_increments = [(c, x) for c, x in increments.items() if x < 0]
    return {
        "max_denominator": max_den if max_den is not None else "decimal_exact",
        "used_count": len(increments),
        "increment_negative_count": len(negative_increments),
        "solution_negative_count": len(negative_vals),
        "full_negative_residual_count": len(negative_rows),
        "full_min_residual": str(min(repaired_residual) if repaired_residual else Fraction(0)),
        "solution_min_value": str(min(vals.values()) if vals else Fraction(0)),
        "exact_ok": not negative_rows and not negative_vals and not negative_increments,
        "negative_rows_prefix": [
            {"row": int(row), "beta": list(prepared.betas[row]), "residual": str(val)}
            for row, val in negative_rows[:20]
        ],
        "negative_solution_prefix": [
            {"source_col": int(c), "value": str(val)}
            for c, val in negative_vals[:20]
        ],
        "increments": {
            str(c): {"num": val.numerator, "den": val.denominator}
            for c, val in sorted(increments.items())
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--repair-report", type=Path, required=True)
    ap.add_argument("--max-den", default="1000000,10000000,100000000,1000000000,10000000000,decimal")
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--source-out", type=Path)
    args = ap.parse_args()

    dim, source_cols, _selected_rows = fullcheck.read_core_maps(args.core)
    sol = fullcheck.read_solution(args.solution, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    report = json.loads(args.repair_report.read_text(encoding="utf-8"))
    used_items = report["history"][-1]["used"]
    neg_source = report.get("negative_source_columns", {})

    denoms: list[int | None] = []
    for token in args.max_den.split(","):
        token = token.strip().lower()
        if not token:
            continue
        denoms.append(None if token == "decimal" else int(token))

    attempts = [
        compute_exact(prepared, columns, source_cols, sol, used_items, neg_source, den)
        for den in denoms
    ]
    best = min(
        attempts,
        key=lambda x: (
            x["full_negative_residual_count"],
            x["solution_negative_count"],
            x["increment_negative_count"],
            Fraction(x["full_min_residual"]),
        ),
    )
    payload = {
        "schema": "exact_replay_multirepair_lb_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "core": str(args.core),
        "core_solution": str(args.solution),
        "repair_report": str(args.repair_report),
        "attempts": [
            {k: v for k, v in attempt.items() if k != "increments"}
            for attempt in attempts
        ],
        "best": {k: v for k, v in best.items() if k != "increments"},
        "exact_ok": best["exact_ok"],
    }

    if args.source_out and best["exact_ok"]:
        vals = collapsed_source_values(source_cols, sol)
        for c_str, frac_data in best["increments"].items():
            c = int(c_str)
            val = Fraction(int(frac_data["num"]), int(frac_data["den"]))
            vals[c] = vals.get(c, Fraction(0)) + val
        args.source_out.parent.mkdir(parents=True, exist_ok=True)
        with args.source_out.open("w", encoding="utf-8") as f:
            for c in sorted(vals):
                val = vals[c]
                if val:
                    f.write(json.dumps({
                        "source_col": c,
                        "num": val.numerator,
                        "den": val.denominator,
                    }, sort_keys=True) + "\n")
        payload["source_solution"] = str(args.source_out)

    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "exact_ok": payload["exact_ok"],
        "best": payload["best"],
        "summary": str(args.summary),
        "source_solution": payload.get("source_solution"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
