"""Independent exact verifier for an active-path nonminimal double cover.

The payload is not a counterexample to NO-ACTIVE-COMPONENT: it deliberately
fails inclusion-minimal Hall.  Its purpose is to expose the structure that a
proof must rule out.  All checks use finite sets, integer distances, and exact
matching/Hall arithmetic.
"""

from __future__ import annotations

import hashlib
import json
from collections import deque
from pathlib import Path

import _codex_internal_offsupport_gate as gate
from _codex_safe_p4_cpsat_search import edge, support_mask


ROOT = Path(__file__).resolve().parents[3]
PAYLOAD = ROOT / "tmp" / "codex_active_nonminimal_witness_locked.json"


def union_mask(masks, indices):
    result = 0
    for index in indices:
        result |= masks[index]
    return result


def shrink_deficient(masks, indices, required):
    current = list(indices)
    changed = True
    while changed:
        changed = False
        for index in list(current):
            if index == required:
                continue
            candidate = [other for other in current if other != index]
            if union_mask(masks, candidate).bit_count() < len(candidate):
                current = candidate
                changed = True
                break
    return current


def restricted_distance(n, edges, source, target):
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    distance = [-1] * n
    distance[source] = 0
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in adjacency[u]:
            if distance[v] < 0:
                distance[v] = distance[u] + 1
                queue.append(v)
    return distance[target]


def saturating_matching(left_atoms, right_edges, masks):
    right_set = set(right_edges)
    owner = {}

    def augment(atom, seen):
        mask = masks[atom]
        for support_index in sorted(right_set):
            if not ((mask >> support_index) & 1) or support_index in seen:
                continue
            seen.add(support_index)
            if support_index not in owner or augment(owner[support_index], seen):
                owner[support_index] = atom
                return True
        return False

    for atom in sorted(left_atoms):
        if not augment(atom, set()):
            return None
    return {atom: edge for edge, atom in owner.items()}


def cut_labels_from_tree(n, support, cut_edge_indices):
    adjacency = [set() for _ in range(n)]
    edge_index = {}
    for index, (u, v) in enumerate(support):
        adjacency[u].add(v)
        adjacency[v].add(u)
        edge_index[edge(u, v)] = index
    labels = [None] * n
    for root in range(n):
        if labels[root] is not None:
            continue
        labels[root] = 0
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                expected = labels[u] ^ (
                    edge_index[edge(u, v)] in cut_edge_indices)
                if labels[v] is None:
                    labels[v] = expected
                    queue.append(v)
                elif labels[v] != expected:
                    return None
    return labels


def components_after_removing(n, edges, removed):
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        if edge(u, v) in removed:
            continue
        adjacency[u].add(v)
        adjacency[v].add(u)
    component = [-1] * n
    next_component = 0
    for root in range(n):
        if component[root] >= 0:
            continue
        component[root] = next_component
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                if component[v] < 0:
                    component[v] = next_component
                    queue.append(v)
        next_component += 1
    return component


