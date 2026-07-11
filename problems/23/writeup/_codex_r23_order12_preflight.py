"""Bounded preflight for order-12 active-scoped row-choice products.

The full gate can be dominated by one graph with a large Cartesian product
of shortest-row families.  This preflight performs no row-tuple enumeration;
it computes each exact Gamma-min cut, filters to all-ell=5 instances, and
reports the largest family products so the stragglers can be sharded.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families


def inspect(g6):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None:
        return ("skipNoCut", g6, 0, (), 0)
    if any(length != 5 for length in info["ell"].values()):
        return ("skipNotAll5", g6, 0, (), len(info["M"]))
    sizes = tuple(len(family) for family in shortest_row_families(info))
    return ("eligible", g6, math.prod(sizes), sizes, len(info["M"]))


def positive(value):
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", type=positive, default=12)
    parser.add_argument("--workers", type=positive, default=min(61, os.cpu_count() or 1))
    parser.add_argument("--top", type=positive, default=30)
    args = parser.parse_args()
    if args.workers > 61:
        parser.error("Windows ProcessPoolExecutor supports at most 61 workers")
    graph6, generated = graph6_for_orders(args.order, args.order)
    status = Counter()
    products = Counter()
    top = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for kind, g6, count, sizes, bads in pool.map(inspect, graph6, chunksize=64):
            status[kind] += 1
            if kind != "eligible":
                continue
            products[str(count)] += 1
            item = (count, g6, sizes, bads)
            if len(top) < args.top:
                top.append(item)
                top.sort(reverse=True)
            elif item > top[-1]:
                top[-1] = item
                top.sort(reverse=True)
    payload = {
        "order": args.order,
        "workers": args.workers,
        "generated": generated,
        "status": dict(status),
        "productHistogram": dict(sorted(products.items(), key=lambda kv: int(kv[0]))),
        "top": [
            {"tuples": count, "g6": g6, "familySizes": sizes, "badEdges": bads}
            for count, g6, sizes, bads in top
        ],
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
