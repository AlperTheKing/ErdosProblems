"""Probe metric invariants of canonical safe off-support components.

For random exact minimal ell=5 support circuits, build the graph of every
individually legal internal off-support edge.  The canonical no-active lemma
says each selected atom's endpoints lie in different components.  This probe
tests whether that separation follows from the elementary distance sign
relative to the atom endpoints, and reports the first obstruction to such a
short proof.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import deque

import _claude_d3_local_obstruction as d3
import _codex_internal_offsupport_gate as gate
import _codex_k4_subdivision_obstruction_search as g6util
import _codex_random_active_component_search as random_gate


def components(adj):
    comp = [-1] * len(adj)
    blocks = []
    for root in range(len(adj)):
        if comp[root] >= 0:
            continue
        cid = len(blocks)
        block = []
        comp[root] = cid
        queue = deque([root])
        while queue:
            x = queue.popleft()
            block.append(x)
            for y in adj[x]:
                if comp[y] < 0:
                    comp[y] = cid
                    queue.append(y)
        blocks.append(block)
    return comp, blocks


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


def component_diameter(adj, block):
    diameter = 0
    witness = None
    for source in block:
        distance = {source: 0}
        queue = deque([source])
        while queue:
            x = queue.popleft()
            for y in adj[x]:
                if y not in distance:
                    distance[y] = distance[x] + 1
                    queue.append(y)
        target = max(block, key=lambda v: distance[v])
        if distance[target] > diameter:
            diameter = distance[target]
            witness = [source, target]
    return diameter, witness


def atom_vertex_mask(n, support_adj, atom):
    a, b = atom
    da, db = gate.bfs(support_adj, a), gate.bfs(support_adj, b)
    assert da[b] == 4
    return sum(1 << v for v in range(n) if da[v] + db[v] == 4)


def explain_invalid(n, support, atoms, offsupport):
    blue_edges = support + sorted(offsupport)
    blue = [set() for _ in range(n)]
    full = [set() for _ in range(n)]
    for u, v in blue_edges:
        blue[u].add(v)
        blue[v].add(u)
        full[u].add(v)
        full[v].add(u)
    for u, v in atoms:
        full[u].add(v)
        full[v].add(u)
    for u in range(n):
        for v in full[u]:
            if u < v and full[u] & full[v]:
                return {
                    "kind": "triangle",
                    "edge": [u, v],
                    "common": min(full[u] & full[v]),
                }
    for atom_index, (a, b) in enumerate(atoms):
        da, db = gate.bfs(blue, a), gate.bfs(blue, b)
        if da[b] != 4:
            return {
                "kind": "distance",
                "atom": atom_index,
                "pair": [a, b],
                "distance": da[b],
            }
        for u, v in offsupport:
            if da[u] + 1 + db[v] == 4 or da[v] + 1 + db[u] == 4:
                return {
                    "kind": "newSupport",
                    "atom": atom_index,
                    "pair": [a, b],
                    "edge": [u, v],
                }
    return {"kind": "unknown"}


def inspect(n, support, atoms):
    support_adj = [set() for _ in range(n)]
    for u, v in support:
        support_adj[u].add(v)
        support_adj[v].add(u)
    colour = gate.bipartition(support_adj)
    assert colour is not None
    colour = gate.bipartition(support_adj)
    support_set = set(support)
    safe = [set() for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            edge = (u, v)
            if colour[u] == colour[v] or edge in support_set:
                continue
            if gate.valid_offsupport_set(n, support, atoms, {edge}):
                safe[u].add(v)
                safe[v].add(u)
    comp, blocks = components(safe)
    diameters = [component_diameter(safe, block) for block in blocks]
    max_diameter = max((row[0] for row in diameters), default=0)
    diameter_witness = next(
        (row[1] for row in diameters if row[0] == max_diameter), None)
    max_same_part = 0
    same_part_witness = None
    for block in blocks:
        for source in block:
            distance = {source: 0}
            queue = deque([source])
            while queue:
                x = queue.popleft()
                for y in safe[x]:
                    if y not in distance:
                        distance[y] = distance[x] + 1
                        queue.append(y)
            for target in block:
                if colour[source] == colour[target] and distance[target] > max_same_part:
                    max_same_part = distance[target]
                    same_part_witness = [source, target]
    masks = [atom_vertex_mask(n, support_adj, atom) for atom in atoms]
    crossing = []
    mixed_component = []
    prefilter_active = None
    for atom_index, (a, b) in enumerate(atoms):
        da, db = gate.bfs(support_adj, a), gate.bfs(support_adj, b)
        for u in range(n):
            for v in safe[u]:
                if u >= v:
                    continue
                su = (da[u] > db[u]) - (da[u] < db[u])
                sv = (da[v] > db[v]) - (da[v] < db[v])
                if su != sv:
                    crossing.append({
                        "atom": atom_index,
                        "edge": [u, v],
                        "signs": [su, sv],
                        "dist": [[da[u], db[u]], [da[v], db[v]]],
                    })
                    break
            if crossing and crossing[-1]["atom"] == atom_index:
                break
        for cid, block in enumerate(blocks):
            signs = {
                (da[v] > db[v]) - (da[v] < db[v])
                for v in block
            }
            if -1 in signs and 1 in signs:
                mixed_component.append({
                    "atom": atom_index,
                    "component": cid,
                    "vertices": block,
                    "endpointComponents": [comp[a], comp[b]],
                })
                break
        if comp[a] == comp[b] and prefilter_active is None:
            path = shortest_path(safe, a, b)
            assert path is not None
            path_edges = {
                tuple(sorted((path[i], path[i + 1])))
                for i in range(len(path) - 1)
            }
            prefilter_active = {
                "atom": atom_index,
                "path": path,
                "jointlyValid": gate.valid_offsupport_set(n, support, atoms, path_edges),
            }
            if not prefilter_active["jointlyValid"]:
                prefilter_active["failure"] = explain_invalid(
                    n, support, atoms, path_edges)

    vertex_atoms = [
        [i for i, mask in enumerate(masks) if (mask >> v) & 1]
        for v in range(n)
    ]
    for u in range(n):
        for v in safe[u]:
            if u < v:
                assert set(vertex_atoms[u]).isdisjoint(vertex_atoms[v])
    repeated_interval = None
    for cid, block in enumerate(blocks):
        owner = {}
        for v in block:
            for atom in vertex_atoms[v]:
                if atom in owner:
                    repeated_interval = {
                        "component": cid,
                        "atom": atom,
                        "vertices": [owner[atom], v],
                        "block": block,
                    }
                    break
                owner[atom] = v
            if repeated_interval is not None:
                break
        if repeated_interval is not None:
            break
    uncovered_two_step = None
    for middle in range(n):
        neighbours = sorted(safe[middle])
        for i, u in enumerate(neighbours):
            for v in neighbours[i + 1:]:
                if set(vertex_atoms[u]).isdisjoint(vertex_atoms[v]):
                    uncovered_two_step = {
                        "path": [u, middle, v],
                        "endpointAtomSets": [vertex_atoms[u], vertex_atoms[v]],
                    }
                    break
            if uncovered_two_step is not None:
                break
        if uncovered_two_step is not None:
            break
    return {
        "safeEdges": sum(len(xs) for xs in safe) // 2,
        "safeComponents": blocks,
        "maxSafeDiameter": max_diameter,
        "diameterWitness": diameter_witness,
        "maxSamePartSafeDistance": max_same_part,
        "samePartDistanceWitness": same_part_witness,
        "firstSignCrossing": crossing[:1],
        "firstMixedSignComponent": mixed_component[:1],
        "firstRepeatedInterval": repeated_interval,
        "firstUncoveredTwoStep": uncovered_two_step,
        "firstPrefilterActive": prefilter_active,
        "vertexAtomSets": vertex_atoms,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=41721)
    parser.add_argument("--trials", type=int, default=200000)
    parser.add_argument("--want", type=int, default=100)
    parser.add_argument("--mlo", type=int, default=9)
    parser.add_argument("--mhi", type=int, default=35)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    d3.NODE_CAP = 5_000_000
    found = 0
    aggregate = {
        "circuits": 0,
        "signCrossings": 0,
        "mixedSignComponents": 0,
        "repeatedIntervals": 0,
        "uncoveredTwoSteps": 0,
        "prefilterActive": 0,
        "jointlyValidActive": 0,
        "maxSafeDiameter": 0,
        "activeComponents": 0,
    }
    first_crossing = None
    first_prefilter = None
    for _ in range(args.trials):
        generated = random_gate.random_support(rng, rng.randint(args.mlo, args.mhi))
        if generated is None:
            continue
        n, support = generated
        witness, aborted, _pairs = d3.check_F((g6util.graph6(n, support),))
        if aborted or witness is None:
            continue
        atoms = [tuple(pair) for pair, _mask in witness[1]]
        supports = [mask for _pair, mask in witness[1]]
        if not random_gate.exact_minimal_circuit(supports, len(support)):
            continue
        result = inspect(n, support, atoms)
        found += 1
        aggregate["circuits"] += 1
        aggregate["signCrossings"] += bool(result["firstSignCrossing"])
        aggregate["mixedSignComponents"] += bool(result["firstMixedSignComponent"])
        aggregate["repeatedIntervals"] += bool(result["firstRepeatedInterval"])
        aggregate["uncoveredTwoSteps"] += bool(result["firstUncoveredTwoStep"])
        aggregate["prefilterActive"] += bool(result["firstPrefilterActive"])
        aggregate["jointlyValidActive"] += bool(
            result["firstPrefilterActive"]
            and result["firstPrefilterActive"]["jointlyValid"])
        aggregate["maxSafeDiameter"] = max(
            aggregate["maxSafeDiameter"], result["maxSafeDiameter"])
        if result["firstSignCrossing"] and first_crossing is None:
            first_crossing = {
                "n": n,
                "support": support,
                "atoms": atoms,
                "probe": result,
            }
        if result["firstPrefilterActive"] and first_prefilter is None:
            first_prefilter = {
                "n": n,
                "support": support,
                "atoms": atoms,
                "probe": result,
            }
        if found >= args.want:
            break
    print(json.dumps({
        "parameters": vars(args),
        "aggregate": aggregate,
        "firstSignCrossing": first_crossing,
        "firstPrefilterActive": first_prefilter,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
