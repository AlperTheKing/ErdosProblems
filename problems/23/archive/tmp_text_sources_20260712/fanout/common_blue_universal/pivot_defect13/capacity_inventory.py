"""Exact numeric and compiled-surface inventory for the defect-13 fixture."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path[:0] = [str(ROOT / "tmp/fanout/pht_n12_direct"), str(ROOT / "problems/23/writeup")]
import n12_pht as n12  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    replay_path = HERE / "replay_defect13_result.json"
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    n, decoded = n12.dec(replay["fixture"]["g6"])
    info = n12.loads(n, decoded)
    assert info is not None
    blue = {tuple(edge) for edge in info["Bset"]}
    support = {tuple(edge) for edge in replay["active"]["support"]}
    active_vertices = set(replay["active"]["activeVertices"])
    off_support = blue - support
    component_boundary = {
        edge for edge in blue
        if (edge[0] in active_vertices) ^ (edge[1] in active_vertices)
    }
    off_support_boundary = off_support & component_boundary

    row_count = Counter()
    for row in replay["fixture"]["rows"]:
        row_count.update(row)
    active_degree = {int(k): v for k, v in replay["active"]["activeDegree"].items()}
    slack = {}
    for owner in (10, 11):
        selected_load = 5 * row_count[owner]
        raw = max(0, n - selected_load)
        degree = active_degree[owner]
        slack[owner] = {
            "selectedLoad": selected_load,
            "rawVertexSlack": raw,
            "activeDegree": degree,
            "consumedBeforeHitNeed": min(raw, degree),
            "remainingAfterActiveDegree": max(0, raw - degree),
            "hitNeed": max(0, degree - raw),
        }
    assert slack == {
        10: {"selectedLoad": 15, "rawVertexSlack": 0, "activeDegree": 2,
             "consumedBeforeHitNeed": 0, "remainingAfterActiveDegree": 0, "hitNeed": 2},
        11: {"selectedLoad": 10, "rawVertexSlack": 2, "activeDegree": 2,
             "consumedBeforeHitNeed": 2, "remainingAfterActiveDegree": 0, "hitNeed": 0},
    }
    assert len(off_support) == 8
    assert len(component_boundary) == 9
    assert not off_support_boundary

    files = {
        "residualSourceTokenization": ROOT / "problems/23/lean/Erdos23Delta0/ResidualSourceTokenization.lean",
        "endpointHalfDoorComplete": ROOT / "problems/23/lean/Erdos23Delta0/EndpointHalfDoorComplete.lean",
        "ell5DistancePrune": ROOT / "problems/23/lean/Erdos23Delta0/Ell5DistancePrune.lean",
        "typedFullBankSources": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean",
        "fullBankPortSinks": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean",
    }
    source_text = {name: path.read_text(encoding="utf-8") for name, path in files.items()}
    compiled = {
        "typedDoorCheckerPresent": "structure OwnEdgeDoorSourceData" in source_text["typedFullBankSources"],
        "typedDoorRequiresRaw25": "25 ≤ (D.token (D.doorOf p)).capQ" in source_text["typedFullBankSources"],
        "doorGraphConstructorPresent": "def ownEdgeDoorSourceDataOfGraph" in source_text["typedFullBankSources"],
        "portIncidenceExplicitlyAbsent": "legal edge-to-token incidence is still absent" in source_text["fullBankPortSinks"],
        "pruneCapSourceConstructorPresent": "| prune (prune : PruneKey)" in source_text["typedFullBankSources"],
        "distancePruneDefinesCapacityProvider": "capQ" in source_text["ell5DistancePrune"],
    }
    assert compiled == {
        "typedDoorCheckerPresent": True,
        "typedDoorRequiresRaw25": True,
        "doorGraphConstructorPresent": False,
        "portIncidenceExplicitlyAbsent": True,
        "pruneCapSourceConstructorPresent": True,
        "distancePruneDefinesCapacityProvider": False,
    }

    result = {
        "schema": "N12_DEFECT13_CAPACITY_INVENTORY_V1",
        "deficientShore": {"owners": [10, 11], "microDemand": 72, "commonBlueReach": 59, "defect": 13},
        "vertexSlack": {
            "owners": {str(owner): data for owner, data in slack.items()},
            "nonDoubleCountedRemaining": sum(data["remainingAfterActiveDegree"] for data in slack.values()),
            "verdict": "ZERO_REMAINING_AT_DEFICIENT_OWNERS",
        },
        "door": {
            "allCutEdges": len(blue),
            "selectedSupportEdges": len(support),
            "globalOffSupportCutEdges": len(off_support),
            "globalOffSupportEdgeList": [list(edge) for edge in sorted(off_support)],
            "activeComponentBoundaryEdges": len(component_boundary),
            "componentBoundaryEdgeList": [list(edge) for edge in sorted(component_boundary)],
            "offSupportComponentBoundaryEdges": len(off_support_boundary),
            "offSupportComponentBoundaryEdgeList": [],
            "numericVerdict": "NO_OFF_SUPPORT_EXIT_DOOR_FOR_ACTIVE_COMPONENT",
        },
        "prune": {
            "compiledDistancePruneCapacityProvider": False,
            "verdict": "NO_CONCRETE_CAPACITY_PROVIDER_IN_ELL5_DISTANCE_PRUNE",
        },
        "compiledSurface": compiled,
        "scope": "Numeric inventory is not a FullBank repair: typed legal incidence and a graph-derived provider remain absent.",
        "sha256": {name: sha256(path) for name, path in files.items()} | {"replay": sha256(replay_path)},
    }
    output = HERE / "capacity_inventory_result.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "vertexSlackRemaining": result["vertexSlack"]["nonDoubleCountedRemaining"],
        "offSupportExitDoors": result["door"]["offSupportComponentBoundaryEdges"],
        "pruneProvider": result["prune"]["compiledDistancePruneCapacityProvider"],
        "resultSha256": sha256(output),
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
