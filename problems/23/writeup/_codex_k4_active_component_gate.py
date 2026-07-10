"""Search the first K4-support obstruction for a genuine active component.

Starting from the exact m=17 local obstruction on a bipartite K4 subdivision,
enumerate every first off-support chord.  Reuse the exact path search to add an
off-support-only path joining the endpoints of a selected bad atom while
preserving triangle-freeness, distance four, and the full selected support.

For every resulting active component, collapse inactive off-support
components, singletonize active components, and evaluate the exact
vertex-slack Hall margin of the remaining internal block load.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction

import _claude_d3_local_obstruction as d3
import _codex_internal_offsupport_gate as gate
import _codex_k4_subdivision_obstruction_search as k4


LENGTHS = (1, 1, 4, 2, 3, 5)


def witness_data():
    encoded = k4.subdivision(LENGTHS)
    d3.NODE_CAP = 5_000_000
    row = k4.check_case((LENGTHS, encoded))
    assert row["hasWitness"] and not row["aborted"]
    n, adj, support = d3.parse_g6(encoded)
    bad = [tuple(pair) for pair, _mask in row["witness"][1]]
    return encoded, n, adj, [tuple(e) for e in support], bad


def all_loads(n, support, bad):
    adj = [set() for _ in range(n)]
    for u, v in support:
        adj[u].add(v)
        adj[v].add(u)
    result = [Fraction(0) for _ in range(n)]
    for a, b in bad:
        da = gate.bfs(adj, a)
        db = gate.bfs(adj, b)
        assert da[b] == 4
        paths = []

        def extend(x, path):
            if x == b:
                paths.append(tuple(path))
                return
            for y in adj[x]:
                if da[y] == da[x] + 1 and da[y] + db[y] == 4:
                    extend(y, path + [y])

        extend(a, [a])
        assert paths
        for v in range(n):
            result[v] += Fraction(5 * sum(v in path for path in paths), len(paths))
    return result


def active_partition_hall(n, bad, offsupport, loads):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        x, y = find(x), find(y)
        if x != y:
            parent[max(x, y)] = min(x, y)

    for u, v in offsupport:
        union(u, v)
    component = [find(v) for v in range(n)]
    active = {component[u] for u, v in bad if component[u] == component[v]}
    demanded = {e for e in offsupport if component[e[0]] in active}
    margin, mask, caps = gate.endpoint_flow_hall_margin(n, demanded, loads)
    return {
        "components": len(set(component)),
        "activeComponents": sorted(active),
        "demandedEdges": [list(e) for e in sorted(demanded)],
        "hallMargin": str(margin),
        "hallSet": [v for v in range(n) if (mask >> v) & 1],
        "hallSetCapacity": str(sum(caps[v] for v in range(n) if (mask >> v) & 1)),
    }


def search_seed(task):
    seed, n, support, bad, loads = task
    found = gate.component_path_counterexample(
        n, support, bad, seed, max_length=n - 1
    )
    if found is None:
        return None
    offsupport = {tuple(e) for e in found["offSupport"]}
    found["seed"] = seed
    found["activePartition"] = active_partition_hall(
        n, bad, offsupport, loads
    )
    return found


def main():
    encoded, n, adj, support, bad = witness_data()
    colours = gate.bipartition(adj)
    assert colours is not None
    support_set = {tuple(sorted(e)) for e in support}
    seeds = [
        (u, v)
        for u in range(n)
        for v in range(u + 1, n)
        if colours[u] != colours[v] and (u, v) not in support_set
    ]
    loads = all_loads(n, support, bad)
    results = []
    with ProcessPoolExecutor(max_workers=min(60, len(seeds))) as pool:
        futures = [
            pool.submit(search_seed, (seed, n, support, bad, loads))
            for seed in seeds
        ]
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                results.append(result)
    results.sort(key=lambda row: (len(row["offSupport"]), row["seed"]))
    print(json.dumps({
        "g6": encoded,
        "N": n,
        "m": len(bad),
        "candidateSeeds": len(seeds),
        "activeWitnesses": len(results),
        "negativeActiveHall": sum(
            Fraction(row["activePartition"]["hallMargin"]) < 0 for row in results
        ),
        "first": results[:10],
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
