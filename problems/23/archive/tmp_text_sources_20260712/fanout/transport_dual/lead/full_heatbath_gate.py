"""Exact full-product heat-bath test for active-scoped Hall failures."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from concurrent.futures import ProcessPoolExecutor

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice, scoped_score
from _codex_r23_outside_attachment_full_obligation_gate import full_owner_flow


def analyze_graph(g6: str):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None or any(length != 5 for length in info["ell"].values()):
        return None
    families = shortest_row_families(info)
    choices = tuple(itertools.product(*(range(len(f)) for f in families)))
    scores = []
    rows = []
    for choice in choices:
        selected = rows_for_choice(families, choice)
        rows.append(selected)
        scores.append(scoped_score(n, info, selected))
    total = sum(scores)
    count = len(scores)
    failures = []
    for choice, selected, score in zip(choices, rows, scores):
        if score == 0:
            continue
        flow = full_owner_flow(
            n, set(info["Bset"]), set(info["Mset"]), selected, g6,
            require_full=False, quiet=True, scope="active", include_outside=False,
        )
        if flow["full"]:
            continue
        numerator = count * score - total
        defect_residual = numerator - count * flow["deficiency"]
        failures.append({
            "choice": choice,
            "score": score,
            "meanGapNumerator": numerator,
            "meanDenominator": count,
            "deficiency": flow["deficiency"],
            "defectResidualNumerator": defect_residual,
            "owners": flow["deficientOwners"],
        })
    if not failures:
        return None
    return {
        "g6": g6,
        "tuples": count,
        "scoreSum": total,
        "failures": len(failures),
        "nonpositive": sum(x["meanGapNumerator"] <= 0 for x in failures),
        "defectBoundFailures": sum(
            x["defectResidualNumerator"] < 0 for x in failures
        ),
        "min": min(failures, key=lambda x: x["meanGapNumerator"]),
        "firstNonpositive": next(
            (x for x in failures if x["meanGapNumerator"] <= 0), None
        ),
        "firstDefectBoundFailure": next(
            (x for x in failures if x["defectResidualNumerator"] < 0), None
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-order", type=int, default=10)
    parser.add_argument("--max-order", type=int, default=11)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    graph6, generated = graph6_for_orders(args.min_order, args.max_order)
    aggregate = {
        "orders": [args.min_order, args.max_order],
        "workers": args.workers,
        "generatedByOrder": generated,
        "graphsWithFailures": 0,
        "tuplesInThoseGraphs": 0,
        "failures": 0,
        "nonpositive": 0,
        "defectBoundFailures": 0,
        "smallestGap": None,
        "firstNonpositive": None,
        "firstDefectBoundFailure": None,
    }
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(analyze_graph, graph6, chunksize=8):
            if result is None:
                continue
            aggregate["graphsWithFailures"] += 1
            aggregate["tuplesInThoseGraphs"] += result["tuples"]
            aggregate["failures"] += result["failures"]
            aggregate["nonpositive"] += result["nonpositive"]
            aggregate["defectBoundFailures"] += result["defectBoundFailures"]
            candidate = {"g6": result["g6"], **result["min"]}
            if (
                aggregate["smallestGap"] is None
                or candidate["meanGapNumerator"]
                < aggregate["smallestGap"]["meanGapNumerator"]
            ):
                aggregate["smallestGap"] = candidate
            if aggregate["firstNonpositive"] is None and result["firstNonpositive"]:
                aggregate["firstNonpositive"] = {
                    "g6": result["g6"], **result["firstNonpositive"]
                }
            if (
                aggregate["firstDefectBoundFailure"] is None
                and result["firstDefectBoundFailure"]
            ):
                aggregate["firstDefectBoundFailure"] = {
                    "g6": result["g6"], **result["firstDefectBoundFailure"]
                }
    source = __file__
    with open(source, "rb") as handle:
        aggregate["scriptSha256"] = hashlib.sha256(handle.read()).hexdigest()
    print(json.dumps(aggregate, sort_keys=True, separators=(",", ":")))
    return int(
        aggregate["nonpositive"] != 0
        or aggregate["defectBoundFailures"] != 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
