"""Exact verifier for the active minimal-circuit near-closure falsifier."""

from __future__ import annotations

import hashlib
import json
from collections import deque
from pathlib import Path


ARTIFACT = Path("tmp/codex_near_closure_bounded_991000.json")
ARTIFACT_SHA256 = (
    "9E7A0744B7DDC970265CD7249E8EA6E9FCEDD04003302E3102E45DBEE8E6F147"
)


def edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def distances(n: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    result = []
    for source in range(n):
        row = [-1] * n
        row[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if row[v] < 0:
                    row[v] = row[u] + 1
                    queue.append(v)
        result.append(row)
    return result


def support_mask(
        support: list[tuple[int, int]], dist: list[list[int]],
        atom: tuple[int, int]) -> int:
    a, b = atom
    assert dist[a][b] == 4
    mask = 0
    for index, (u, v) in enumerate(support):
        if (dist[a][u] + 1 + dist[v][b] == 4 or
                dist[a][v] + 1 + dist[u][b] == 4):
            mask |= 1 << index
    return mask


def has_perfect_matching_after_delete(
        masks: list[int], deleted: int, edge_count: int) -> bool:
    owner = [-1] * edge_count

    def augment(atom: int, seen: list[bool]) -> bool:
        mask = masks[atom]
        while mask:
            bit = mask & -mask
            index = bit.bit_length() - 1
            mask ^= bit
            if seen[index]:
                continue
            seen[index] = True
            if owner[index] < 0 or augment(owner[index], seen):
                owner[index] = atom
                return True
        return False

    return all(
        atom == deleted or augment(atom, [False] * edge_count)
        for atom in range(len(masks))
    )


def verify_triangle_free(
        n: int, graph_edges: list[tuple[int, int]]) -> None:
    adj = [set() for _ in range(n)]
    for u, v in graph_edges:
        assert v not in adj[u]
        adj[u].add(v)
        adj[v].add(u)
    assert all(not (adj[u] & adj[v]) for u, v in graph_edges)


def main() -> None:
    raw = ARTIFACT.read_bytes()
    assert hashlib.sha256(raw).hexdigest().upper() == ARTIFACT_SHA256
    batch = json.loads(raw)
    row = batch["first"]
    n = row["n"]
    support = [edge(*pair) for pair in row["support"]]
    atoms = [edge(*pair) for pair in row["atoms"]]
    path = row["forcedPath"]
    forced_atom = edge(*row["forcedAtom"])
    path_edges = [edge(path[i], path[i + 1]) for i in range(len(path) - 1)]

    assert n == 45
    assert len(support) == 48
    assert len(atoms) == 49
    assert forced_atom in atoms
    assert len(path_edges) == 6
    assert not (set(path_edges) & set(support))

    support_dist = distances(n, support)
    masks = [support_mask(support, support_dist, atom) for atom in atoms]
    assert all(mask for mask in masks)
    assert all(
        has_perfect_matching_after_delete(masks, deleted, len(support))
        for deleted in range(len(atoms))
    )

    blue = support + path_edges
    verify_triangle_free(n, blue + atoms)
    blue_dist = distances(n, blue)
    assert all(blue_dist[a][b] == 4 for a, b in atoms)
    for a, b in atoms:
        for u, v in path_edges:
            assert blue_dist[a][u] + 1 + blue_dist[v][b] != 4
            assert blue_dist[a][v] + 1 + blue_dist[u][b] != 4

    near = edge(path[1], path[-2])
    assert support_dist[near[0]][near[1]] == 4
    near_mask = support_mask(support, support_dist, near)
    owners = [
        {atom for atom, mask in enumerate(masks) if (mask >> index) & 1}
        for index in range(len(support))
    ]
    near_atoms = set().union(*(
        owners[index]
        for index in range(len(support))
        if (near_mask >> index) & 1
    ))
    closed_edges = {
        index for index, edge_owners in enumerate(owners)
        if edge_owners and edge_owners <= near_atoms
    }
    closed_atoms = set().union(*(owners[index] for index in closed_edges))
    assert closed_atoms == near_atoms
    assert len(closed_atoms) > len(closed_edges)

    output = {
        "artifactSha256": ARTIFACT_SHA256,
        "n": n,
        "atomCount": len(atoms),
        "supportCount": len(support),
        "forcedAtom": list(forced_atom),
        "forcedPath": path,
        "nearPair": list(near),
        "nearCorridorEdges": near_mask.bit_count(),
        "nearIncidentAtoms": len(near_atoms),
        "closedAtoms": len(closed_atoms),
        "closedEdges": len(closed_edges),
        "closureDeficiency": len(closed_atoms) - len(closed_edges),
        "exactMinimalCircuit": True,
        "triangleFreeWithDetour": True,
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
