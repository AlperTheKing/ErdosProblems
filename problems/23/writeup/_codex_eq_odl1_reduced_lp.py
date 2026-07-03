#!/usr/bin/env python3
"""Reduced-support EQ-ODL1 shifted-cone LP runner.

Runs the EQ-ODL1 LP on either a greedy support from
_codex_eq_odl1_support_diagnose.py or all negative-repair columns for selected
generators.  HiGHS is a search oracle; accepted output must pass exact residual
checking.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from scipy.optimize import linprog
from scipy.sparse import coo_matrix

import _codex_eq_odl1_shifted_lp as eq


def load_greedy_columns(path: Path, generators: list[eq.Generator]) -> list[eq.Column]:
    data = json.loads(path.read_text(encoding="utf-8"))
    name_to_index = {gen.name: i for i, gen in enumerate(generators)}
    cols = []
    seen = set()
    for item in data.get("greedy", []):
        gi = name_to_index[item["generator"]]
        exp = tuple(int(x) for x in item["monomial_exp"])
        key = (gi, exp)
        if key in seen:
            continue
        seen.add(key)
        cols.append(eq.Column(gi, exp))
    return cols


def load_generator_columns(target_expr, generators: list[eq.Generator], names: set[str]) -> list[eq.Column]:
    target = eq.coeff_map(target_expr)
    cols = eq.candidate_columns(target, generators, "negative")
    return [col for col in cols if generators[col.gen_index].name in names]


def solve_reduced(target_expr, cols: list[eq.Column], objective: str, time_limit: float | None, max_denominators: list[int]):
    target = eq.coeff_map(target_expr)
    generators = eq.build_generators()
    col_maps = [eq.column_map(col, generators) for col in cols]
    monoms = sorted(set(target) | set().union(*(set(m) for m in col_maps))) if col_maps else sorted(target)
    row_index = {m: i for i, m in enumerate(monoms)}
    data = []
    rows = []
    col_ids = []
    for j, cmap in enumerate(col_maps):
        for exp, coeff in cmap.items():
            rows.append(row_index[exp])
            col_ids.append(j)
            data.append(float(coeff))
    mat = coo_matrix((data, (rows, col_ids)), shape=(len(monoms), len(cols))).tocsr()
    b_ub = [float(target.get(exp, Fraction(0))) for exp in monoms]
    c = [0.0 if objective == "zero" else 1.0] * len(cols)
    options = {} if time_limit is None else {"time_limit": float(time_limit)}
    print("reduced vars", len(cols), "constraints", len(monoms), flush=True)
    res = linprog(c=c, A_ub=mat, b_ub=b_ub, bounds=[(0, None)] * len(cols), method="highs", options=options)
    out = {
        "schema": "eq_odl1_reduced_lp_v1",
        "variables": len(cols),
        "constraints": len(monoms),
        "lp_status": int(res.status),
        "lp_message": res.message,
        "success": bool(res.success),
        "objective": objective,
        "float_nonzero": None,
    }
    print("LP", res.status, res.message, flush=True)
    if not res.success:
        return out
    raw = res.x
    out["float_nonzero"] = int(sum(1 for x in raw if x > 1e-9))
    for max_den in max_denominators:
        coeffs = [Fraction(str(x)).limit_denominator(max_den) for x in raw]
        ok, check = eq.exact_check(target_expr, generators, cols, coeffs)
        print("try", max_den, "ok", ok, "min", check["residual_min_coeff"], "neg", check["negative_terms"][:1], flush=True)
        if ok:
            out.update({"exact_ok": True, "max_denominator": max_den, "exact_check": check})
            return out
    ok, check = eq.exact_check(target_expr, generators, cols, [Fraction(str(x)) for x in raw])
    out.update({"exact_ok": ok, "exact_check": check})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["greedy", "generators"], default="greedy")
    ap.add_argument("--diagnostic", default="tmp/eq_odl1_support_diagnose_v2.json")
    ap.add_argument("--generators", default="F5", help="Comma-separated generator names for --mode generators")
    ap.add_argument("--objective", choices=["zero", "sum"], default="zero")
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--max-den", default="1000,1000000")
    ap.add_argument("--summary", default="tmp/eq_odl1_reduced_lp_v1.json")
    args = ap.parse_args()

    target_expr, meta = eq.build_target()
    generators = eq.build_generators()
    if args.mode == "greedy":
        cols = load_greedy_columns(Path(args.diagnostic), generators)
    else:
        names = {x.strip() for x in args.generators.split(",") if x.strip()}
        cols = load_generator_columns(target_expr, generators, names)

    time_limit = None if args.time_limit <= 0 else args.time_limit
    max_denominators = [int(x) for x in args.max_den.split(",") if x]
    result = solve_reduced(target_expr, cols, args.objective, time_limit, max_denominators)
    result["mode"] = args.mode
    result["diagnostic"] = args.diagnostic
    result["selected_generators"] = args.generators
    result["target_meta"] = {k: v for k, v in meta.items() if k != "I_EQ"}
    result["target_terms"] = len(eq.coeff_map(target_expr))
    result["target_negative_terms"] = sum(1 for c in eq.coeff_map(target_expr).values() if c < 0)
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: result.get(k) for k in ["success", "exact_ok", "lp_status", "variables", "constraints", "float_nonzero"]}, sort_keys=True))


if __name__ == "__main__":
    main()
