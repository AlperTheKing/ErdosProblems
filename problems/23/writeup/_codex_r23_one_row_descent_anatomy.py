"""Anatomy of the first active-scoped Hall failures and their one-row descent.

This is a proof-design probe, not an additional census.  It expands the first
N=10/N=11 falsifier fixtures from the exact R23 census, finds every Hamming-one
row replacement, and reports the unique score components changed by a best
strict descent.
"""

from __future__ import annotations

from _codex_r19_global_base_census import dec, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_outside_attachment_full_obligation_gate import edge, full_owner_flow


FIXTURES = (
    ("I?`fBO]]?", (1, 1, 1)),
    ("J?BEFboL`{?", (0, 0, 0, 7)),
    ("J?bFF`wN?{?", (0, 0, 0, 0)),
)


def score_parts(n, info, rows):
    counts = {}
    selected = set()
    support = set()
    for row in rows:
        selected.update(row)
        support.update(edge(x, y) for x, y in zip(row, row[1:]))
        for x in row:
            for y in row:
                counts[(x, y)] = counts.get((x, y), 0) + 1
    collisions = sum(max(0, value - 1) for value in counts.values())
    covered = sum(value > 0 for value in counts.values())
    active = {
        e for e in info["Bset"]
        if e[0] in selected and e[1] in selected and e not in support
    }
    return {
        "collisionUnits": collisions,
        "coveredPairs": covered,
        "activeEdges": sorted(active),
        "score": 2 * collisions + 2 * len(active),
        "counts": counts,
    }


def analyze(g6, choice):
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    assert info is not None
    families = shortest_row_families(info)
    rows = tuple(families[i][choice[i]] for i in range(len(choice)))
    old = score_parts(n, info, rows)
    old_flow = full_owner_flow(
        n, set(info["Bset"]), set(info["Mset"]), rows, g6,
        require_full=False, quiet=True, scope="active", include_outside=False
    )
    assert not old_flow["full"]

    candidates = []
    for index, family in enumerate(families):
        for replacement, row in enumerate(family):
            if replacement == choice[index]:
                continue
            new_rows = list(rows)
            new_rows[index] = row
            new_rows = tuple(new_rows)
            parts = score_parts(n, info, new_rows)
            if parts["score"] < old["score"]:
                flow = full_owner_flow(
                    n, set(info["Bset"]), set(info["Mset"]), new_rows, g6,
                    require_full=False, quiet=True, scope="active",
                    include_outside=False
                )
                candidates.append((parts["score"], index, replacement, row, parts, flow))
    assert candidates
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    new_score, index, replacement, row, new, new_flow = candidates[0]

    lost_covered = sorted(
        pair for pair, value in old["counts"].items()
        if value > 0 and new["counts"].get(pair, 0) == 0
    )
    gained_covered = sorted(
        pair for pair, value in new["counts"].items()
        if value > 0 and old["counts"].get(pair, 0) == 0
    )
    print({
        "g6": g6,
        "order": n,
        "oldChoice": choice,
        "changedBadEdge": info["M"][index],
        "oldRow": rows[index],
        "newRowIndex": replacement,
        "newRow": row,
        "oldScore": old["score"],
        "newScore": new_score,
        "oldCollisionUnits": old["collisionUnits"],
        "newCollisionUnits": new["collisionUnits"],
        "oldActive": old["activeEdges"],
        "newActive": new["activeEdges"],
        "lostCovered": lost_covered,
        "gainedCovered": gained_covered,
        "oldFlow": old_flow,
        "newFlow": new_flow,
        "strictOneRowChoices": len(candidates),
    })


def main():
    for fixture in FIXTURES:
        analyze(*fixture)


if __name__ == "__main__":
    main()
