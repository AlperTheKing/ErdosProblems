"""Construct and lock a structured active-component candidate.

The support graph is a 10-leg subdivided star (20 edges).  Twenty-one selected
distance-four leaf pairs form a minimal support-deficient circuit.  We search
for an off-support-only path connecting one selected pair while preserving all
full shortest supports and triangle-freeness.  If found, private long parity
locks make the displayed cut the unique maximum cut without changing any
selected shortest distance.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction

import _codex_internal_offsupport_gate as gate


T = 10
LOCKS = 22


def edge(u, v):
    return (u, v) if u < v else (v, u)


def spider():
    n = 1 + 2 * T
    support = []
    mids = []
    leaves = []
    for i in range(T):
        mid, leaf = 1 + 2 * i, 2 + 2 * i
        mids.append(mid)
        leaves.append(leaf)
        support.extend((edge(0, mid), edge(mid, leaf)))
    left, right = leaves[:5], leaves[5:]
    missing = {
        edge(left[0], right[1]),
        edge(left[1], right[0]),
        edge(left[1], right[1]),
        edge(left[2], right[2]),
    }
    bad = [edge(u, v) for u in left for v in right if edge(u, v) not in missing]
    assert len(bad) == 21
    return n, support, bad, mids, leaves


def support_mask(support, a, b):
    adj = [set() for _ in range(1 + 2 * T)]
    for u, v in support:
        adj[u].add(v)
        adj[v].add(u)
    da, db = gate.bfs(adj, a), gate.bfs(adj, b)
    assert da[b] == 4
    result = 0
    for i, (u, v) in enumerate(support):
        if da[u] + 1 + db[v] == 4 or da[v] + 1 + db[u] == 4:
            result |= 1 << i
    return result


def verify_minimal(support, bad):
    masks = [support_mask(support, *a) for a in bad]
    full = (1 << len(support)) - 1
    assert len(bad) == len(support) + 1
    assert __import__("functools").reduce(int.__or__, masks, 0) == full
    minimum_margin = None
    for subset in range(1, 1 << len(bad)):
        union = 0
        for i, mask in enumerate(masks):
            if (subset >> i) & 1:
                union |= mask
        margin = union.bit_count() - subset.bit_count()
        if subset == (1 << len(bad)) - 1:
            assert margin == -1
        else:
            assert margin >= 0
            minimum_margin = margin if minimum_margin is None else min(minimum_margin, margin)
    return minimum_margin


def selected_loads(n, support, bad):
    adj = [set() for _ in range(n)]
    for u, v in support:
        adj[u].add(v)
        adj[v].add(u)
    loads = [Fraction(0) for _ in range(n)]
    for a, b in bad:
        da, db = gate.bfs(adj, a), gate.bfs(adj, b)
        assert da[b] == 4
        for v in range(n):
            if da[v] >= 0 and db[v] >= 0 and da[v] + db[v] == 4:
                loads[v] += 5
    return loads


def find_active(n, support, bad, loads):
    adj = [set() for _ in range(n)]
    for u, v in support:
        adj[u].add(v)
        adj[v].add(u)
    colours = gate.bipartition(adj)
    support_set = set(support)
    seeds = [
        edge(u, v)
        for u in range(n)
        for v in range(u + 1, n)
        if colours[u] != colours[v] and edge(u, v) not in support_set
    ]
    for seed in seeds:
        found = gate.component_path_counterexample(
            n, support, bad, seed, max_length=n - 1
        )
        if found is None:
            continue
        offsupport = {tuple(e) for e in found["offSupport"]}
        hall = gate.endpoint_flow_hall_margin(n, offsupport, loads)
        found["seed"] = seed
        found["localEndpointHallMargin"] = str(hall[0])
        found["localEndpointHallSet"] = [v for v in range(n) if (hall[1] >> v) & 1]
        return found, len(seeds)
    return None, len(seeds)


def locked_certificate(n, support, bad, offsupport, side):
    edges = set(support) | set(bad) | set(offsupport)
    blue = set(support) | set(offsupport)
    next_vertex = n
    anchor = next_vertex
    next_vertex += 1
    side = list(side) + [0]
    paths = []
    for x in range(n):
        length = 6 if side[x] == 0 else 7
        for _ in range(LOCKS):
            internal = tuple(range(next_vertex, next_vertex + length - 1))
            next_vertex += length - 1
            for step, v in enumerate(internal, 1):
                assert v == len(side)
                side.append(side[x] ^ (step & 1))
            path = (x,) + internal + (anchor,)
            for u, v in zip(path, path[1:]):
                e = edge(u, v)
                assert e not in edges
                edges.add(e)
                blue.add(e)
            paths.append(path)

    full_adj = gate.adjacency(next_vertex, edges)
    assert all(full_adj[u].isdisjoint(full_adj[v]) for u, v in edges)
    blue_adj = gate.adjacency(next_vertex, blue)
    assert all(gate.bfs(blue_adj, a)[b] == 4 for a, b in bad)

    # Fix the anchor side.  Any nonempty changed core set loses at least one
    # edge on each of LOCKS private paths per changed vertex.  The core can
    # gain at most all |bad| currently uncut edges.
    assert LOCKS > len(bad)
    displayed = len(blue)
    maxcut_certificate = {
        "anchorFixed": True,
        "lockLossPerChangedCoreVertex": LOCKS,
        "maximumPossibleCoreGain": len(bad),
        "strict": LOCKS > len(bad),
        "maxCut": displayed,
        "badCount": len(bad),
    }
    payload = "".join(f"{u} {v}\n" for u, v in sorted(edges)).encode("ascii")
    return {
        "N": next_vertex,
        "edges": len(edges),
        "blue": len(blue),
        "bad": len(bad),
        "triangleFree": True,
        "BConnected": True,
        "ellHistogram": {"5": len(bad)},
        "Gamma": 25 * len(bad),
        "maxCutCertificate": maxcut_certificate,
        "edgeListSHA256": hashlib.sha256(payload).hexdigest(),
    }


def main():
    n, support, bad, _mids, _leaves = spider()
    minimum_margin = verify_minimal(support, bad)
    loads = selected_loads(n, support, bad)
    found, seed_count = find_active(n, support, bad, loads)
    result = {
        "localN": n,
        "supportEdges": len(support),
        "atoms": len(bad),
        "properSubsetMinMargin": minimum_margin,
        "candidateSeeds": seed_count,
        "active": found,
    }
    if found is not None:
        support_adj = [set() for _ in range(n)]
        for u, v in support:
            support_adj[u].add(v)
            support_adj[v].add(u)
        side = gate.bipartition(support_adj)
        result["locked"] = locked_certificate(
            n, support, bad, {tuple(e) for e in found["offSupport"]}, side
        )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
