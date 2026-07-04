#!/usr/bin/env python3
"""Parallel numeric map for EQ-ODL1 Rung-2 reduced-support charts.

This is a numeric-only scout requested by Claude: chart -> feasible / infeasible /
timeout for the reduced-support full-dominance LP.  It deliberately does not claim
certificate validity; exact rational replay is handled elsewhere.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
from pathlib import Path

import _codex_eq_odl1_rung2_support_lp as support_lp


def parse_ints(text: str, upper: int) -> list[int]:
    if text == "all":
        return list(range(upper))
    return [int(x) for x in text.split(",") if x]


def run_chart(args_tuple):
    k, dominants, bands, support, objective, method, time_limit, no_deltas, leading_s0_only = args_tuple
    prepared = support_lp.prepare_chart(k)
    rows = []
    for dominant in dominants:
        for band in bands:
            item = support_lp.solve_one(
                k,
                dominant,
                band,
                support,
                None,
                None,
                time_limit,
                objective,
                method,
                [1000000],
                False,
                include_deltas=not no_deltas,
                leading_s0_only=leading_s0_only,
                prepared=prepared,
            )
            # Keep map compact: no exact_check attempts in numeric-only mode.
            item.pop("exact_check", None)
            item.pop("family_counts", None)
            rows.append(item)
    return {"k": k, "items": rows}


def summarize(chart_results: list[dict[str, object]], complete: bool) -> dict[str, object]:
    items = []
    for result in chart_results:
        items.extend(result["items"])
    by_status = {"feasible_numeric": 0, "infeasible": 0, "timeout": 0, "other_failure": 0}
    for item in items:
        if item.get("success"):
            by_status["feasible_numeric"] += 1
        elif item.get("lp_status") == 2:
            by_status["infeasible"] += 1
        elif item.get("lp_status") == 1:
            by_status["timeout"] += 1
        else:
            by_status["other_failure"] += 1
    return {
        "schema": "eq_odl1_rung2_support_numeric_map_v1",
        "complete": complete,
        "charts_done": len(chart_results),
        "rows": len(items),
        **by_status,
        "chart_results": chart_results,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--charts", default="all")
    ap.add_argument("--dominants", default="all")
    ap.add_argument("--bands", default="all")
    ap.add_argument("--support", choices=["negative", "all"], default="negative")
    ap.add_argument("--objective", choices=["sum", "zero", "margin"], default="sum")
    ap.add_argument("--method", choices=["highs", "highs-ds", "highs-ipm"], default="highs")
    ap.add_argument("--time-limit", type=float, default=60.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-deltas", action="store_true")
    ap.add_argument("--leading-s0-only", action="store_true")
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_support_numeric_map_v1.json"))
    args = ap.parse_args()

    charts = parse_ints(args.charts, 10)
    dominants = parse_ints(args.dominants, 15)
    bands = list(support_lp.BANDS) if args.bands == "all" else [x for x in args.bands.split(",") if x]
    tasks = [(k, dominants, bands, args.support, args.objective, args.method, args.time_limit, args.no_deltas, args.leading_s0_only) for k in charts]
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    results = []
    if args.workers <= 1:
        for task in tasks:
            results.append(run_chart(task))
            args.summary.write_text(json.dumps(summarize(results, complete=False), indent=2, sort_keys=True), encoding="utf-8")
    else:
        with mp.Pool(processes=args.workers) as pool:
            for result in pool.imap_unordered(run_chart, tasks):
                results.append(result)
                results.sort(key=lambda r: r["k"])
                args.summary.write_text(json.dumps(summarize(results, complete=False), indent=2, sort_keys=True), encoding="utf-8")
    out = summarize(results, complete=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ["charts_done", "rows", "feasible_numeric", "infeasible", "timeout", "other_failure"]}, sort_keys=True))


if __name__ == "__main__":
    main()
