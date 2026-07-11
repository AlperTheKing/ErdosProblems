"""Exact falsifier for the R25/R26 three-active-edge killer statement.

The scoped Hall-failing tuple below has a score-zero one-row replacement,
but every active-killing replacement uses at most two old active edges.  It
also has no selected support edge at active-graph radius three from any bad
atom.  All arithmetic and owner-flow checks are integral exact.
"""

from __future__ import annotations

import json
from collections import Counter

from _codex_r19_global_base_census import dec, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_outside_attachment_census_gate import (
    edge_distance,
    edge_radius,
)
from _codex_r23_outside_attachment_full_obligation_gate import (
    active_scoped_obligation_score,
    full_owner_flow,
)


GRAPH6 = "J?bFF`wN?{?"
CHOICE = (0, 0, 0, 0)


def norm_edge(x, y):
    return (x, y) if x < y else (y, x)


def main() -> int:
    n, graph_edges = dec(GRAPH6)
    info = loads(n, graph_edges)
    assert info is not None
    assert all(length == 5 for length in info["ell"].values())
    families = shortest_row_families(info)
    rows = tuple(families[i][CHOICE[i]] for i in range(len(CHOICE)))
    blue = set(info["Bset"])
    bad = set(info["Mset"])
    vertices = {v for row in rows for v in row}
    support = {
        norm_edge(x, y)
        for row in rows
        for x, y in zip(row, row[1:])
    }
    active = {
        edge for edge in blue
        if edge[0] in vertices and edge[1] in vertices and edge not in support
    }
    score = active_scoped_obligation_score(n, blue, bad, rows)
    flow = full_owner_flow(
        n, blue, bad, rows, GRAPH6,
        require_full=False, quiet=True, scope="active", include_outside=False,
    )
    radius_three_pairs = [
        (index, selected_edge)
        for index, bad_edge in enumerate(info["M"])
        for selected_edge in support
        if edge_radius(active, bad_edge, selected_edge) == 3
    ]
    active_atom_distances = [
        edge_distance(active, *bad_edge) for bad_edge in info["M"]
    ]
    active_atom_distances = [d for d in active_atom_distances if d is not None]

    replacements = []
    histogram = Counter()
    for index, family in enumerate(families):
        for replacement, replacement_row in enumerate(family):
            if replacement == CHOICE[index]:
                continue
            eta = CHOICE[:index] + (replacement,) + CHOICE[index + 1:]
            new_rows = tuple(families[i][eta[i]] for i in range(len(eta)))
            new_score = active_scoped_obligation_score(n, blue, bad, new_rows)
            new_flow = full_owner_flow(
                n, blue, bad, new_rows, GRAPH6,
                require_full=False, quiet=True, scope="active",
                include_outside=False,
            )
            replacement_edges = {
                norm_edge(x, y)
                for x, y in zip(replacement_row, replacement_row[1:])
            }
            active_count = len(replacement_edges & active)
            support_count = len(replacement_edges & support)
            internal = (
                set(replacement_row) <= vertices
                and replacement_edges <= active | support
            )
            kills = new_flow["activeComponents"] == 0
            killer = internal and active_count >= 3 and kills
            histogram[
                f"{active_count}A+{support_count}S/kill={kills}/score={new_score}"
            ] += 1
            replacements.append({
                "index": index,
                "replacement": replacement,
                "row": list(replacement_row),
                "newScore": new_score,
                "newFlowFull": new_flow["full"],
                "newActiveComponents": new_flow["activeComponents"],
                "activeCount": active_count,
                "supportCount": support_count,
                "internal": internal,
                "killer": killer,
            })

    assert score == 30
    assert not flow["full"] and flow["deficiency"] == 2
    assert active_atom_distances == [8]
    assert not radius_three_pairs
    assert min(row["newScore"] for row in replacements) == 0
    assert any(row["newActiveComponents"] == 0 for row in replacements)
    assert not any(row["killer"] for row in replacements)
    assert max(
        row["activeCount"] for row in replacements
        if row["internal"] and row["newActiveComponents"] == 0
    ) == 2

    payload = {
        "graph6": GRAPH6,
        "order": n,
        "choice": list(CHOICE),
        "badEdges": [list(edge) for edge in info["M"]],
        "rows": [list(row) for row in rows],
        "oldScore": score,
        "oldFlow": flow,
        "oldSupport": [list(edge) for edge in sorted(support)],
        "oldActive": [list(edge) for edge in sorted(active)],
        "activeAtomDistances": active_atom_distances,
        "radiusThreePairs": radius_three_pairs,
        "replacementHistogram": dict(sorted(histogram.items())),
        "descendingReplacements": [
            row for row in replacements if row["newScore"] < score
        ],
        "verdict": "R25_THREE_ACTIVE_AND_R26_RADIUS_THREE_FALSE",
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
