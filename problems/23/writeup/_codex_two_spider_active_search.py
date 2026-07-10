"""Structured 2-sum stress test for NO-ACTIVE-COMPONENT.

Two exact 19-atom/18-support subdivided-star circuits share one selected bad
atom and its endpoints.  Their support edges are otherwise disjoint, so the
union is an exact 37/36 minimal Hall circuit.  Cross-gadget off-support edges
are then searched for a jointly valid path joining the shared atom endpoints.
"""

from __future__ import annotations

import json
from collections import deque

import _codex_internal_offsupport_gate as gate
import _codex_random_active_component_search as random_gate


def edge(u, v):
    return (u, v) if u < v else (v, u)


def add_spider(next_vertex, shared_u, shared_v, removed_pair):
    center = next_vertex
    next_vertex += 1
    leaves = [shared_u, shared_v]
    leaves.extend(range(next_vertex, next_vertex + 7))
    next_vertex += 7
    mids = list(range(next_vertex, next_vertex + 9))
    next_vertex += 9
    support = []
    for mid, leaf in zip(mids, leaves):
        support.extend((edge(center, mid), edge(mid, leaf)))
    left = [leaves[0], leaves[2], leaves[3], leaves[4]]
    right = [leaves[1], leaves[5], leaves[6], leaves[7], leaves[8]]
    bad = [
        edge(u, v)
        for u in left
        for v in right
        if edge(u, v) != edge(left[removed_pair[0]], right[removed_pair[1]])
    ]
    assert edge(shared_u, shared_v) in bad
    assert len(support) == 18 and len(bad) == 19
    return next_vertex, support, bad


def incidence_masks(n, support, atoms):
    adj = [set() for _ in range(n)]
    for u, v in support:
        adj[u].add(v)
        adj[v].add(u)
    masks = []
    for a, b in atoms:
        da, db = gate.bfs(adj, a), gate.bfs(adj, b)
        assert da[b] == 4
        mask = 0
        for i, (u, v) in enumerate(support):
            if da[u] + 1 + db[v] == 4 or da[v] + 1 + db[u] == 4:
                mask |= 1 << i
        masks.append(mask)
    return masks


def individually_safe_graph(n, support, atoms):
    adj = [set() for _ in range(n)]
    colour_adj = [set() for _ in range(n)]
    for u, v in support:
        colour_adj[u].add(v)
        colour_adj[v].add(u)
    colour = gate.bipartition(colour_adj)
    support_set = set(support)
    for u in range(n):
        for v in range(u + 1, n):
            e = edge(u, v)
            if colour[u] != colour[v] and e not in support_set:
                if gate.valid_offsupport_set(n, support, atoms, {e}):
                    adj[u].add(v)
                    adj[v].add(u)
    return adj


def shortest_path(adj, source, target):
    parent = {source: None}
    queue = deque([source])
    while queue:
        x = queue.popleft()
        if x == target:
            path = []
            while x is not None:
                path.append(x)
                x = parent[x]
            return list(reversed(path))
        for y in adj[x]:
            if y not in parent:
                parent[y] = x
                queue.append(y)
    return None


def instance(removed1, removed2):
    shared_u, shared_v = 0, 1
    next_vertex = 2
    next_vertex, support1, bad1 = add_spider(
        next_vertex, shared_u, shared_v, removed1)
    next_vertex, support2, bad2 = add_spider(
        next_vertex, shared_u, shared_v, removed2)
    support = support1 + support2
    atoms = sorted(set(bad1) | set(bad2))
    masks = incidence_masks(next_vertex, support, atoms)
    assert len(support) == 36 and len(atoms) == 37
    assert random_gate.exact_minimal_circuit(masks, len(support))
    candidate = individually_safe_graph(next_vertex, support, atoms)
    prefilter_path = shortest_path(candidate, shared_u, shared_v)
    exact = gate.component_path_counterexample(
        next_vertex,
        support,
        atoms,
        (shared_u, next(iter(candidate[shared_u]), shared_v)),
        max_length=next_vertex - 1,
    ) if candidate[shared_u] else None
    return {
        "removed": [removed1, removed2],
        "n": next_vertex,
        "supportEdges": len(support),
        "atoms": len(atoms),
        "minimalCircuit": True,
        "candidateEdges": sum(map(len, candidate)) // 2,
        "sharedEndpointDegrees": [len(candidate[shared_u]), len(candidate[shared_v])],
        "prefilterPath": prefilter_path,
        "jointActive": exact,
    }


def main():
    choices = [
        (i, j)
        for i in range(4)
        for j in range(5)
        if (i, j) != (0, 0)
    ]
    rows = []
    for removed1 in choices:
        for removed2 in choices:
            rows.append(instance(removed1, removed2))
    first_candidate = next(
        (row for row in rows if row["candidateEdges"]), None)
    first_prefilter = next(
        (row for row in rows if row["prefilterPath"] is not None), None)
    first_joint = next(
        (row for row in rows if row["jointActive"] is not None), None)
    print(json.dumps({
        "instances": len(rows),
        "withCandidateEdges": sum(bool(row["candidateEdges"]) for row in rows),
        "withPrefilterPath": sum(row["prefilterPath"] is not None for row in rows),
        "withJointActive": sum(row["jointActive"] is not None for row in rows),
        "firstCandidate": first_candidate,
        "firstPrefilter": first_prefilter,
        "firstJoint": first_joint,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
