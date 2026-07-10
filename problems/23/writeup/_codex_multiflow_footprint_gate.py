"""Exact series-parallel audit for the first local-obstruction footprints.

For a finite simple graph, being series-parallel in the multiflow sense used by
Chakrabarti--Fleischer--Weibel is equivalent (componentwise, after the usual
biconnected reduction) to having no K4 minor, equivalently treewidth at most 2.
The recursive elimination test below is exact: it searches for an elimination
ordering in which every eliminated vertex has at most two remaining neighbors,
adding the fill edge between two neighbors when necessary.

The listed graph6 strings are the complete m=9 and m=10 footprint orbits from
the existing local-obstruction scan.
"""

from __future__ import annotations

import json
from functools import lru_cache

from _claude_d3_local_obstruction import parse_g6


FOOTPRINTS = {
    9: ("H???FaM",),
    10: ("I????B_fo", "I????Bobo", "I???E?wh_"),
}


def adjacency_masks(g6: str) -> tuple[int, ...]:
    n, adj, _edges = parse_g6(g6)
    return tuple(sum(1 << v for v in adj[u]) for u in range(n))


@lru_cache(maxsize=None)
def tw2_order_cached(state: tuple[int, ...]) -> tuple[int, ...] | None:
    alive = [v for v, mask in enumerate(state) if mask >= 0]
    if len(alive) <= 2:
        return tuple(alive)

    for v in alive:
        nbrs = [u for u in alive if (state[v] >> u) & 1]
        if len(nbrs) > 2:
            continue

        nxt = list(state)
        if len(nbrs) == 2:
            a, b = nbrs
            nxt[a] |= 1 << b
            nxt[b] |= 1 << a
        for u in nbrs:
            nxt[u] &= ~(1 << v)
        nxt[v] = -1

        suffix = tw2_order_cached(tuple(nxt))
        if suffix is not None:
            return (v,) + suffix
    return None


def cut_condition_margin(g6: str, demands: tuple[tuple[int, int], ...]) -> int:
    n, _adj, edges = parse_g6(g6)
    best = 10**9
    for mask in range(1 << (n - 1)):
        shore = mask << 1
        supply = sum(((shore >> u) ^ (shore >> v)) & 1 for u, v in edges)
        demand = sum(((shore >> u) ^ (shore >> v)) & 1 for u, v in demands)
        best = min(best, supply - demand)
    return best


DEMANDS = {
    "H???FaM": (
        (1, 4), (1, 5), (1, 6),
        (2, 4), (2, 5), (2, 6),
        (3, 4), (3, 5), (3, 6),
    ),
    "I????B_fo": (
        (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
        (2, 3), (2, 4), (2, 5), (2, 6), (2, 7),
    ),
    "I????Bobo": (
        (1, 4), (1, 5), (1, 6), (1, 7),
        (2, 4), (2, 5), (2, 6), (2, 7),
        (3, 4), (3, 5),
    ),
    "I???E?wh_": (
        (0, 3), (0, 4), (1, 2), (1, 5), (1, 6),
        (3, 5), (3, 6), (4, 5), (4, 6), (7, 8),
    ),
}


def main() -> None:
    rows = []
    for m, graphs in FOOTPRINTS.items():
        for g6 in graphs:
            n, _adj, edges = parse_g6(g6)
            order = tw2_order_cached(adjacency_masks(g6))
            margin = cut_condition_margin(g6, DEMANDS[g6])
            rows.append({
                "m": m,
                "g6": g6,
                "vertices": n,
                "supplyEdges": len(edges),
                "seriesParallel": order is not None,
                "tw2EliminationOrder": list(order) if order is not None else None,
                "unitCutConditionMinMargin": margin,
            })
    assert len(rows) == 4
    print(json.dumps(rows, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

