"""Reproduce the R32 K??E@cyjFgWk full-bank 78/78 certificate."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
P5_DIR = ROOT / "tmp" / "fanout" / "p5_n12_census"
FIXTURE = ROOT / "tmp" / "fanout" / "r29_fullbank_local" / "n12_first_micro_fixture.json"
sys.path.insert(0, str(PHT))
sys.path.insert(0, str(P5_DIR))
sys.path.insert(0, str(HERE))

import n12_pht as n12  # noqa: E402
import p5_core as p5  # noqa: E402
from collision_only_core import analyze_collision_only, canonical_sha  # noqa: E402


G6 = "K??E@cyjFgWk"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert fixture["g6"] == G6
    choice = tuple(fixture["choice"])
    n, edges = n12.dec(G6)
    info = n12.loads(n, edges)
    assert info is not None
    families = n12.shortest_row_families(info)
    rows = n12.rows_for_choice(families, choice)
    ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])
    result = analyze_collision_only(ctx, rows, details=True)

    state = result["state"]
    collision = {
        int(owner): amount
        for owner, amount in state["collisionByOwner"].items()
        if amount
    }
    hit_need = {
        int(owner): amount
        for owner, amount in state["hitNeedByOwner"].items()
        if amount
    }
    door_edges = {
        tuple(record["edge"]) for record in result["doorAssignmentSeparate"]
    }
    assigned = {tuple(record["source"]) for record in result["collisionAssignment"]}
    expected_reserved = {(10, 0, 0), (10, 2, 0)}
    companions_10 = {
        vertex
        for vertex in range(n)
        if vertex != 10 and state["pair"][10][vertex] > 0
    }

    checks = {
        "graphOrder12": n == 12,
        "familySizes": [len(family) for family in families] == [6, 5, 8, 10],
        "rowsMatchPinnedFixture": [list(row) for row in rows] == fixture["rows"],
        "activeScope": state["activeVertices"] == [0, 1, 2, 7, 10, 11],
        "collisionProfile": collision == {7: 6, 10: 14, 11: 8},
        "hitNeedProfile": hit_need == {10: 2},
        "companions10": {1, 5, 8}.issubset(companions_10),
        "reservedHalfZerosExcluded": expected_reserved.isdisjoint(assigned),
        "collisionPaid28": result["collisionDemand"] == result["collisionMatched"] == 28,
        "doorEdges": door_edges == {(0, 10), (2, 10)},
        "doorsPaid50": (
            result["hitNeedSlotsSeparate"] == result["doorMatchedSlots"] == 2
        ),
        "hitNeedExcludedFromHall": not result["hallDemandIncludesHitNeed"],
        "noCommonNeeded": result["commonBlueUsed"] == 0,
        "noPrune": result["pruneCheckedCapacity"] == 0,
        "micro78of78": (
            result["collisionMatched"] + 25 * result["doorMatchedSlots"] == 78
        ),
        "zeroDefect": result["collisionDefect"] == 0 and result["full"],
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"fixture checks failed: {failed}")

    payload = {
        "schema": "R32_N12_NO_COMMON_FIXTURE_V1",
        "verdict": "EXACT_NO_COMMON_COLLISION_28_OF_28_PLUS_DOORS_50",
        "g6": G6,
        "choice": list(choice),
        "familySizes": [len(family) for family in families],
        "checks": checks,
        "accounting": {
            "collisionDemand": result["collisionDemand"],
            "freeHalfMatched": result["collisionMatched"],
            "hallDemandIncludesHitNeed": result["hallDemandIncludesHitNeed"],
            "hitNeedSlotsSeparate": result["hitNeedSlotsSeparate"],
            "doorEdges": [list(edge) for edge in sorted(door_edges)],
            "doorCapacityEach": 25,
            "pruneCheckedCapacity": result["pruneCheckedCapacity"],
            "combinedDemandDiagnostic": (
                result["collisionDemand"] + 25 * result["hitNeedSlotsSeparate"]
            ),
            "combinedMatchedDiagnostic": (
                result["collisionMatched"] + 25 * result["doorMatchedSlots"]
            ),
        },
        "sourceLedger": {
            "sourceKeys": result["sourceKeys"],
            "p13Keys": result["p13Keys"],
            "p4Keys": result["p4Keys"],
            "p5Keys": result["p5Keys"],
            "commonCandidates": result["commonBlueCandidates"],
            "commonUsed": result["commonBlueUsed"],
            "newReservationEdges": result["newReservationEdges"],
            "coherenceLabels": result["coherenceLabels"],
            "collisionSearchNodes": result["searchNodes"],
            "reservedHalfZerosExcluded": [list(key) for key in sorted(expected_reserved)],
        },
        "collisionProfile": {str(k): v for k, v in sorted(collision.items())},
        "hitNeedProfile": {str(k): v for k, v in sorted(hit_need.items())},
        "collisionAssignment": result["collisionAssignment"],
        "doorAssignmentSeparate": result["doorAssignmentSeparate"],
        "sha256": {
            "inputFixture": sha256(FIXTURE),
            "n12Pht": sha256(PHT / "n12_pht.py"),
            "p5Core": sha256(HERE.parent / "p5_n12_census" / "p5_core.py"),
            "fullbankCore": sha256(HERE / "fullbank_core.py"),
            "collisionCore": sha256(HERE / "collision_only_core.py"),
        },
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    output = HERE / "fixture_no_common.json"
    output.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii"
    )
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
