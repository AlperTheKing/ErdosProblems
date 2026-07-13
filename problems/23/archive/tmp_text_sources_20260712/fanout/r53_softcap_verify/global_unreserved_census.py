"""Exact N<=10 census for the global unreserved soft-collision provider.

Every global collision half is demanded. Actual off-diagonal free halves are
available through P1, P3, or corrected common-blue. P4/P5 are deliberately
omitted. Hall is checked exactly over owner shores and cross-checked against
integer maximum flow on every first failure/pass representative.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems/23/writeup"
R32 = ROOT / "tmp/fanout/r32_n12_fullbank"
P5 = ROOT / "tmp/fanout/p5_n12_census"
PHT = ROOT / "tmp/fanout/pht_n12_direct"
for path in (WRITEUP, R32, P5, PHT):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice
from p5_core import make_graph_context, reconstruct_state, source_id


def analyze_tuple(ctx, rows):
    state = reconstruct_state(ctx, rows)
    n = ctx.n
    demand = tuple(
        2 * sum(max(0, state.pair[owner][y] - 1) for y in range(n))
        for owner in range(n)
    )
    owners = tuple(owner for owner in range(n) if demand[owner] > 0)
    if not owners:
        return {"demand": 0, "flow": 0, "defect": 0, "shore": []}

    owner_index = {owner: index for index, owner in enumerate(owners)}
    relation = {}
    for x in range(n):
        for y in range(n):
            if x == y or state.pair[x][y] != 0:
                continue
            mask = 0
            for owner in owners:
                p1 = x == owner
                p3 = (
                    state.pair[owner][x] > 0
                    and state.pair[owner][y] > 0
                    and ctx.sigma_pair[x][y] >= 0
                )
                common_blue = (
                    x in ctx.blue_adj[owner]
                    and y in ctx.blue_adj[owner]
                    and ctx.sigma_pair[x][y] >= 2
                )
                if p1 or p3 or common_blue:
                    mask |= 1 << owner_index[owner]
            if mask:
                relation[source_id(n, x, y, 0)] = mask
                relation[source_id(n, x, y, 1)] = mask

    owner_count = len(owners)
    full_mask = (1 << owner_count) - 1
    histogram = [0] * (1 << owner_count)
    for mask in relation.values():
        histogram[mask] += 1
    subset = histogram[:]
    for index in range(owner_count):
        bit = 1 << index
        for mask in range(1 << owner_count):
            if mask & bit:
                subset[mask] += subset[mask ^ bit]

    demand_sum = [0] * (1 << owner_count)
    worst_defect = 0
    worst_mask = 0
    worst_reach = 0
    for mask in range(1, 1 << owner_count):
        bit = mask & -mask
        index = bit.bit_length() - 1
        demand_sum[mask] = demand_sum[mask ^ bit] + demand[owners[index]]
        reach = len(relation) - subset[full_mask ^ mask]
        defect = demand_sum[mask] - reach
        if defect > worst_defect:
            worst_defect = defect
            worst_mask = mask
            worst_reach = reach

    total = sum(demand)
    return {
        "demand": total,
        "flow": total - worst_defect,
        "defect": worst_defect,
        "shore": [
            owner for index, owner in enumerate(owners)
            if worst_mask & (1 << index)
        ],
        "shoreDemand": demand_sum[worst_mask],
        "shoreReach": worst_reach,
    }


def analyze_graph(task):
    order, ordinal, g6 = task
    n, graph_edges = dec(g6)
    assert n == order
    info = loads(n, graph_edges)
    if info is None:
        return {"status": "skipNoCut", "order": order}
    if any(length != 5 for length in info["ell"].values()):
        return {"status": "skipNotAll5", "order": order}

    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    ctx = make_graph_context(n, info["Bset"], info["Mset"])
    tuple_count = 0
    failing_count = 0
    minimum_collision = None
    minimum_failures = 0
    first_failure = None
    first_pass = None

    for tuple_index, choice in enumerate(product(*(range(size) for size in sizes))):
        rows = rows_for_choice(families, choice)
        result = analyze_tuple(ctx, rows)
        tuple_count += 1
        collision_units = result["demand"] // 2
        if minimum_collision is None or collision_units < minimum_collision:
            minimum_collision = collision_units
            minimum_failures = int(result["defect"] > 0)
        elif collision_units == minimum_collision:
            minimum_failures += int(result["defect"] > 0)
        if result["defect"] > 0:
            failing_count += 1
            if first_failure is None:
                first_failure = {
                    "order": order,
                    "ordinal": ordinal,
                    "g6": g6,
                    "choice": choice,
                    "tupleIndex": tuple_index,
                    **result,
                }
        elif first_pass is None:
            first_pass = {
                "order": order,
                "ordinal": ordinal,
                "g6": g6,
                "choice": choice,
                "tupleIndex": tuple_index,
                **result,
            }

    return {
        "status": "tested",
        "order": order,
        "tupleCount": tuple_count,
        "failingCount": failing_count,
        "allFail": failing_count == tuple_count,
        "minimumCollision": minimum_collision,
        "minimumFailures": minimum_failures,
        "firstFailure": first_failure,
        "firstPass": first_pass,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=10)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--output", type=Path, default=HERE / "global_unreserved_census_n5_n10.json")
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        parser.error("workers must be in 1..16")

    graphs, _generated_by_order = graph6_for_orders(args.n_min, args.n_max)
    ordinals = Counter()
    tasks = []
    for g6 in graphs:
        order, _ = dec(g6)
        ordinal = ordinals[order]
        ordinals[order] += 1
        tasks.append((order, ordinal, g6))

    status = Counter()
    by_order = {}
    first_failure = None
    first_all_fail = None
    first_minimum_failure = None
    first_pass = None
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for result in executor.map(analyze_graph, tasks, chunksize=16):
            order_counts = by_order.setdefault(result["order"], Counter())
            status[result["status"]] += 1
            order_counts[result["status"]] += 1
            if result["status"] != "tested":
                continue
            order_counts["tuples"] += result["tupleCount"]
            order_counts["failingTuples"] += result["failingCount"]
            order_counts["allFailGraphs"] += int(result["allFail"])
            order_counts["minimumFailingGraphs"] += int(result["minimumFailures"] > 0)
            if first_failure is None and result["firstFailure"] is not None:
                first_failure = result["firstFailure"]
            if first_pass is None and result["firstPass"] is not None:
                first_pass = result["firstPass"]
            if first_all_fail is None and result["allFail"]:
                first_all_fail = result["firstFailure"]
            if first_minimum_failure is None and result["minimumFailures"] > 0:
                first_minimum_failure = result["firstFailure"]

    payload = {
        "range": [args.n_min, args.n_max],
        "workers": args.workers,
        "relation": ["P1", "P3", "corrected-common-blue"],
        "reservation": "none",
        "scope": "all global collision halves",
        "status": dict(status),
        "byOrder": {str(order): dict(counts) for order, counts in sorted(by_order.items())},
        "firstFailure": first_failure,
        "firstPass": first_pass,
        "firstAllFail": first_all_fail,
        "firstMinimumCollisionFailure": first_minimum_failure,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="ascii")
    print(json.dumps(payload["byOrder"], sort_keys=True))
    print("firstAllFail=", first_all_fail)
    print("firstMinimumCollisionFailure=", first_minimum_failure)
    if first_all_fail is not None:
        print("VERDICT=FAIL_GRAPH_WITH_NO_FEASIBLE_TUPLE")
        return 1
    print("VERDICT=PASS_EXISTS_PER_GRAPH_IN_RANGE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
