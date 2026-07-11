"""Size coherent shortest-row products before launching exchange enumeration."""

from __future__ import annotations

import argparse
import json
import math
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

from _codex_r19_global_base_census import dec, graph6_for_orders, loads


def size_graph(g6):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None:
        return "skipNoCut", 0, 0
    if any(length != 5 for length in info["ell"].values()):
        return "skipNotAll5", 0, 0
    family_sizes = [len(info["cyc"][edge]) for edge in info["M"]]
    return "eligible", math.prod(family_sizes), max(family_sizes, default=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-order", type=int, default=11)
    parser.add_argument("--max-order", type=int, default=11)
    parser.add_argument("--workers", type=int, default=min(61, os.cpu_count() or 1))
    args = parser.parse_args()
    if not (1 <= args.workers <= 61):
        parser.error("--workers must be between 1 and 61 on Windows")
    graph6, generated = graph6_for_orders(args.min_order, args.max_order)
    status = Counter()
    histogram = Counter()
    total = 0
    maximum = 0
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for state, tuples, _ in pool.map(size_graph, graph6, chunksize=16):
            status[state] += 1
            if state == "eligible":
                histogram[tuples] += 1
                total += tuples
                maximum = max(maximum, tuples)
    print(json.dumps({
        "orders": [args.min_order, args.max_order],
        "workers": args.workers,
        "generatedByOrder": generated,
        "status": dict(sorted(status.items())),
        "totalRowTuples": total,
        "maxRowTuplesPerGraph": maximum,
        "tupleHistogram": dict(sorted(histogram.items())),
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
