"""Exact full-product PHT gate for the order-12 heavy tail.

Omega is the full Cartesian product of the complete shortest-row families,
with every coherent row tuple counted once.  Score is the active-scoped
collision-half plus HitNeed cardinality.  For the owner shore returned by the
exact max-flow failure, deficiency is demand cardinality minus the cardinality
of its available FreeHalf neighborhood, including ScopedReserved removal and
same-owner/row-companion eligibility.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "problems" / "23" / "writeup"))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice, scoped_score
from _codex_r23_order12_preflight import inspect
from _codex_r23_outside_attachment_full_obligation_gate import full_owner_flow


def analyze_graph(item):
    g6, expected_count = item
    n, edges = dec(g6)
    info = loads(n, edges)
    assert info is not None
    assert all(length == 5 for length in info["ell"].values())
    families = shortest_row_families(info)
    choices = tuple(itertools.product(*(range(len(f)) for f in families)))
    assert len(choices) == expected_count
    scores = []
    selected_rows = []
    for choice in choices:
        rows = rows_for_choice(families, choice)
        selected_rows.append(rows)
        scores.append(scoped_score(n, info, rows))
    total = sum(scores)
    count = len(scores)
    failures = 0
    defect_bound_failures = 0
    minimum = None
    first_falsifier = None
    for choice, rows, score in zip(choices, selected_rows, scores):
        if score == 0:
            continue
        flow = full_owner_flow(
            n,
            set(info["Bset"]),
            set(info["Mset"]),
            rows,
            g6,
            require_full=False,
            quiet=True,
            scope="active",
            include_outside=False,
        )
        if flow["full"]:
            continue
        failures += 1
        defect = flow["deficiency"]
        residual = count * (score - defect) - total
        record = {
            "g6": g6,
            "choice": list(choice),
            "omegaCard": count,
            "score": score,
            "scoreSum": total,
            "deficiency": defect,
            "owners": flow["deficientOwners"],
            "residualNumerator": residual,
            "residualDenominator": count,
        }
        ratio = Fraction(residual, count)
        if minimum is None or ratio < Fraction(
            minimum["residualNumerator"], minimum["residualDenominator"]
        ):
            minimum = record
        if residual < 0:
            defect_bound_failures += 1
            if first_falsifier is None:
                first_falsifier = record
    return {
        "g6": g6,
        "tuples": count,
        "failures": failures,
        "defectBoundFailures": defect_bound_failures,
        "minimum": minimum,
        "firstFalsifier": first_falsifier,
    }


def positive(value):
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", type=positive, default=12)
    parser.add_argument("--min-product", type=positive, default=4097)
    parser.add_argument("--workers", type=positive, default=min(61, os.cpu_count() or 1))
    parser.add_argument("--expected-tuples", type=int, default=0)
    args = parser.parse_args()
    if args.workers > 61:
        parser.error("Windows ProcessPoolExecutor supports at most 61 workers")

    graph6, generated = graph6_for_orders(args.order, args.order)
    status = Counter()
    heavy = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for kind, g6, count, _sizes, _bads in pool.map(inspect, graph6, chunksize=64):
            status[kind] += 1
            if kind == "eligible" and count >= args.min_product:
                heavy.append((g6, count))
    heavy.sort(key=lambda item: (-item[1], item[0]))
    heavy_tuples = sum(count for _, count in heavy)
    if args.expected_tuples:
        assert heavy_tuples == args.expected_tuples

    aggregate = {
        "graphs": 0,
        "tuples": 0,
        "failures": 0,
        "defectBoundFailures": 0,
    }
    minimum = None
    first_falsifier = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(analyze_graph, heavy, chunksize=1):
            aggregate["graphs"] += 1
            aggregate["tuples"] += result["tuples"]
            aggregate["failures"] += result["failures"]
            aggregate["defectBoundFailures"] += result["defectBoundFailures"]
            candidate = result["minimum"]
            if candidate is not None and (
                minimum is None
                or Fraction(candidate["residualNumerator"], candidate["residualDenominator"])
                < Fraction(minimum["residualNumerator"], minimum["residualDenominator"])
            ):
                minimum = candidate
            if first_falsifier is None and result["firstFalsifier"] is not None:
                first_falsifier = result["firstFalsifier"]

    assert aggregate["graphs"] == len(heavy)
    assert aggregate["tuples"] == heavy_tuples
    payload = {
        "order": args.order,
        "workers": args.workers,
        "minProduct": args.min_product,
        "generatedGraphs": generated,
        "status": dict(sorted(status.items())),
        "heavyGraphs": len(heavy),
        "heavyTuples": heavy_tuples,
        **aggregate,
        "minimumResidual": minimum,
        "firstFalsifier": first_falsifier,
        "scriptSha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return int(aggregate["defectBoundFailures"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
