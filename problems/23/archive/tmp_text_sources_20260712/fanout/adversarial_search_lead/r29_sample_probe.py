"""Deterministic diagnostic samples for reconstructed R29 selector products."""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R29 = ROOT / "tmp" / "fanout" / "r29_gate" / "lead"
sys.path.insert(0, str(R29))

from r29_lead_gate import adjacency, build, scoped_state, shortest_rows


def main():
    data = build()
    start, stop = data["selectorStart"], data["selectorStop"]
    adj = adjacency(data["n"], data["blue"])
    families = []
    for atom in data["atoms"][start:stop]:
        rows = shortest_rows(adj, *atom)
        anchors = [row for row in rows if 55 in row]
        locals_ = [row for row in rows if 55 not in row]
        assert len(anchors) == 676 and len(locals_) == 4
        families.append((anchors, locals_))

    fixed_positive = {0, 1, 2} | set(range(2762, 2784))
    records = []
    for seed in range(8):
        rng = random.Random(seed)
        rows = list(data["rows"])
        local_count = 0
        for index, (anchors, locals_) in enumerate(families):
            if rng.randrange(170) == 0:
                row = locals_[rng.randrange(4)]
                local_count += 1
            else:
                row = anchors[rng.randrange(676)]
            rows[start + index] = row
        state = scoped_state(data, tuple(rows))
        anchor_degree = sum(55 in edge for edge in state["demandedActive"])
        assert anchor_degree <= 4 + 2 * local_count
        positive = {
            v for v in state["activeVertices"]
            if state["collision"].get(v, 0) + state["hitNeed"].get(v, 0)
        }
        records.append({
            "seed": seed,
            "localRows": local_count,
            "score": state["score"],
            "collision": state["collisionTotal"],
            "hitNeed": state["hitNeedTotal"],
            "activeVertices": len(state["activeVertices"]),
            "activeTrafficLeaves": sorted(positive & set(range(3, 55))),
            "otherPositiveOwners": sorted(
                positive - fixed_positive - {55} - set(range(3, 55))
            ),
            "anchorDemand": (
                state["collision"].get(55, 0) + state["hitNeed"].get(55, 0)
            ),
            "anchorActiveDegree": anchor_degree,
            "qActive": [q for q in (2760, 2761) if q in state["activeVertices"]],
        })
    print(json.dumps(records, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