def main():
    raw = PAYLOAD.read_bytes()
    data = json.loads(raw)
    n = data["n"]
    support = [tuple(item) for item in data["support"]]
    atoms = [tuple(item) for item in data["selectedAtoms"]]
    path = data["forcedPath"]
    forced_atom = tuple(data["forcedAtom"])
    hall = data["hallWitness"]

    adjacency, distances = [], []
    support_adjacency = [set() for _ in range(n)]
    for u, v in support:
        support_adjacency[u].add(v)
        support_adjacency[v].add(u)
    distances = [gate.bfs(support_adjacency, source) for source in range(n)]
    colours = gate.bipartition(support_adjacency)
    assert colours is not None
    assert len(support) + 1 == len(atoms)

    path_edges = {
        edge(path[index], path[index + 1])
        for index in range(len(path) - 1)
    }
    assert len(path_edges) == len(path) - 1
    assert not path_edges.intersection(support)
    assert forced_atom in atoms
    assert path[0] in forced_atom and path[-1] in forced_atom
    assert gate.valid_offsupport_set(n, support, atoms, path_edges)

    masks = [support_mask(support, distances, atom) for atom in atoms]
    assert all(distances[u][v] == 4 for u, v in atoms)
    assert union_mask(masks, range(len(masks))) == (1 << len(support)) - 1
    multiplicities = [
        sum((mask >> support_index) & 1 for mask in masks)
        for support_index in range(len(support))
    ]
    assert min(multiplicities) >= 2

    left = hall["left"]
    right = hall["right"]
    left_union = union_mask(masks, left)
    asserted_right = sum(1 << index for index in right)
    assert left_union == asserted_right
    assert len(left) == len(right) + 1
    assert len(left) < len(atoms)
    forced_index = atoms.index(forced_atom)
    assert forced_index in left

    minimal_left = shrink_deficient(masks, left, forced_index)
    minimal_union = union_mask(masks, minimal_left)
    assert minimal_union.bit_count() < len(minimal_left)
    assert all(
        union_mask(masks, [i for i in minimal_left if i != index]).bit_count()
        >= len(minimal_left) - 1
        for index in minimal_left
        if index != forced_index
    )

    left_set = set(left)
    right_set = set(right)
    complement_atoms = [i for i in range(len(atoms)) if i not in left_set]
    complement_edges = [i for i in range(len(support)) if i not in right_set]
    assert len(complement_atoms) == len(complement_edges)
    assert all(
        not (masks[index] & sum(1 << edge_index for edge_index in complement_edges))
        for index in left
    )

    first_internal = path[1]
    last_internal = path[-2]
    complement_support = [support[index] for index in complement_edges]
    complement_distance = restricted_distance(
        n, complement_support, first_internal, last_internal)
    assert complement_distance == 4

    near_pair = (first_internal, last_internal)
    assert distances[first_internal][last_internal] == 4
    near_mask = support_mask(support, distances, near_pair)
    edge_atoms = [
        {index for index, mask in enumerate(masks) if (mask >> edge_index) & 1}
        for edge_index in range(len(support))
    ]
    near_atoms = set()
    for edge_index in range(len(support)):
        if (near_mask >> edge_index) & 1:
            near_atoms.update(edge_atoms[edge_index])
    neighborhood_closed_edges = {
        edge_index
        for edge_index, owners in enumerate(edge_atoms)
        if owners and owners <= near_atoms
    }
    neighborhood_closed_atoms = set().union(
        *(edge_atoms[index] for index in neighborhood_closed_edges))
    assert neighborhood_closed_atoms == near_atoms
    complement_edge_set = set(complement_edges)
    closure_missing_edges = sorted(
        complement_edge_set - neighborhood_closed_edges)
    closure_excess_edges = sorted(
        neighborhood_closed_edges - complement_edge_set)
    near_matching = saturating_matching(
        near_atoms, neighborhood_closed_edges, masks)
    assert near_matching is not None
    cut_labels = cut_labels_from_tree(
        n, support, neighborhood_closed_edges)
    assert cut_labels is not None
    crossing_atoms = {
        index for index, (u, v) in enumerate(atoms)
        if cut_labels[u] != cut_labels[v]
    }
    crossing_path_edges = {
        edge(path[index], path[index + 1])
        for index in range(len(path) - 1)
        if cut_labels[path[index]] != cut_labels[path[index + 1]]
    }
    near_atom_profiles = []
    for index in sorted(near_atoms):
        near_atom_profiles.append({
            "atom": atoms[index],
            "corridorEdges": (masks[index] & near_mask).bit_count(),
            "closedEdges": sum(
                1 for edge_index in neighborhood_closed_edges
                if (masks[index] >> edge_index) & 1),
            "crossesCut": index in crossing_atoms,
        })
    closed_edge_pairs = {
        edge(*support[index]) for index in neighborhood_closed_edges
    }
    full_blue = support + sorted(path_edges)
    block_component = components_after_removing(
        n, full_blue, closed_edge_pairs)
    closed_edges_are_boundary = all(
        block_component[u] != block_component[v]
        for u, v in closed_edge_pairs
    )
    nonclosed_blue_internal = all(
        block_component[u] == block_component[v]
        for u, v in full_blue
        if edge(u, v) not in closed_edge_pairs
    )
    near_atoms_blocks_apart = all(
        block_component[atoms[index][0]] != block_component[atoms[index][1]]
        for index in near_atoms
    )
    all_apart_atoms = {
        index for index, (u, v) in enumerate(atoms)
        if block_component[u] != block_component[v]
    }
    all_same_atoms = set(range(len(atoms))) - all_apart_atoms
    all_same_support = union_mask(masks, all_same_atoms)
    path_vertex_atom_labels = []
    for vertex in path:
        labels = [
            index for index, (u, v) in enumerate(atoms)
            if distances[u][vertex] + distances[vertex][v] == 4
        ]
        path_vertex_atom_labels.append(labels)
    assert all(
        set(path_vertex_atom_labels[index]).isdisjoint(
            path_vertex_atom_labels[index + 1])
        for index in range(len(path) - 1)
    )

    report = {
        "activeAtom": list(forced_atom),
        "activePath": path,
        "atomCount": len(atoms),
        "supportCount": len(support),
        "minSupportMultiplicity": min(multiplicities),
        "hallLeft": len(left),
        "hallRight": len(right),
        "minimalLeftContainingActive": len(minimal_left),
        "minimalLeftSupport": minimal_union.bit_count(),
        "complementAtoms": len(complement_atoms),
        "complementEdges": len(complement_edges),
        "complementInternalDistance": complement_distance,
        "nearCorridorEdges": near_mask.bit_count(),
        "nearCorridorIncidentAtoms": len(near_atoms),
        "nearCorridorAtomList": [atoms[index] for index in sorted(near_atoms)],
        "neighborhoodClosedEdges": len(neighborhood_closed_edges),
        "neighborhoodClosedAtoms": len(neighborhood_closed_atoms),
        "neighborhoodClosedEdgeList": [
            support[index] for index in sorted(neighborhood_closed_edges)
        ],
        "nearAtomMatching": [
            {"atom": atoms[index], "edge": support[near_matching[index]]}
            for index in sorted(near_matching)
        ],
        "nearAtomProfiles": near_atom_profiles,
        "cutCrossingAtoms": len(crossing_atoms),
        "cutCrossingAtomsEqualNear": crossing_atoms == near_atoms,
        "cutCrossingPathEdges": sorted(crossing_path_edges),
        "blockComponentCount": len(set(block_component)),
        "closedEdgesAreBoundary": closed_edges_are_boundary,
        "nonclosedBlueInternal": nonclosed_blue_internal,
        "nearAtomsBlocksApart": near_atoms_blocks_apart,
        "allApartAtoms": len(all_apart_atoms),
        "allSameAtoms": len(all_same_atoms),
        "allSameSupport": all_same_support.bit_count(),
        "sameAtomsEqualHallLeft": all_same_atoms == set(left),
        "apartAtomsEqualHallComplement":
            all_apart_atoms == set(range(len(atoms))) - set(left),
        "closureMissingEdges": [support[index] for index in closure_missing_edges],
        "closureExcessEdges": [support[index] for index in closure_excess_edges],
        "pathVertexLabelCounts": [len(labels) for labels in path_vertex_atom_labels],
        "payloadSHA256": hashlib.sha256(raw).hexdigest(),
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
