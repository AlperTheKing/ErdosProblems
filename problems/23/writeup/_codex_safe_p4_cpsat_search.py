"""CP-SAT falsifier search for the safe-component diameter-two lemma."""

from __future__ import annotations

import argparse
import json
import random
from collections import deque
from concurrent.futures import CancelledError, ProcessPoolExecutor, as_completed
from pathlib import Path

from ortools.sat.python import cp_model

import _codex_internal_offsupport_gate as gate
import _codex_random_active_component_search as random_gate
from _codex_safe_component_signature_probe import inspect


def edge(u, v):
    return (u, v) if u < v else (v, u)


def random_tree(rng, n):
    edges = []
    for v in range(1, n):
        if rng.random() < 0.7:
            parent = rng.randrange(max(1, min(v, 6)))
        else:
            parent = rng.randrange(v)
        edges.append(edge(parent, v))
    return edges


def random_support(rng, n, max_extra_edges):
    edges = random_tree(rng, n)
    if max_extra_edges <= 0:
        return edges
    adj, _dist = all_distances(n, edges)
    colour = gate.bipartition(adj)
    assert colour is not None
    edge_set = set(edges)
    candidates = [
        edge(u, v)
        for u in range(n)
        for v in range(u + 1, n)
        if colour[u] != colour[v] and edge(u, v) not in edge_set
    ]
    rng.shuffle(candidates)
    extra = rng.randint(0, min(max_extra_edges, len(candidates)))
    return sorted(edges + candidates[:extra])


def all_distances(n, support):
    adj = [set() for _ in range(n)]
    for u, v in support:
        adj[u].add(v)
        adj[v].add(u)
    return adj, [gate.bfs(adj, source) for source in range(n)]


def support_mask(support, dist, atom):
    a, b = atom
    assert dist[a][b] == 4
    mask = 0
    for i, (u, v) in enumerate(support):
        if dist[a][u] + 1 + dist[v][b] == 4 or dist[a][v] + 1 + dist[u][b] == 4:
            mask |= 1 << i
    return mask


def safe_for_atom(dist, chord, atom):
    x, y = chord
    a, b = atom
    return (
        dist[a][x] + 1 + dist[y][b] > 4
        and dist[a][y] + 1 + dist[x][b] > 4
    )


def matching_hall_witness(masks, skip, edge_count):
    left = [i for i in range(len(masks)) if i != skip]
    match_right = [-1] * edge_count
    match_left = [-1] * len(masks)

    def augment(atom, seen):
        mask = masks[atom]
        while mask:
            bit = mask & -mask
            support_index = bit.bit_length() - 1
            mask ^= bit
            if seen[support_index]:
                continue
            seen[support_index] = True
            owner = match_right[support_index]
            if owner < 0 or augment(owner, seen):
                match_right[support_index] = atom
                match_left[atom] = support_index
                return True
        return False

    for atom in left:
        augment(atom, [False] * edge_count)
    unmatched = [atom for atom in left if match_left[atom] < 0]
    if not unmatched:
        return None
    seen_left = set(unmatched)
    seen_right = set()
    queue = deque((0, atom) for atom in unmatched)
    while queue:
        kind, value = queue.popleft()
        if kind == 0:
            mask = masks[value]
            while mask:
                bit = mask & -mask
                support_index = bit.bit_length() - 1
                mask ^= bit
                if support_index == match_left[value] or support_index in seen_right:
                    continue
                seen_right.add(support_index)
                queue.append((1, support_index))
        else:
            owner = match_right[value]
            if owner >= 0 and owner not in seen_left:
                seen_left.add(owner)
                queue.append((0, owner))
    return {
        "skip": skip,
        "left": sorted(seen_left),
        "right": sorted(seen_right),
        "deficiency": len(seen_left) - len(seen_right),
    }


