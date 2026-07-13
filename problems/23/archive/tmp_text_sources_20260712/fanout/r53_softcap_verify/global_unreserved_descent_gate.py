"""Exact one/two-row collision-descent gate for corrected global Hall failures."""

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
for path in (HERE, WRITEUP, R32, P5, PHT):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice
from global_unreserved_census import analyze_tuple
from p5_core import make_graph_context


def hamming_distance(left, right):
    return sum(x != y for x, y in zip(left, right))


def analyze_graph(task):
    order, ordinal, g6 = task
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    if info is None:
        return {"status": "skip", "order": order}
    if any(length != 5 for length in info["ell"].values()):
        return {"status": "skip", "order": order}

    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    choices = tuple(product(*(range(size) for size in sizes)))
    ctx = make_graph_context(n, info["Bset"], info["Mset"])
    landscape = {}
    for choice in choices:
        result = analyze_tuple(ctx, rows_for_choice(families, choice))
        landscape[choice] = (result["demand"] // 2, result["defect"], result)

    failures = [choice for choice in choices if landscape[choice][1] > 0]
    no_one = []
    no_two = []
    for choice in failures:
        collision = landscape[choice][0]
        one = any(
            hamming_distance(choice, other) == 1
            and landscape[other][0] < collision
            for other in choices
        )
        if not one:
            no_one.append(choice)
        two = one or any(
            hamming_distance(choice, other) <= 2
            and landscape[other][0] < collision
            for other in choices
        )
        if not two:
            no_two.append(choice)

    def record(choice):
        collision, defect, result = landscape[choice]
        return {
            "order": order,
            "ordinal": ordinal,
            "g6": g6,
            "choice": choice,
            "familySizes": sizes,
            "collisionUnits": collision,
            "defect": defect,
            "shore": result["shore"],
            "shoreDemand": result["shoreDemand"],
            "shoreReach": result["shoreReach"],
        }

    return {
        "status": "tested",
        "order": order,
        "failures": len(failures),
        "noOne": len(no_one),
        "noTwo": len(no_two),
        "firstNoOne": record(no_one[0]) if no_one else None,
        "firstNoTwo": record(no_two[0]) if no_two else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=10)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--output", type=Path, default=HERE / "global_unreserved_descent_n5_n10.json")
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        parser.error("workers must be in 1..16")

    graphs, _ = graph6_for_orders(args.n_min, args.n_max)
    ordinals = Counter()
    tasks = []
    for g6 in graphs:
        order, _edges = dec(g6)
        ordinal = ordinals[order]
        ordinals[order] += 1
        tasks.append((order, ordinal, g6))

    counts = Counter()
    first_no_one = None
    first_no_two = None
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for result in executor.map(analyze_graph, tasks, chunksize=16):
            counts[result["status"]] += 1
            if result["status"] != "tested":
                continue
            counts["failures"] += result["failures"]
            counts["noOne"] += result["noOne"]
            counts["noTwo"] += result["noTwo"]
            if first_no_one is None and result["firstNoOne"] is not None:
                first_no_one = result["firstNoOne"]
            if first_no_two is None and result["firstNoTwo"] is not None:
                first_no_two = result["firstNoTwo"]

    payload = {
        "range": [args.n_min, args.n_max],
        "counts": dict(counts),
        "firstNoOneRowDescent": first_no_one,
        "firstNoTwoRowDescent": first_no_two,
        "descentPotential": "global collisionUnits",
        "failurePredicate": "global unreserved P1+P3+common-blue Hall defect > 0",
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="ascii")
    print(json.dumps(payload, sort_keys=True))
    print("VERDICT_ONE=", "PASS" if first_no_one is None else "FAIL")
    print("VERDICT_TWO=", "PASS" if first_no_two is None else "FAIL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
