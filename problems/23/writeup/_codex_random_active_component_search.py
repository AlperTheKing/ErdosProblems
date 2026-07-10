"""Random exact search for an active internal off-support component.

Random connected bipartite support graphs are passed through the existing
exact local-obstruction DFS.  Every returned atom family is upgraded from the
necessary no-private-edge test to the exact minimal Hall-circuit test via
matchings after each single-atom deletion.  We then search every selected atom
for a simple off-support-only path of even length at least six, validating at
every extension that triangle-freeness, distance four, and every full support
remain unchanged.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed

import _claude_d3_local_obstruction as d3
import _codex_internal_offsupport_gate as gate
import _codex_k4_subdivision_obstruction_search as g6util


def connected(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    seen = {0}
    queue = deque([0])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return len(seen) == n


def random_support(rng, m):
    e = m - 1
    for _ in range(100):
        n = rng.randint(max(7, int((4 * e) ** 0.5) + 1), min(e + 1, 20))
        left = rng.randint(2, n - 2)
        candidates = [(u, v) for u in range(left) for v in range(left, n)]
        if len(candidates) < e:
            continue
        edges = sorted(rng.sample(candidates, e))
        if connected(n, edges):
            return n, edges
    return None


def has_saturating_matching(supports, skip, edge_count):
    match = [-1] * edge_count

    def augment(a, seen):
        mask = supports[a]
        while mask:
            bit = mask & -mask
            e = bit.bit_length() - 1
            mask ^= bit
            if seen[e]:
                continue
            seen[e] = True
            if match[e] < 0 or augment(match[e], seen):
                match[e] = a
                return True
        return False

    for a in range(len(supports)):
        if a == skip:
            continue
        if not augment(a, [False] * edge_count):
            return False
    return True


def exact_minimal_circuit(supports, edge_count):
    return len(supports) == edge_count + 1 and all(
        has_saturating_matching(supports, skip, edge_count)
        for skip in range(len(supports))
    )


def active_path(n, support, bad, node_cap=200_000):
    adj = [set() for _ in range(n)]
    for u, v in support:
        adj[u].add(v)
        adj[v].add(u)
    colours = gate.bipartition(adj)
    support_set = set(support)
    candidate = [set() for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            if colours[u] != colours[v] and (u, v) not in support_set:
                candidate[u].add(v)
                candidate[v].add(u)

    nodes = 0
    for a, b in bad:
        for length in range(6, n, 2):
            path = [a]
            used = {a}

            def extend(x, remaining):
                nonlocal nodes
                nodes += 1
                if nodes > node_cap:
                    return "cap"
                if remaining == 0:
                    return tuple(path) if x == b else None
                for y in candidate[x]:
                    if y in used or (remaining == 1 and y != b):
                        continue
                    used.add(y)
                    path.append(y)
                    off = {
                        tuple(sorted((path[i], path[i + 1])))
                        for i in range(len(path) - 1)
                    }
                    result = None
                    if gate.valid_offsupport_set(n, support, bad, off):
                        result = extend(y, remaining - 1)
                    if result is not None:
                        return result
                    path.pop()
                    used.remove(y)
                return None

            result = extend(a, length)
            if result == "cap":
                return None, nodes, True
            if result is not None:
                return {"badEdge": [a, b], "path": list(result)}, nodes, False
    return None, nodes, False


def worker(task):
    seed, trials, mlo, mhi = task
    rng = random.Random(seed)
    d3.NODE_CAP = 5_000_000
    stats = {"supports": 0, "localAborts": 0, "localWitnesses": 0,
             "minimalCircuits": 0, "pathCaps": 0}
    for _ in range(trials):
        m = rng.randint(mlo, mhi)
        generated = random_support(rng, m)
        if generated is None:
            continue
        n, edges = generated
        stats["supports"] += 1
        encoded = g6util.graph6(n, edges)
        witness, aborted, _pairs = d3.check_F((encoded,))
        if aborted:
            stats["localAborts"] += 1
            continue
        if witness is None:
            continue
        stats["localWitnesses"] += 1
        bad = [tuple(pair) for pair, _mask in witness[1]]
        supports = [mask for _pair, mask in witness[1]]
        if not exact_minimal_circuit(supports, len(edges)):
            continue
        stats["minimalCircuits"] += 1
        path, nodes, capped = active_path(n, edges, bad)
        stats["pathCaps"] += int(capped)
        if path is not None:
            assert gate.valid_offsupport_set(
                n, edges, bad,
                {tuple(sorted((path["path"][i], path["path"][i + 1])))
                 for i in range(len(path["path"]) - 1)},
            )
            return {"seed": seed, "m": m, "n": n, "g6": encoded,
                    "support": edges, "atoms": bad, "active": path,
                    "searchNodes": nodes, "stats": stats}
    return {"seed": seed, "stats": stats}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=60)
    parser.add_argument("--trials-per-worker", type=int, default=100)
    parser.add_argument("--mlo", type=int, default=16)
    parser.add_argument("--mhi", type=int, default=28)
    args = parser.parse_args()
    tasks = [(10_000 + i, args.trials_per_worker, args.mlo, args.mhi)
             for i in range(args.workers)]
    totals = {"supports": 0, "localAborts": 0, "localWitnesses": 0,
              "minimalCircuits": 0, "pathCaps": 0}
    first = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(worker, task) for task in tasks]
        for future in as_completed(futures):
            row = future.result()
            for key in totals:
                totals[key] += row["stats"][key]
            if "active" in row and first is None:
                first = row
                for pending in futures:
                    pending.cancel()
    print(json.dumps({"workers": args.workers,
                      "trialsPerWorker": args.trials_per_worker,
                      "mRange": [args.mlo, args.mhi],
                      "totals": totals, "first": first},
                     sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
