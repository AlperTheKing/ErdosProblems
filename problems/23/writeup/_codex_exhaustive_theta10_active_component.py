"""Exhaust the smallest P4-plus-active-P6 bipartite geometry.

The ten vertices form a fixed P4 x-y support corridor and an internally
disjoint P6 x-y off-support path.  Among the remaining fifteen K5,5 edges,
every subset is tested as additional support.  For every connected completion
where x-y remains an ell=5 atom whose full support avoids P6, the exact atom
circuit solver searches for a triangle-free inclusion-minimal defect-one
family containing x-y.
"""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor, as_completed

from _codex_fixed_active_path_search import candidates, connected, edge, select_circuit


N = 10
SIDE0 = range(5)
SIDE1 = range(5, 10)
X, Y = 0, 1
P4 = {edge(0, 5), edge(5, 2), edge(2, 6), edge(6, 1)}
I6 = {edge(0, 7), edge(7, 3), edge(3, 8),
      edge(8, 4), edge(4, 9), edge(9, 1)}
OPTIONAL = sorted({edge(u, v) for u in SIDE0 for v in SIDE1} - P4 - I6)
assert len(OPTIONAL) == 15


def worker(bounds):
    lo, hi = bounds
    stats = {"masks": 0, "connected": 0, "forcedValid": 0,
             "pairsEnough": 0, "circuitCaps": 0}
    first = None
    for mask in range(lo, hi):
        stats["masks"] += 1
        F = sorted(P4 | {OPTIONAL[i] for i in range(len(OPTIONAL)) if (mask >> i) & 1})
        if not connected(N, F):
            continue
        stats["connected"] += 1
        pairs = candidates(N, F, sorted(I6))
        if not any(pair == (X, Y) for pair, _support in pairs):
            continue
        stats["forcedValid"] += 1
        if len(pairs) < len(F) + 1:
            continue
        stats["pairsEnough"] += 1
        circuit, nodes, capped = select_circuit(N, F, sorted(I6), (X, Y), 10_000_000)
        stats["circuitCaps"] += int(capped)
        if circuit is not None:
            first = {"mask": mask, "support": F,
                     "atoms": [list(pair) for pair, _s in circuit],
                     "supportMasks": [s for _pair, s in circuit],
                     "nodes": nodes}
            break
    return {"stats": stats, "first": first}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=60)
    args = parser.parse_args()
    total = 1 << len(OPTIONAL)
    chunk = (total + args.workers - 1) // args.workers
    bounds = [(lo, min(total, lo + chunk)) for lo in range(0, total, chunk)]
    totals = {"masks": 0, "connected": 0, "forcedValid": 0,
              "pairsEnough": 0, "circuitCaps": 0}
    first = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(worker, bound) for bound in bounds]
        for future in as_completed(futures):
            row = future.result()
            for key in totals:
                totals[key] += row["stats"][key]
            if row["first"] is not None and first is None:
                first = row["first"]
                for pending in futures:
                    pending.cancel()
    print(json.dumps({"optionalEdges": len(OPTIONAL), "totals": totals,
                      "first": first}, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
