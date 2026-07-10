"""Sparse depth-two-tree stress test of the safe-diameter invariant."""

from __future__ import annotations

import argparse
import json
import random
from concurrent.futures import ProcessPoolExecutor, as_completed

import _codex_random_active_component_search as random_gate
from _codex_safe_component_signature_probe import inspect


def depth_two_tree(rng, nlo, nhi):
    n = rng.randint(nlo, nhi)
    branches = rng.randint(4, min(14, (n - 1) // 2))
    leaves = n - 1 - branches
    counts = [1] * branches
    for _ in range(leaves - branches):
        counts[rng.randrange(branches)] += 1
    support = []
    leaf_branch = {}
    next_vertex = 1 + branches
    for branch, count in enumerate(counts, 1):
        support.append((0, branch))
        for _ in range(count):
            support.append((branch, next_vertex))
            leaf_branch[next_vertex] = branch
            next_vertex += 1
    assert next_vertex == n and len(support) == n - 1
    return n, support, counts, leaf_branch


def random_atom_circuit(rng, n, support, leaf_branch):
    leaves = sorted(leaf_branch)
    rng.shuffle(leaves)
    split = rng.randint(2, len(leaves) - 2)
    left, right = leaves[:split], leaves[split:]
    candidates = [
        (u, v) if u < v else (v, u)
        for u in left
        for v in right
        if leaf_branch[u] != leaf_branch[v]
    ]
    if len(candidates) < n:
        return None
    atoms = sorted(rng.sample(candidates, n))
    edge_index = {edge: i for i, edge in enumerate(support)}
    masks = []
    for u, v in atoms:
        bu, bv = leaf_branch[u], leaf_branch[v]
        mask = 0
        for edge in ((0, bu), (bu, u), (0, bv), (bv, v)):
            normalized = edge if edge[0] < edge[1] else (edge[1], edge[0])
            mask |= 1 << edge_index[normalized]
        masks.append(mask)
    if not random_gate.exact_minimal_circuit(masks, len(support)):
        return None
    return atoms


def worker(seed, trials, want, nlo, nhi):
    rng = random.Random(seed)
    stats = {
        "supports": 0,
        "circuits": 0,
        "maxDiameter": 0,
    }
    for _ in range(trials):
        n, support, counts, leaf_branch = depth_two_tree(rng, nlo, nhi)
        stats["supports"] += 1
        atoms = random_atom_circuit(rng, n, support, leaf_branch)
        if atoms is None:
            continue
        result = inspect(n, support, atoms)
        stats["circuits"] += 1
        stats["maxDiameter"] = max(
            stats["maxDiameter"], result["maxSafeDiameter"])
        if result["maxSafeDiameter"] > 2:
            return {
                "seed": seed,
                "n": n,
                "branchLeafCounts": counts,
                "support": support,
                "atoms": atoms,
                "probe": result,
                "stats": stats,
            }
        if stats["circuits"] >= want:
            break
    return {"seed": seed, "stats": stats}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--tasks", type=int, default=64)
    parser.add_argument("--trials", type=int, default=10000)
    parser.add_argument("--want", type=int, default=20)
    parser.add_argument("--nlo", type=int, default=16)
    parser.add_argument("--nhi", type=int, default=50)
    args = parser.parse_args()
    totals = {
        "supports": 0,
        "circuits": 0,
        "maxDiameter": 0,
    }
    first = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(
                worker, 770000 + i, args.trials, args.want, args.nlo, args.nhi)
            for i in range(args.tasks)
        ]
        for future in as_completed(futures):
            row = future.result()
            for key in ("supports", "circuits"):
                totals[key] += row["stats"][key]
            totals["maxDiameter"] = max(
                totals["maxDiameter"], row["stats"]["maxDiameter"])
            if "probe" in row and first is None:
                first = row
                for pending in futures:
                    pending.cancel()
    print(json.dumps({
        "parameters": vars(args),
        "totals": totals,
        "firstDiameterAboveTwo": first,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
