"""Exact N167 R19 base-transfer gate with GLOBAL Free sources.

The earlier `_codex_r19_n167_base_transfer_gate.py` restricted source pairs to
the 27-vertex active row component.  R18 established that this restriction is
invalid: overloaded components may import permanently-Free mass from outside.
This gate keeps the same sound same-owner/common-blue terminal rules but lets
source vertices range over all 167 graph vertices.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _codex_pro_active_cycle_counterexample_verify import adjacency  # noqa: E402
from _codex_r19_n167_base_transfer_gate import (  # noqa: E402
    Source,
    build_fixture,
    full_matching,
    hall_witness,
    multiplicities,
    owner_demands,
    switch_counts,
)


def global_source_candidates(owner, count, blue, bad, blue_adj):
    relation: dict[Source, str] = {}
    n_vertices = len(count)

    # Pointwise cancellation may use every globally Free ordered pair with
    # first coordinate equal to the owner.
    for y in range(n_vertices):
        if count[owner][y] == 0:
            relation[(owner, y, 0)] = "sameOwner"
            relation[(owner, y, 1)] = "sameOwner"

    # External c5Base transfers may use any two distinct common blue
    # neighbours of the destination owner, including private path vertices.
    neighbours = sorted(blue_adj[owner])
    for x in neighbours:
        for y in neighbours:
            if x == y or count[x][y] != 0:
                continue
            delta_blue, delta_bad = switch_counts(blue, bad, {x, y})
            if delta_blue - delta_bad - 2 < 0:
                continue
            relation.setdefault((x, y, 0), "c5Base")
            relation.setdefault((x, y, 1), "c5Base")
    return relation


def main():
    n_vertices, blue, bad, active_edges, rows = build_fixture()
    count = multiplicities(n_vertices, rows)
    component = set().union(*(set(row) for row in rows))
    assert component == set(range(27))
    demands = owner_demands(count, component, active_edges)
    blue_adj = adjacency(n_vertices, blue)
    candidates = {
        owner: global_source_candidates(owner, count, blue, bad, blue_adj)
        for owner in demands
    }

    matching, unmatched = full_matching(demands, candidates)
    assert len(set(matching.values())) == len(matching)

    if unmatched:
        hall_left, hall_right = hall_witness(
            demands, candidates, matching, unmatched
        )
        payload = json.dumps({
            "left": sorted(hall_left),
            "right": sorted(hall_right),
        }, separators=(",", ":")).encode()
        print(json.dumps({
            "N": n_vertices,
            "sourceScope": "all vertices",
            "totalHalfDemands": sum(map(len, demands.values())),
            "maximumMatched": len(matching),
            "unmatched": len(unmatched),
            "hallLeft": len(hall_left),
            "hallRight": len(hall_right),
            "hallDeficiency": len(hall_left) - len(hall_right),
            "hallWitnessSHA256": hashlib.sha256(payload).hexdigest(),
            "verdict": "global base-only transfer relation is Hall-deficient",
        }, sort_keys=True, separators=(",", ":")))
        return

    relation_hist = Counter()
    external_sources = 0
    records = []
    for node, source in sorted(matching.items()):
        owner, _index = node
        relation = candidates[owner][source]
        relation_hist[relation] += 1
        x, y, _half = source
        assert count[x][y] == 0
        if x not in component or y not in component:
            external_sources += 1
        if relation == "sameOwner":
            assert x == owner
        else:
            assert owner in blue_adj[x] and owner in blue_adj[y]
            delta_blue, delta_bad = switch_counts(blue, bad, {x, y})
            assert delta_blue - delta_bad - 2 >= 0
        records.append((node, source, relation))

    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    print(json.dumps({
        "N": n_vertices,
        "componentN": len(component),
        "sourceScope": "all vertices",
        "totalHalfDemands": sum(map(len, demands.values())),
        "matched": len(matching),
        "externalSourcesUsed": external_sources,
        "relationHistogram": dict(sorted(relation_hist.items())),
        "minimumCandidateHalfSlots": min(map(len, candidates.values())),
        "matchingSHA256": hashlib.sha256(payload).hexdigest(),
        "verdict": "global base-only transfer relation matches every obligation",
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
