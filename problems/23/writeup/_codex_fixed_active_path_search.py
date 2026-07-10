"""Exact randomized search with an active off-support path forced in advance.

Each trial fixes an ell=5 atom x-y, a four-edge support path, and a disjoint
six-edge off-support path between x and y.  A random connected bipartite
support graph F is completed around those vertices.  Candidate atoms are all
distance-four pairs in B=F union I whose complete shortest support avoids I.
The exact DFS forces x-y, triangle-freeness, full double coverage of F, and
|A|=|F|+1; a matching after every atom deletion then verifies inclusion
minimality rather than merely the no-private-edge relaxation.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed

import _codex_internal_offsupport_gate as gate
from _codex_random_active_component_search import exact_minimal_circuit


def edge(u, v):
    return (u, v) if u < v else (v, u)


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


def candidates(n, F, I):
    B = sorted(set(F) | set(I))
    adj = [set() for _ in range(n)]
    for u, v in B:
        adj[u].add(v)
        adj[v].add(u)
    dist = [gate.bfs(adj, s) for s in range(n)]
    findex = {e: i for i, e in enumerate(F)}
    result = []
    for u in range(n):
        for v in range(u + 1, n):
            if dist[u][v] != 4:
                continue
            du, dv = dist[u], dist[v]
            support = {
                e for e in B
                if du[e[0]] + 1 + dv[e[1]] == 4
                or du[e[1]] + 1 + dv[e[0]] == 4
            }
            if support & set(I):
                continue
            mask = 0
            for e in support:
                mask |= 1 << findex[e]
            result.append(((u, v), mask))
    return result


def select_circuit(n, F, I, forced, node_cap=2_000_000):
    pairs = candidates(n, F, I)
    ecount = len(F)
    target = ecount + 1
    forced_index = next((i for i, (pair, _s) in enumerate(pairs) if pair == forced), None)
    if forced_index is None or len(pairs) < target:
        return None, 0, False
    forced_pair = pairs.pop(forced_index)
    pairs.sort(key=lambda row: (-row[1].bit_count(), row[0]))
    full = (1 << ecount) - 1
    if forced_pair[1] | __import__("functools").reduce(int.__or__, (s for _, s in pairs), 0) != full:
        return None, 0, False

    availability = [[0] * ecount for _ in range(len(pairs) + 1)]
    for i in range(len(pairs) - 1, -1, -1):
        mask = pairs[i][1]
        for j in range(ecount):
            availability[i][j] = availability[i + 1][j] + ((mask >> j) & 1)

    mult = [((forced_pair[1] >> j) & 1) for j in range(ecount)]
    nb = {forced[0]: {forced[1]}, forced[1]: {forced[0]}}
    chosen = [forced_pair]
    nodes = 0
    capped = False

    def dfs(i, need):
        nonlocal nodes, capped
        nodes += 1
        if nodes > node_cap:
            capped = True
            return None
        if need == 0:
            if all(x >= 2 for x in mult):
                return list(chosen)
            return None
        if len(pairs) - i < need:
            return None
        for j in range(ecount):
            if mult[j] + availability[i][j] < 2:
                return None
        (u, v), mask = pairs[i]
        if not (nb.get(u, set()) & nb.get(v, set())):
            nb.setdefault(u, set()).add(v)
            nb.setdefault(v, set()).add(u)
            bits = mask
            while bits:
                bit = bits & -bits
                mult[bit.bit_length() - 1] += 1
                bits ^= bit
            chosen.append(pairs[i])
            got = dfs(i + 1, need - 1)
            if got is not None:
                return got
            chosen.pop()
            bits = mask
            while bits:
                bit = bits & -bits
                mult[bit.bit_length() - 1] -= 1
                bits ^= bit
            nb[u].remove(v)
            nb[v].remove(u)
        return dfs(i + 1, need)

    result = dfs(0, target - 1)
    if result is None:
        return None, nodes, capped
    supports = [mask for _pair, mask in result]
    if not exact_minimal_circuit(supports, ecount):
        return None, nodes, capped
    bad = [pair for pair, _mask in result]
    assert gate.valid_offsupport_set(n, F, bad, set(I))
    return result, nodes, capped


def trial(rng):
    # Side 0 is 0..left-1; side 1 is left..n-1.
    left = rng.randint(6, 10)
    right = rng.randint(6, 10)
    n = left + right
    x, y = 0, 1
    side0 = list(range(left))
    side1 = list(range(left, n))
    # P4: x-a-b-c-y.
    a, b, c = side1[0], side0[2], side1[1]
    p4 = {edge(x, a), edge(a, b), edge(b, c), edge(c, y)}
    # I6: x-r1-r2-r3-r4-r5-y, disjoint from P4 internally.
    r1, r2, r3, r4, r5 = side1[2], side0[3], side1[3], side0[4], side1[4]
    I = {edge(x, r1), edge(r1, r2), edge(r2, r3),
         edge(r3, r4), edge(r4, r5), edge(r5, y)}
    all_cross = {edge(u, v) for u in side0 for v in side1}
    available = sorted(all_cross - I - p4)
    max_e = min(len(all_cross - I), n + 5, 28)
    min_e = max(n - 1, 10)
    if min_e > max_e:
        return None
    ecount = rng.randint(min_e, max_e)
    for _ in range(200):
        F = sorted(p4 | set(rng.sample(available, ecount - len(p4))))
        if connected(n, F) and any(pair == (x, y) for pair, _ in candidates(n, F, I)):
            return n, F, sorted(I), (x, y)
    return None


def worker(task):
    seed, count = task
    rng = random.Random(seed)
    stats = {"trials": 0, "circuitCaps": 0}
    for _ in range(count):
        generated = trial(rng)
        if generated is None:
            continue
        stats["trials"] += 1
        n, F, I, forced = generated
        circuit, nodes, capped = select_circuit(n, F, I, forced)
        stats["circuitCaps"] += int(capped)
        if circuit is not None:
            return {"seed": seed, "n": n, "support": F, "offSupport": I,
                    "forcedAtom": forced,
                    "atoms": [list(pair) for pair, _mask in circuit],
                    "supportMasks": [mask for _pair, mask in circuit],
                    "searchNodes": nodes, "stats": stats}
    return {"seed": seed, "stats": stats}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=60)
    parser.add_argument("--trials-per-worker", type=int, default=200)
    args = parser.parse_args()
    totals = {"trials": 0, "circuitCaps": 0}
    first = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(worker, (50_000 + i, args.trials_per_worker))
                   for i in range(args.workers)]
        for future in as_completed(futures):
            row = future.result()
            for key in totals:
                totals[key] += row["stats"][key]
            if "atoms" in row and first is None:
                first = row
                for pending in futures:
                    pending.cancel()
    print(json.dumps({"workers": args.workers,
                      "trialsPerWorker": args.trials_per_worker,
                      "totals": totals, "first": first},
                     sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
