"""Finite star-completion probe for the 16-vertex IES near-counterexample."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_matrix

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "problems" / "23" / "writeup"))

from _codex_ies_16_near_counterexample import (  # noqa: E402
    displayed_cut_data,
    instance,
)
from _codex_ies_random_stress import (  # noqa: E402
    adjacency,
    blue_connected,
    edge,
    frac,
    is_triangle_free,
    row_data,
    subset_check,
)


def star_types(edges, side):
    adj = adjacency(16, edges)
    out = []
    for new_side in (0, 1):
        opposite = [v for v in range(16) if side[v] != new_side]
        for mask in range(1, 1 << len(opposite)):
            nbrs = tuple(opposite[i] for i in range(len(opposite)) if mask >> i & 1)
            if len(nbrs) < 2:
                continue
            if all(v not in adj[u] for i, u in enumerate(nbrs) for v in nbrs[i + 1 :]):
                out.append((new_side, nbrs))
    return out


def old_switch_rows(edges, types):
    rows = 1 << 15
    base = np.zeros(rows, dtype=np.int16)
    penalty = np.zeros((rows, len(types)), dtype=np.int8)
    for mask in range(rows):
        switched = [False] + [bool(mask >> (v - 1) & 1) for v in range(1, 16)]
        energy = 0
        for u, v in edges:
            boundary = switched[u] != switched[v]
            if boundary:
                energy += 1 if SIDE[u] != SIDE[v] else -1
        base[mask] = energy
        for j, (_, nbrs) in enumerate(types):
            t = sum(switched[v] for v in nbrs)
            penalty[mask, j] = min(t, len(nbrs) - t)
    return base, penalty


def exact_old_reduced_min(base, penalty, counts):
    energy = base.astype(np.int32) + penalty.astype(np.int32) @ counts
    arg = int(np.argmin(energy))
    return int(energy[arg]), arg


def build_graph(edges, side, types, counts):
    out_edges = set(edges)
    out_side = list(side)
    chosen = []
    for j, count in enumerate(counts):
        new_side, nbrs = types[j]
        for _ in range(int(count)):
            v = len(out_side)
            out_side.append(new_side)
            out_edges.update(edge(v, u) for u in nbrs)
            chosen.append({"vertex": v, "side": new_side, "neighbors": list(nbrs)})
    return tuple(sorted(out_edges)), tuple(out_side), chosen


def verify(edges, side, atoms):
    n = len(side)
    adj = adjacency(n, edges)
    bad = tuple(e for e in edges if side[e[0]] == side[e[1]])
    blue, rows, load = row_data(n, adj, side, bad)
    margin, deficient, failure, detail = subset_check(n, blue, rows, load, atoms)
    deletions = []
    for atom in atoms:
        child = tuple(a for a in atoms if a != atom)
        short = set().union(*(rows[a]["edges"] for a in child))
        deletions.append(len(child) > len(short))
    displayed = sum(side[u] != side[v] for u, v in edges)
    best = -1
    best_mask = None
    for mask in range(1 << (n - 1)):
        value = sum(
            (((mask >> (u - 1)) & 1) if u else 0)
            != (((mask >> (v - 1)) & 1) if v else 0)
            for u, v in edges
        )
        if value > best:
            best, best_mask = value, mask
    return {
        "n": n,
        "m": len(edges),
        "triangleFree": is_triangle_free(adj, edges),
        "blueConnected": blue_connected(n, adj, side),
        "displayedCut": displayed,
        "globalMaxCut": best,
        "isMaximum": displayed == best,
        "bestMask": best_mask,
        "badUnchanged": set(bad) == set(BASE_BAD),
        "witnessDeficient": deficient,
        "witnessMinimal": not any(deletions),
        "witnessMargin": frac(margin),
        "failure": failure,
        "internalEdge09OffSupport": (0, 9) in map(tuple, detail["internalEdges"]),
        "supportSize": len(detail["shortEdges"]),
        "T9": frac(load[9]),
        "fractionType": isinstance(margin, Fraction),
    }


if __name__ == "__main__":
    BASE_EDGES, SIDE, ATOMS = instance()
    BASE_ADJ = adjacency(16, BASE_EDGES)
    BASE_BAD = tuple(e for e in BASE_EDGES if SIDE[e[0]] == SIDE[e[1]])
    types = star_types(BASE_EDGES, SIDE)
    base, penalty = old_switch_rows(BASE_EDGES, types)
    need = np.maximum(0, -base).astype(np.float64)
    constraints = [
        LinearConstraint(csc_matrix(penalty), lb=need, ub=np.full(len(base), np.inf)),
        LinearConstraint(np.ones((1, len(types))), lb=-np.inf, ub=10),
    ]
    result = milp(
        c=np.ones(len(types)),
        integrality=np.ones(len(types)),
        bounds=Bounds(np.zeros(len(types)), np.full(len(types), 10)),
        constraints=constraints,
        options={"time_limit": 300, "mip_rel_gap": 0.0, "presolve": True},
    )
    counts = np.rint(result.x).astype(np.int16) if result.x is not None else None
    output = {
        "types": len(types),
        "constraints": len(base),
        "milpStatus": result.message,
        "objective": None if result.fun is None else float(result.fun),
