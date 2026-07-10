"""Exact locked-family gate for the GPT-Pro collision-reserve inequality.

This verifies only the graph-combinatorial counting atom

    E[q_v + h_v] >= deg_H(v) - max(0, N - T(v)).

It deliberately does NOT claim that a raw collision witness is an official
``c5Base``/``prune`` token.  That transfer is the remaining theorem.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _codex_pro_active_cycle_counterexample_verify import (  # noqa: E402
    adjacency,
    edge,
    full_support,
)
from _codex_endpointflow_3892_counterexample import (  # noqa: E402
    ATTACHMENTS,
    T,
)


def active_cycle_lock() -> dict:
    w = 26
    support = {edge(i, (i + 1) % 26) for i in range(26)} | {edge(w, 0)}
    atoms = (
        {edge(i, (i + 4) % 26) for i in range(26)}
        | {edge(w, 3), edge(w, 23)}
    )
    active_vertices = [(9 * k) % 26 for k in range(13)]
    active_edges = {
        edge(active_vertices[i], active_vertices[i + 1])
        for i in range(len(active_vertices) - 1)
    }
    blue_core = support | active_edges

    # Private length-six locking paths add 140 zero-load vertices.
    blue = set(blue_core)
    next_vertex = 27
    for a, b in sorted(atoms):
        internal = list(range(next_vertex, next_vertex + 5))
        next_vertex += 5
        path = [a] + internal + [b]
        blue.update(edge(u, v) for u, v in zip(path, path[1:]))
    n = next_vertex
    assert n == 167

    blue_adj = adjacency(n, blue)
    row_vertices = {}
    for atom in sorted(atoms):
        distance, path_count, _, vertices = full_support(blue, blue_adj, atom)
        assert distance == 4 and path_count == 1
        row_vertices[atom] = vertices

    h_adj = adjacency(n, active_edges)
    rows = tuple(row_vertices.values())
    records = []
    for v in active_vertices:
        through = [row for row in rows if v in row]
        r_v = len(through)
        union_v = set().union(*through) if through else set()
        q_v = 5 * r_v - len(union_v)
        h_v = len(h_adj[v] & union_v)
        t_v = 5 * r_v
        deg_v = len(h_adj[v])
        slack_v = max(0, n - t_v)
        count_rhs = t_v + deg_v - n
        hall_rhs = deg_v - slack_v
        assert q_v + h_v >= count_rhs
        assert q_v + h_v >= hall_rhs
        records.append({
            "v": v,
            "r": r_v,
            "union": len(union_v),
            "q": q_v,
            "h": h_v,
            "T": t_v,
            "degree": deg_v,
            "slack": slack_v,
            "collisionMargin": q_v + h_v - hall_rhs,
        })

    return {
        "N": n,
        "badEdges": len(atoms),
        "activeEdges": len(active_edges),
        "minCollisionMargin": min(r["collisionMargin"] for r in records),
        "maxRequiredReserve": str(max(
            Fraction(max(0, r["degree"] - r["slack"]), 2)
            for r in records
        )),
        "records": records,
    }


def nonuniform_c5_attachment_lock() -> dict:
    # Every shortest row of one attached bad block passes through its singleton
    # middle vertex v and remains inside the five blow-up parts.
    bad_per_attachment = T * T
    part_union = T + T * T + 1 + T * T + T
    deterministic_q_lower = 5 * bad_per_attachment - part_union
    assert bad_per_attachment == 784
    assert part_union == 1625
    assert deterministic_q_lower == 2295

    n = 3892
    endpoint_load = {4: 3935, 8: 3930}
    records = []
    for v in ATTACHMENTS:
        slack_v = max(0, n - endpoint_load[v])
        degree_v = 1
        hall_rhs = degree_v - slack_v
        assert deterministic_q_lower >= hall_rhs
        records.append({
            "v": v,
            "T": endpoint_load[v],
            "degree": degree_v,
            "slack": slack_v,
            "qLower": deterministic_q_lower,
            "halfReserveLower": str(Fraction(deterministic_q_lower, 2)),
            "requiredHalfReserve": str(Fraction(max(0, hall_rhs), 2)),
            "collisionMarginLower": deterministic_q_lower - hall_rhs,
        })

    return {
        "N": n,
        "attachmentSizes": [T, T * T, 1, T * T, T],
        "badPerAttachment": bad_per_attachment,
        "rowUnionUpper": part_union,
        "records": records,
    }


def main() -> None:
    print(json.dumps({
        "activeCycle": active_cycle_lock(),
        "nonuniformC5": nonuniform_c5_attachment_lock(),
        "scope": "raw collision counting only; bank-token transfer unproved",
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
