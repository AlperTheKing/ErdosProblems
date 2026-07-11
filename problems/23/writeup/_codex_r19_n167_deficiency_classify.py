"""Classify the exact N167 base-transfer Hall deficiency.

This companion to ``_codex_r19_n167_base_transfer_gate.py`` varies only the
common-blue switch threshold.  It reports which smallest relaxation would
close the locked cage, without asserting that a negative-adjusted-surplus
relation is sound.  It also counts the original common-bad-neighbour pairs.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter

import _codex_r19_n167_base_transfer_gate as gate


OWNERS = {0, 23, 24, 25}


def candidates_at_threshold(
    owner, count, component, blue, bad, blue_adj, bad_adj, threshold,
    include_common_bad, include_common_mixed,
):
    relation = {}
    for y in sorted(component):
        if count[owner][y] == 0:
            relation[(owner, y, 0)] = "sameOwner"
            relation[(owner, y, 1)] = "sameOwner"

    for x in sorted(blue_adj[owner] & component):
        for y in sorted(blue_adj[owner] & component):
            if x == y or count[x][y] != 0:
                continue
            delta_blue, delta_bad = gate.switch_counts(blue, bad, {x, y})
            adjusted = delta_blue - delta_bad - 2
            if adjusted < threshold:
                continue
            relation.setdefault((x, y, 0), f"commonBlue[{adjusted}]")
            relation.setdefault((x, y, 1), f"commonBlue[{adjusted}]")

    if include_common_bad:
        for x in sorted(bad_adj[owner] & component):
            for y in sorted(bad_adj[owner] & component):
                if x == y or count[x][y] != 0:
                    continue
                delta_blue, delta_bad = gate.switch_counts(blue, bad, {x, y})
                loss = delta_blue - delta_bad
                if loss < 0:
                    continue
                relation.setdefault((x, y, 0), f"commonBad[{loss}]")
                relation.setdefault((x, y, 1), f"commonBad[{loss}]")

    if include_common_mixed:
        for x in sorted(blue_adj[owner] & component):
            for y in sorted(bad_adj[owner] & component):
                if x == y or count[x][y] != 0:
                    continue
                delta_blue, delta_bad = gate.switch_counts(blue, bad, {x, y})
                loss = delta_blue - delta_bad
                if loss < 0:
                    continue
                relation.setdefault((x, y, 0), f"commonMixed[{loss}]")
                relation.setdefault((x, y, 1), f"commonMixed[{loss}]")
                relation.setdefault((y, x, 0), f"commonMixed[{loss}]")
                relation.setdefault((y, x, 1), f"commonMixed[{loss}]")
    return relation


def main():
    n_vertices, blue, bad, active_edges, rows = gate.build_fixture()
    count = gate.multiplicities(n_vertices, rows)
    component = set().union(*(set(row) for row in rows))
    assert component == set(range(27))
    demands = gate.owner_demands(count, component, active_edges)
    blue_adj = gate.adjacency(n_vertices, blue)
    bad_adj = gate.adjacency(n_vertices, bad)

    owner_stats = {}
    for owner in sorted(OWNERS):
        free = sum(count[owner][z] == 0 for z in component)
        collisions = sum(max(0, count[owner][z] - 1) for z in component)
        hit_half = sum(d[0] == "hit" for d in demands[owner])
        total_row_mass = sum(count[owner][z] for z in component)
        assert free - collisions == len(component) - total_row_mass
        owner_stats[str(owner)] = {
            "T": total_row_mass,
            "freeCells": free,
            "collisionCells": collisions,
            "hitHalf": hit_half,
            "demandHalf": len(demands[owner]),
            "signedResidual": free - collisions,
        }

    threshold_results = []
    for threshold, include_common_bad, include_common_mixed in (
        (0, False, False), (-1, False, False), (-2, False, False),
        (0, True, False), (0, True, True)
    ):
        candidates = {
            owner: candidates_at_threshold(
                owner, count, component, blue, bad, blue_adj, bad_adj,
                threshold, include_common_bad, include_common_mixed
            )
            for owner in demands
        }
        matching, unmatched = gate.full_matching(demands, candidates)
        hall_summary = None
        if unmatched:
            hall_left, hall_right = gate.hall_witness(
                demands, candidates, matching, unmatched
            )
            hall_summary = {
                "left": len(hall_left),
                "right": len(hall_right),
                "deficiency": len(hall_left) - len(hall_right),
                "ownerHistogram": {
                    str(k): v for k, v in sorted(
                        Counter(owner for owner, _index in hall_left).items()
                    )
                },
                "kindHistogram": dict(sorted(Counter(
                    demands[owner][index][0]
                    for owner, index in hall_left
                ).items())),
            }
        owner_union = {
            source for owner in OWNERS for source in candidates[owner]
        }
        relation_hist = Counter()
        for source in owner_union:
            labels = {
                candidates[owner][source]
                for owner in OWNERS
                if source in candidates[owner]
            }
            relation_hist["+".join(sorted(labels))] += 1
        threshold_results.append({
            "threshold": threshold,
            "includeCommonBad": include_common_bad,
            "includeCommonMixed": include_common_mixed,
            "matched": len(matching),
            "unmatched": len(unmatched),
            "hallWitness": hall_summary,
            "fourOwnerDemand": sum(len(demands[o]) for o in OWNERS),
            "fourOwnerNeighborHalfSlots": len(owner_union),
            "fourOwnerDeficiency":
                sum(len(demands[o]) for o in OWNERS) - len(owner_union),
            "fourOwnerRelationHistogram": dict(sorted(relation_hist.items())),
        })

    common_bad_pairs = {}
    for owner in sorted(OWNERS):
        pairs = []
        for x in sorted(bad_adj[owner] & component):
            for y in sorted(bad_adj[owner] & component):
                if x == y or count[x][y] != 0:
                    continue
                delta_blue, delta_bad = gate.switch_counts(blue, bad, {x, y})
                pairs.append((x, y, delta_blue - delta_bad))
        common_bad_pairs[str(owner)] = {
            "orderedFreePairs": len(pairs),
            "lossHistogram": dict(sorted(Counter(loss for _, _, loss in pairs).items())),
        }

    payload = {
        "N": n_vertices,
        "componentN": len(component),
        "owners": owner_stats,
        "thresholds": threshold_results,
        "commonBad": common_bad_pairs,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["recordSHA256"] = hashlib.sha256(canonical.encode()).hexdigest()
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
