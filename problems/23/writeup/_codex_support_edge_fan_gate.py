"""Exact guardrail for raw shared-support-edge fan switches.

The genuine support-edge collision count is valid, but a shared edge does not
by itself guarantee a positive ambient switch: extra blue boundary must be
routed through the inherited bank/closure.  This gate exhausts every pair of
ell=5 atoms sharing a support edge in the canonical 24-vertex wall, every
shortest row for each atom, and both terminal-prefix orientations.
"""

from __future__ import annotations

from itertools import combinations

from _claude_residual_hall_gate import geos_paths, residuals
from _codex_k2t_switch_probe import adj_from_edges
from _codex_singleton_vertexslack_gate import norm_edge, structured_records


def terminal_prefixes(path, edge):
    edge = tuple(sorted(edge))
    out = []
    for index in range(len(path) - 1):
        if norm_edge(path[index], path[index + 1]) == edge:
            out.append(set(path[: index + 1]))
            out.append(set(path[index + 1 :]))
    return out


def switch_gain(adj, side, switch):
    delta_blue = 0
    delta_bad = 0
    for u in range(len(adj)):
        for v in adj[u]:
            if u >= v or ((u in switch) == (v in switch)):
                continue
            if side[u] != side[v]:
                delta_blue += 1
            else:
                delta_bad += 1
    return delta_bad - delta_blue


def analyze(record):
    name, n, edges, side = record
    adj = adj_from_edges(n, edges)
    data = residuals(n, adj, side)
    assert data is not None
    atoms = tuple(data["M"])
    rows = {atom: geos_paths(adj, side, *atom) for atom in atoms}

    support = set()
    for paths in rows.values():
        for path in paths:
            support.update(
                norm_edge(path[i], path[i + 1]) for i in range(len(path) - 1)
            )

    fibers = {edge: [] for edge in support}
    for edge in support:
        for atom, paths in rows.items():
            using = [
                path
                for path in paths
                if edge
                in {
                    norm_edge(path[i], path[i + 1])
                    for i in range(len(path) - 1)
                }
            ]
            if using:
                fibers[edge].append((atom, using))

    distribution = {}
    failures = []
    pair_count = 0
    for edge, items in fibers.items():
        if len(items) < 2:
            continue
        for (atom_a, paths_a), (atom_b, paths_b) in combinations(items, 2):
            pair_count += 1
            best = None
            for path_a in paths_a:
                for path_b in paths_b:
                    for prefix_a in terminal_prefixes(path_a, edge):
                        for prefix_b in terminal_prefixes(path_b, edge):
                            gain = switch_gain(adj, side, prefix_a | prefix_b)
                            best = gain if best is None else max(best, gain)
            assert best is not None
            distribution[best] = distribution.get(best, 0) + 1
            if best < 1:
                failures.append((edge, atom_a, atom_b, best))

    return {
        "name": name,
        "atoms": len(atoms),
        "support": len(support),
        "defect": len(atoms) - len(support),
        "fiberSizes": sorted(len(items) for items in fibers.values()),
        "pairs": pair_count,
        "bestGainDistribution": dict(sorted(distribution.items())),
        "positivePairs": pair_count - len(failures),
        "failures": len(failures),
        "firstFailure": failures[0] if failures else None,
    }


def main():
    wanted = {"canonical24", "canonical24+waistDoor"}
    records = [record for record in structured_records() if record[0] in wanted]
    assert {record[0] for record in records} == wanted
    for record in records:
        print(analyze(record))


if __name__ == "__main__":
    main()
