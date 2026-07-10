"""Random exact 1-sum stress test for NO-ACTIVE-COMPONENT.

Duplicate an exact minimal ell=5 support circuit while identifying the two
endpoints and the identity of one selected atom.  The support copies are edge
disjoint and the shared atom obtains both shortest-path bundles, producing a
new exact minimal circuit.  Search the cross-copy off-support geometry for an
active component.
"""

from __future__ import annotations

import argparse
import json
import random
from concurrent.futures import ProcessPoolExecutor, as_completed

import _claude_d3_local_obstruction as d3
import _codex_internal_offsupport_gate as gate
import _codex_k4_subdivision_obstruction_search as g6util
import _codex_random_active_component_search as random_gate
from _codex_two_spider_active_search import individually_safe_graph, shortest_path


def edge(u, v):
    return (u, v) if u < v else (v, u)


def incidence_masks(n, support, atoms):
    adj = [set() for _ in range(n)]
    for u, v in support:
        adj[u].add(v)
        adj[v].add(u)
    result = []
    for a, b in atoms:
        da, db = gate.bfs(adj, a), gate.bfs(adj, b)
        if da[b] != 4:
            return None
        mask = 0
        for i, (u, v) in enumerate(support):
            if da[u] + 1 + db[v] == 4 or da[v] + 1 + db[u] == 4:
                mask |= 1 << i
        result.append(mask)
    return result


def twosum(n, support, atoms, shared_index):
    shared = atoms[shared_index]
    fixed = set(shared)
    mapping = {}
    next_vertex = n
    for v in range(n):
        if v in fixed:
            mapping[v] = v
        else:
            mapping[v] = next_vertex
            next_vertex += 1
    support2 = [edge(mapping[u], mapping[v]) for u, v in support]
    atoms2 = [edge(mapping[u], mapping[v]) for u, v in atoms]
    combined_support = sorted(set(support) | set(support2))
    combined_atoms = sorted(set(atoms) | set(atoms2))
    assert len(combined_support) == 2 * len(support)
    assert len(combined_atoms) == len(combined_support) + 1
    return next_vertex, combined_support, combined_atoms, shared


def one_base(seed, trials, mlo, mhi, path_cap):
    rng = random.Random(seed)
    d3.NODE_CAP = 5_000_000
    stats = {
        "supports": 0,
        "baseCircuits": 0,
        "sharedAtoms": 0,
        "prefilterPaths": 0,
        "pathCaps": 0,
    }
    for _ in range(trials):
        generated = random_gate.random_support(rng, rng.randint(mlo, mhi))
        if generated is None:
            continue
        n, support = generated
        stats["supports"] += 1
        witness, aborted, _pairs = d3.check_F((g6util.graph6(n, support),))
        if aborted or witness is None:
            continue
        atoms = [tuple(pair) for pair, _mask in witness[1]]
        supports = [mask for _pair, mask in witness[1]]
        if not random_gate.exact_minimal_circuit(supports, len(support)):
            continue
        stats["baseCircuits"] += 1
        for shared_index in range(len(atoms)):
            stats["sharedAtoms"] += 1
            nn, ff, aa, shared = twosum(n, support, atoms, shared_index)
            masks = incidence_masks(nn, ff, aa)
            assert masks is not None
            assert random_gate.exact_minimal_circuit(masks, len(ff))
            candidate = individually_safe_graph(nn, ff, aa)
            if shortest_path(candidate, *shared) is None:
                continue
            stats["prefilterPaths"] += 1
            active, nodes, capped = random_gate.active_path(
                nn, ff, aa, node_cap=path_cap)
            stats["pathCaps"] += int(capped)
            if active is not None:
                off = {
                    edge(active["path"][i], active["path"][i + 1])
                    for i in range(len(active["path"]) - 1)
                }
                assert gate.valid_offsupport_set(nn, ff, aa, off)
                return {
                    "seed": seed,
                    "baseN": n,
                    "baseSupport": support,
                    "baseAtoms": atoms,
                    "sharedIndex": shared_index,
                    "sharedAtom": shared,
                    "sumN": nn,
                    "active": active,
                    "stats": stats,
                }
        return {"seed": seed, "stats": stats}
    return {"seed": seed, "stats": stats}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--tasks", type=int, default=64)
    parser.add_argument("--trials", type=int, default=5000)
    parser.add_argument("--mlo", type=int, default=9)
    parser.add_argument("--mhi", type=int, default=24)
    parser.add_argument("--path-cap", type=int, default=500000)
    args = parser.parse_args()
    totals = {
        "supports": 0,
        "baseCircuits": 0,
        "sharedAtoms": 0,
        "prefilterPaths": 0,
        "pathCaps": 0,
    }
    first = None
    tasks = [
        (990000 + i, args.trials, args.mlo, args.mhi, args.path_cap)
        for i in range(args.tasks)
    ]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(one_base, *task) for task in tasks]
        for future in as_completed(futures):
            row = future.result()
            for key in totals:
                totals[key] += row["stats"][key]
            if "active" in row and first is None:
                first = row
                for pending in futures:
                    pending.cancel()
    print(json.dumps({
        "parameters": vars(args),
        "totals": totals,
        "first": first,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
