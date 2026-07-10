"""Exact 16-vertex near-counterexample to Internal Endpoint Slack.

The displayed cut is triangle-free, has connected blue graph, and every bad
edge has odd-cycle length five.  A minimal support-deficient atom set has one
internal off-support blue edge at an overloaded vertex, so IES fails by 1/2.
The cut is not maximum; this script also proves that no triangle-free addition
on the same vertex set can make this particular cut maximum.
"""

from __future__ import annotations

import json

from _codex_ies_random_stress import (
    adjacency,
    blue_connected,
    edge,
    exact_gamma_min_cuts,
    frac,
    is_triangle_free,
    row_data,
    subset_check,
)


def instance():
    left = range(4)
    u0, u, w1, v1, w2, v2 = 4, 5, 6, 7, 8, 9
    right1 = range(10, 13)
    right2 = range(13, 16)

    edges = {
        edge(0, u0),
        edge(u0, w1),
        edge(u, w1),
        edge(w1, v1),
        edge(u, w2),
        edge(w2, v2),
        edge(0, v2),
    }
    edges.update(edge(x, u) for x in (1, 2, 3))
    edges.update(edge(v1, r) for r in right1)
    edges.update(edge(v2, r) for r in right2)

    for x in left:
        for r in right1:
            if (x, r) not in {(1, 10), (2, 11)}:
                edges.add(edge(x, r))
    for x in (1, 2, 3):
        for r in right2:
            if (x, r) != (1, 13):
                edges.add(edge(x, r))

    side = tuple(1 if x in {u0, u, v1, v2} else 0 for x in range(16))
    atoms = (
        (0, 10), (0, 11), (0, 12),
        (1, 11), (1, 12), (1, 14), (1, 15),
        (2, 10), (2, 12), (2, 13), (2, 14), (2, 15),
        (3, 10), (3, 11), (3, 12), (3, 13),
    )
    return tuple(sorted(edges)), side, atoms


def displayed_cut_data(edges, side, atoms):
    adj = adjacency(16, edges)
    bad = tuple(e for e in edges if side[e[0]] == side[e[1]])
    blue, rows, load = row_data(16, adj, side, bad)
    margin, deficient, failure, detail = subset_check(
        16, blue, rows, load, atoms
    )
    deletion_data = []
    for atom in atoms:
        child = tuple(a for a in atoms if a != atom)
        short = set().union(*(rows[a]["edges"] for a in child))
        deletion_data.append({
            "removed": list(atom),
            "atoms": len(child),
            "support": len(short),
            "deficient": len(child) > len(short),
        })
    return adj, bad, rows, load, {
        "displayedCut": sum(side[u] != side[v] for u, v in edges),
        "displayedBad": len(bad),
        "blueConnected": blue_connected(16, adj, side),
        "allEll5": all(row["ell"] == 5 for row in rows.values()),
        "witnessDeficient": deficient,
        "witnessMargin": frac(margin),
        "witnessFailure": failure,
        "witness": detail,
        "inclusionMinimal": not any(row["deficient"] for row in deletion_data),
        "deletions": deletion_data,
        "T": [frac(x) for x in load],
    }


def no_same_vertex_completion(edges, side):
    """Exhaust all triangle-free blue additions on the existing vertices."""
    adj = adjacency(16, edges)
    candidates = []
    for u in range(16):
        for v in range(u + 1, 16):
            e = (u, v)
            if side[u] != side[v] and e not in edges and not (adj[u] & adj[v]):
                candidates.append(e)

    displayed_base = sum(side[u] != side[v] for u, v in edges)
    constraints = []
    for assignment in range(1 << 15):
        alt_side = (0,) + tuple((assignment >> (v - 1)) & 1 for v in range(1, 16))
        alt_cut = sum(alt_side[u] != alt_side[v] for u, v in edges)
        gain = alt_cut - displayed_base
        if gain <= 0:
            continue
        uncut_mask = sum(
            1 << i
            for i, (u, v) in enumerate(candidates)
            if alt_side[u] == alt_side[v]
        )
        constraints.append((uncut_mask, gain))

    valid = 0
    maximum = []
    for mask in range(1 << len(candidates)):
        added = tuple(candidates[i] for i in range(len(candidates)) if mask >> i & 1)
        augmented = tuple(sorted(set(edges) | set(added)))
        aug_adj = adjacency(16, augmented)
        if not is_triangle_free(aug_adj, augmented):
            continue
        valid += 1
        if all((mask & uncut_mask).bit_count() >= gain
               for uncut_mask, gain in constraints):
            maximum.append([list(e) for e in added])
    return {
        "candidateBlueEdges": [list(e) for e in candidates],
        "triangleFreeCompletions": valid,
        "fixedCutMaximumCompletions": maximum,
    }


def main():
    edges, side, atoms = instance()
    adj, _, _, _, displayed = displayed_cut_data(edges, side, atoms)
    best, maximum_count, gamma, cuts = exact_gamma_min_cuts(16, edges, adj)
    result = {
        "n": 16,
        "edges": [list(e) for e in edges],
        "triangleFree": is_triangle_free(adj, edges),
        "side": list(side),
        **displayed,
        "globalMaxCut": best,
        "maximumCutsModComplement": maximum_count,
        "gammaMinMaximumCut": gamma,
        "gammaMinConnectedBCuts": len(cuts),
        "sameVertexCompletion": no_same_vertex_completion(edges, side),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
