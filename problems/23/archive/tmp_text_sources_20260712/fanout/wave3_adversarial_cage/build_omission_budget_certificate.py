#!/usr/bin/env python3
"""Extract a small omission-budget triangle obstruction from each support."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
V, M, A, B = 0, 1, 2, 3


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def all_distances(n: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    result = []
    for source in range(n):
        distance = [-1] * n
        distance[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                if distance[v] < 0:
                    distance[v] = distance[u] + 1
                    queue.append(v)
        result.append(distance)
    return result


def key(atom: tuple[str, int, int]) -> list[object]:
    return [atom[0], atom[1], atom[2]]


def support_atoms(record: dict) -> set[tuple[str, int, int]]:
    left, right = record["left"], record["right"]
    distance = all_distances(
        left + right, [tuple(edge) for edge in record["supportEdgesGlobal"]]
    )
    atoms = set()
    for shore, vertices in (("L", range(left)), ("R", range(left, left + right))):
        for u, v in itertools.combinations(vertices, 2):
            if distance[u][v] == 4:
                atoms.add((shore, u, v))
    return atoms


def owner_neighbours(atoms: set[tuple[str, int, int]], owner: int) -> list[int]:
    out = []
    for shore, u, v in atoms:
        if shore == "L" and owner in (u, v):
            out.append(v if u == owner else u)
    return sorted(out)


def all_atom_triangles(atoms, left: int, n: int):
    triangles = []
    for shore, vertices in (("L", range(left)), ("R", range(left, n))):
        for u, v, w in itertools.combinations(vertices, 3):
            triangle = ((shore, u, v), (shore, u, w), (shore, v, w))
            if all(atom in atoms for atom in triangle):
                triangles.append(triangle)
    return triangles


def analyze(record: dict) -> dict:
    left, right = record["left"], record["right"]
    atoms = support_atoms(record)
    root = ("L", A, B)
    omission_budget = len(atoms) - 25
    neighbours = {owner: owner_neighbours(atoms, owner) for owner in (V, M)}
    base = {
        "split": [left, right],
        "supportSha256": record["supportSha256"],
        "distanceFourAtomCount": len(atoms),
        "selectedAtomCount": 25,
        "omissionBudget": omission_budget,
        "rootAtom": key(root),
        "ownerDistanceFourNeighbours": {
            str(owner): neighbours[owner] for owner in (V, M)
        },
    }
    if omission_budget < 0 or root not in atoms:
        raise AssertionError(base)

    common = sorted(set(neighbours[V]) & set(neighbours[M]))
    twin_five = neighbours[V] == neighbours[M] and len(common) == 5
    completers = sorted(
        ("L", s, t)
        for s, t in itertools.combinations(common, 2)
        if ("L", s, t) in atoms
    )
    if twin_five and len(completers) > omission_budget:
        forced = sorted(
            {("L", min(owner, z), max(owner, z)) for owner in (V, M) for z in common}
            | {root}
        )
        base.update({
            "kind": "TWIN_OWNER_COMPLETER_PIGEONHOLE",
            "commonOwnerNeighbourSet": common,
            "forcedAtoms": [key(atom) for atom in forced],
            "triangleCompleters": [key(atom) for atom in completers],
            "completerCount": len(completers),
            "strictPigeonhole": True,
            "proof": (
                "bad-degree 5 forces both owner stars; every completer closes a "
                "triangle; deleting all completers exceeds the omission budget"
            ),
        })
        return base

    if omission_budget == 0:
        triangles = all_atom_triangles(atoms, left, left + right)
        if not triangles:
            raise AssertionError(base)
        triangle = triangles[0]
        base.update({
            "kind": "ZERO_OMISSION_TRIANGLE",
            "forcedAtoms": [key(atom) for atom in triangle],
            "triangle": [key(atom) for atom in triangle],
            "strictPigeonhole": True,
            "proof": "all 25 available atoms are selected, including this triangle",
        })
        return base
    raise AssertionError({**base, "completers": [key(atom) for atom in completers]})


def main() -> None:
    source_path = HERE / "first_supports.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    result = {
        "schema": "wave3-t5-omission-budget-certificate-v1",
        "classStatement": {
            "twinOwnerClass": (
                "If a support has N distance-four atoms, two bad-degree-five owners "
                "with the same only five atom-neighbours S, and more than N-25 "
                "distance-four atoms internal to S, no triangle-free 25-atom "
                "selection exists."
            ),
            "zeroOmissionClass": (
                "If a support has exactly 25 distance-four atoms and their atom graph "
                "contains a triangle, no triangle-free 25-atom selection exists."
            ),
            "productionConsequence": (
                "An intrinsic triangle excludes all ambient extensions, maximum cuts, "
                "active scopes, second owners, matchings, positive defects, and ledgers."
            ),
        },
        "source": {"path": source_path.name, "sha256": sha256_file(source_path)},
        "certificates": [analyze(record) for record in source["supports"]],
    }
    result["canonicalSha256"] = canonical_sha(result)
    output = HERE / "omission_budget_certificate.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