def random_chord_path(rng, n, support, colour, path_edges):
    support_set = set(support)
    candidate = [set() for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            if colour[u] != colour[v] and edge(u, v) not in support_set:
                candidate[u].add(v)
                candidate[v].add(u)
    for _ in range(200):
        path = [rng.randrange(n)]
        for _step in range(path_edges):
            options = candidate[path[-1]] - set(path)
            if not options:
                break
            path.append(rng.choice(tuple(options)))
        if len(path) == path_edges + 1:
            return path
    return None


def random_active_path(
        rng, n, support, colour, dist, path_edges, node_cap):
    support_set = set(support)
    candidate = [set() for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            if colour[u] != colour[v] and edge(u, v) not in support_set:
                candidate[u].add(v)
                candidate[v].add(u)
    endpoint_pairs = [
        (u, v)
        for u in range(n)
        for v in range(u + 1, n)
        if dist[u][v] == 4
    ]
    rng.shuffle(endpoint_pairs)
    nodes = 0
    capped = False
    for source, target in endpoint_pairs[:100]:
        if capped:
            break
        path = [source]
        used = {source}

        def extend(remaining):
            nonlocal nodes, capped
            nodes += 1
            if nodes > node_cap:
                capped = True
                return None
            if remaining == 0:
                return list(path) if path[-1] == target else None
            options = list(candidate[path[-1]] - used)
            rng.shuffle(options)
            for nxt in options:
                if remaining == 1 and nxt != target:
                    continue
                if nxt == target and remaining != 1:
                    continue
                used.add(nxt)
                path.append(nxt)
                offsupport = {
                    edge(path[i], path[i + 1])
                    for i in range(len(path) - 1)
                }
                result = None
                if gate.valid_offsupport_set(
                        n, support, [(source, target)], offsupport):
                    result = extend(remaining - 1)
                if result is not None:
                    return result
                path.pop()
                used.remove(nxt)
            return None

        result = extend(path_edges)
        if result is not None:
            return (result, (source, target)), capped
    return None, capped


def solve_instance(seed, attempts, nlo, nhi, seconds, path_edges, solutions,
                   force_active, report_shortage, report_model,
                   hall_separate, max_extra_edges, path_node_cap):
    rng = random.Random(seed)
    stats = {
        "trees": 0,
        "models": 0,
        "exactCircuits": 0,
        "maxDiameter": 0,
        "cpUnknown": 0,
        "cpInfeasible": 0,
        "edgeShortage": 0,
        "forcedAtomRejected": 0,
        "hallCuts": 0,
        "hallClosures": 0,
        "forcedAtomInHall": 0,
        "maxHallDeficiency": 0,
        "nearDistanceFour": 0,
        "nearDistanceOther": 0,
        "nearClosureSuccess": 0,
        "nearClosureFailure": 0,
        "pathCaps": 0,
    }
    for _ in range(attempts):
        n = rng.randint(nlo, nhi)
        support = random_support(rng, n, max_extra_edges)
        atom_count = len(support) + 1
        adj, dist = all_distances(n, support)
        colour = gate.bipartition(adj)
        assert colour is not None
        if force_active:
            active_data, path_capped = random_active_path(
                rng, n, support, colour, dist, path_edges, path_node_cap)
            stats["pathCaps"] += int(path_capped)
        else:
            active_data = None
        if force_active:
            if active_data is None:
                continue
            path, forced_atom = active_data
        else:
            path = random_chord_path(rng, n, support, colour, path_edges)
            forced_atom = None
        if path is None:
            continue
        chords = [edge(path[i], path[i + 1]) for i in range(3)]
        if path_edges != 3:
            chords = [edge(path[i], path[i + 1]) for i in range(path_edges)]
        bad_colour = [rng.randrange(2) for _ in range(n)]
        if forced_atom is not None:
            bad_colour[forced_atom[0]] = 0
            bad_colour[forced_atom[1]] = 1
        chord_set = set(chords)
        atoms = [
            (u, v)
            for u in range(n)
            for v in range(u + 1, n)
            if dist[u][v] == 4
            and (force_active or bad_colour[u] != bad_colour[v])
            and (
                gate.valid_offsupport_set(n, support, [(u, v)], chord_set)
                if force_active
                else all(safe_for_atom(dist, chord, (u, v)) for chord in chords)
            )
        ]
        if len(atoms) < atom_count:
            continue
        masks = [support_mask(support, dist, atom) for atom in atoms]
        stats["trees"] += 1
        if forced_atom is not None and forced_atom not in atoms:
            stats["forcedAtomRejected"] += 1
            continue
        multiplicities = [
            sum((mask >> support_index) & 1 for mask in masks)
            for support_index in range(len(support))
        ]
        if min(multiplicities, default=0) < 2:
            stats["edgeShortage"] += 1
            if report_shortage:
                shortage = [
                    i for i, multiplicity in enumerate(multiplicities)
                    if multiplicity < 2
                ]
                return {
                    "seed": seed,
                    "shortage": {
                        "n": n,
                        "support": support,
                        "forcedPath": path,
                        "forcedAtom": forced_atom,
                        "allowedAtoms": atoms,
                        "shortage": [
                            {
                                "index": i,
                                "edge": support[i],
                                "multiplicity": multiplicities[i],
                                "compatibleAtoms": [
                                    atoms[j] for j, mask in enumerate(masks)
                                    if (mask >> i) & 1
                                ],
                            }
                            for i in shortage
                        ],
                    },
                    "stats": stats,
                }
            continue
        model = cp_model.CpModel()
        chosen = [model.new_bool_var(f"a{i}") for i in range(len(atoms))]
        model.add(sum(chosen) == atom_count)
        if force_active:
            atom_index = {atom: i for i, atom in enumerate(atoms)}
            for u in range(n):
                for v in range(u + 1, n):
                    uv = atom_index.get((u, v))
                    if uv is None:
                        continue
                    for w in range(v + 1, n):
                        uw = atom_index.get((u, w))
                        vw = atom_index.get((v, w))
                        if uw is not None and vw is not None:
                            model.add(chosen[uv] + chosen[uw] + chosen[vw] <= 2)
        if forced_atom is not None:
            model.add(chosen[atoms.index(forced_atom)] == 1)
        for support_index in range(len(support)):
            model.add(sum(
                chosen[i] for i, mask in enumerate(masks)
                if (mask >> support_index) & 1
            ) >= 2)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = seconds
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = seed & 0x7FFFFFFF
        cuts_added = 0
        for _solution in range(solutions):
            status = solver.solve(model)
            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                if status == cp_model.UNKNOWN:
                    stats["cpUnknown"] += 1
                elif status == cp_model.INFEASIBLE:
                    stats["cpInfeasible"] += 1
                    if cuts_added:
                        stats["hallClosures"] += 1
                break
            selected_indices = [i for i, var in enumerate(chosen) if solver.value(var)]
            stats["models"] += 1
            selected_atoms = [atoms[i] for i in selected_indices]
            selected_masks = [masks[i] for i in selected_indices]
            near_closure = None
            if force_active and len(path) >= 3:
                near_source, near_target = path[1], path[-2]
                near_distance = dist[near_source][near_target]
                if near_distance == 4:
                    stats["nearDistanceFour"] += 1
                    near_mask = support_mask(
                        support, dist, (near_source, near_target))
                    edge_owners = [
                        {
                            index for index, mask in enumerate(selected_masks)
                            if (mask >> support_index) & 1
                        }
                        for support_index in range(len(support))
                    ]
                    near_atoms = set()
                    for support_index in range(len(support)):
                        if (near_mask >> support_index) & 1:
                            near_atoms.update(edge_owners[support_index])
                    closed_edges = {
                        support_index
                        for support_index, owners in enumerate(edge_owners)
                        if owners and owners <= near_atoms
                    }
                    closed_atoms = set().union(
                        *(edge_owners[index] for index in closed_edges))
                    assert closed_atoms == near_atoms
                    success = len(closed_atoms) <= len(closed_edges)
                    stats[
                        "nearClosureSuccess" if success
                        else "nearClosureFailure"
                    ] += 1
                    near_closure = {
                        "distance": near_distance,
                        "corridorEdges": near_mask.bit_count(),
                        "incidentAtoms": len(near_atoms),
                        "closedEdges": len(closed_edges),
                        "success": success,
                    }
                else:
                    stats["nearDistanceOther"] += 1
                    near_closure = {"distance": near_distance}
            if random_gate.exact_minimal_circuit(selected_masks, len(support)):
                stats["exactCircuits"] += 1
                probe = inspect(n, support, selected_atoms)
                stats["maxDiameter"] = max(
                    stats["maxDiameter"], probe["maxSafeDiameter"])
                active, nodes, capped = random_gate.active_path(
                    n, support, selected_atoms, node_cap=1_000_000)
                if force_active:
                    assert gate.valid_offsupport_set(
                        n, support, selected_atoms, chord_set)
                    assert forced_atom in selected_atoms
                    active = {"badEdge": list(forced_atom), "path": path}
                if probe["maxSamePartSafeDistance"] > 4 or active is not None:
                    return {
                        "seed": seed,
                        "n": n,
                        "support": support,
                        "forcedPath": path,
                        "forcedAtom": forced_atom,
                        "atoms": selected_atoms,
                        "probe": probe,
                        "active": active,
                        "activeNodes": nodes,
                        "activeCapped": capped,
                        "stats": stats,
                    }
            else:
                hall = None
                for skip in range(len(selected_masks)):
                    hall = matching_hall_witness(
                        selected_masks, skip, len(support))
                    if hall is not None:
                        break
                assert hall is not None
                stats["maxHallDeficiency"] = max(
                    stats["maxHallDeficiency"], hall["deficiency"])
                forced_local = (
                    selected_atoms.index(forced_atom)
                    if forced_atom is not None else -1
                )
                if forced_local in hall["left"]:
                    stats["forcedAtomInHall"] += 1
                if report_model:
                    left_set = set(hall["left"])
                    right_set = set(hall["right"])
                    complement_atoms = [
                        selected_atoms[i]
                        for i in range(len(selected_atoms))
                        if i not in left_set
                    ]
                    complement_edges = [
                        support[i]
                        for i in range(len(support))
                        if i not in right_set
                    ]
                    return {
                        "seed": seed,
                        "nonminimal": {
                            "n": n,
                            "support": support,
                            "forcedPath": path,
                            "forcedAtom": forced_atom,
                            "selectedAtoms": selected_atoms,
                            "nearClosure": near_closure,
                            "hallWitness": {
                                **hall,
                                "leftAtoms": [selected_atoms[i] for i in hall["left"]],
                                "rightEdges": [support[i] for i in hall["right"]],
                                "complementAtoms": complement_atoms,
                                "complementEdges": complement_edges,
                                "complementBalanced":
                                    len(complement_atoms) == len(complement_edges),
                            },
                        },
                        "stats": stats,
                    }
                if hall_separate:
                    # This Hall-deficient atom subset can occur in no
                    # inclusion-minimal circuit, regardless of what other
                    # compatible atoms are selected.  Cut it globally.
                    model.add(sum(
                        chosen[selected_indices[i]] for i in hall["left"]
                    ) <= len(hall["left"]) - 1)
                    stats["hallCuts"] += 1
                    cuts_added += 1
                    continue
            model.add(
                sum(chosen[i] for i in selected_indices) <= atom_count - 1)
    return {"seed": seed, "stats": stats}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--tasks", type=int, default=128)
    parser.add_argument("--seed-base", type=int, default=660000)
    parser.add_argument("--attempts", type=int, default=200)
    parser.add_argument("--nlo", type=int, default=12)
    parser.add_argument("--nhi", type=int, default=30)
    parser.add_argument("--seconds", type=float, default=1.0)
    parser.add_argument("--path-edges", type=int, default=6)
    parser.add_argument("--solutions", type=int, default=3)
    parser.add_argument("--force-active", action="store_true")
    parser.add_argument("--report-shortage", action="store_true")
    parser.add_argument("--report-model", action="store_true")
    parser.add_argument("--hall-separate", action="store_true")
    parser.add_argument("--extra-support-edges", type=int, default=0)
    parser.add_argument("--path-node-cap", type=int, default=5000)
    parser.add_argument("--output")
    args = parser.parse_args()
    totals = {
        "trees": 0,
        "models": 0,
        "exactCircuits": 0,
        "maxDiameter": 0,
        "cpUnknown": 0,
        "cpInfeasible": 0,
        "edgeShortage": 0,
        "forcedAtomRejected": 0,
        "hallCuts": 0,
        "hallClosures": 0,
        "forcedAtomInHall": 0,
        "maxHallDeficiency": 0,
        "nearDistanceFour": 0,
        "nearDistanceOther": 0,
        "nearClosureSuccess": 0,
        "nearClosureFailure": 0,
        "pathCaps": 0,
    }
    first = None
    first_shortage = None
    first_nonminimal = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(
                solve_instance, args.seed_base + i, args.attempts,
                args.nlo, args.nhi, args.seconds, args.path_edges,
                args.solutions, args.force_active, args.report_shortage,
                args.report_model, args.hall_separate,
                args.extra_support_edges, args.path_node_cap)
            for i in range(args.tasks)
        ]
        for future in as_completed(futures):
            try:
                row = future.result()
            except CancelledError:
                continue
            for key in ("trees", "models", "exactCircuits", "cpUnknown", "cpInfeasible", "edgeShortage", "forcedAtomRejected", "hallCuts", "hallClosures", "forcedAtomInHall", "nearDistanceFour", "nearDistanceOther", "nearClosureSuccess", "nearClosureFailure", "pathCaps"):
                totals[key] += row["stats"][key]
            totals["maxDiameter"] = max(
                totals["maxDiameter"], row["stats"]["maxDiameter"])
            totals["maxHallDeficiency"] = max(
                totals["maxHallDeficiency"],
                row["stats"]["maxHallDeficiency"])
            if "probe" in row and first is None:
                first = row
                for pending in futures:
                    pending.cancel()
            if "shortage" in row and first_shortage is None:
                first_shortage = row
                for pending in futures:
                    pending.cancel()
            if "nonminimal" in row and first_nonminimal is None:
                first_nonminimal = row
                for pending in futures:
                    pending.cancel()
    output = json.dumps({
        "parameters": vars(args),
        "totals": totals,
        "first": first,
        "firstShortage": first_shortage,
        "firstNonminimal": first_nonminimal,
    }, sort_keys=True, separators=(",", ":"))
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="ascii")
    print(output)


if __name__ == "__main__":
    main()
