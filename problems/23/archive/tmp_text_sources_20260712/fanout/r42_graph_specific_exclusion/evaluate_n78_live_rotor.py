"""Exact production collision evaluation of the live N=78 R40 rotor states."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
P5 = ROOT / "tmp" / "fanout" / "p5_n12_census"
FULLBANK = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
for path in (WRITEUP, P5, FULLBANK):
    sys.path.insert(0, str(path))

import _claude_r40_n78_instance_gate as fixture  # noqa: E402
import p5_core as p5  # noqa: E402
from fullbank_core import (  # noqa: E402
    coherent_collision_match,
    collision_owners,
    project_masks,
)


def norm(edge):
    return tuple(sorted(edge))


def canonical_sha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main():
    blue = {norm(edge) for edge in fixture.blue}
    bad = {norm(edge) for edge in fixture.bad}
    ctx = p5.make_graph_context(fixture.N, blue, bad)
    records = []
    for index, rows in enumerate(fixture.states):
        state = p5.reconstruct_state(ctx, tuple(rows))
        masks = p5.relation_masks(ctx, state)
        owners = collision_owners(state)
        raw = project_masks(state, masks["five"], owners)
        result = coherent_collision_match(ctx, state, owners, raw, ())
        relation_counts = {
            name: len(masks[name]) for name in ("p13", "p2", "p4", "p5", "five")
        }
        owner_margins = []
        for owner_index, owner in enumerate(owners):
            bit = 1 << owner_index
            reach = sum(bool(mask & bit) for mask in raw.values())
            demand = state.collision[owner]
            owner_margins.append({
                "owner": owner,
                "demand": demand,
                "reach": reach,
                "margin": reach - demand,
            })
        records.append({
            "state": index,
            "activeVertices": len(state.active_vertices),
            "owners": len(owners),
            "collisionDemand": result.demand,
            "collisionMatched": result.matched,
            "collisionDefect": result.defect,
            "relationKeyCounts": relation_counts,
            "minimumOwnerMargin": min(
                (record["margin"] for record in owner_margins), default=0
            ),
            "ownerMargins": owner_margins,
            "matchingSearchNodes": result.search_nodes,
            "baseLabels": len(result.base_labels),
            "assignmentSha256": canonical_sha(result.assignment),
        })
    assert [r["collisionDemand"] for r in records] == [264, 180, 180, 264]
    assert all(r["collisionDefect"] == 0 for r in records)
    payload = {
        "schema": "R42_LIVE_N78_PRODUCTION_EVALUATION_V1",
        "states": records,
        "verdict": "PASS_ALL_FOUR_STATES_COLLISION_DEFECT_ZERO",
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    output = HERE / "n78_live_rotor.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        "verdict": payload["verdict"],
        "states": [
            [r["collisionDemand"], r["collisionMatched"], r["collisionDefect"],
             r["minimumOwnerMargin"]]
            for r in records
        ],
        "sha256": payload["canonicalPayloadSha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
