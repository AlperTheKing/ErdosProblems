"""Exact R29 row-partition and zero-surplus audit.

This does not claim a FullBank provider.  It checks whether the standalone
R29 graph is even in the Branch-B domain of the production component-level
row partition.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
R29 = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
ROW_PARTITION = ROOT / "problems/23/lean/Erdos23Delta0/RowPartitionCore.lean"
ROW_PROVIDER = ROOT / "problems/23/lean/Erdos23Delta0/Rows/RowPartition.lean"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_r29():
    spec = importlib.util.spec_from_file_location("r29_lead_gate", R29)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    r29 = load_r29()
    data = r29.build()
    n = data["n"]
    m = len(data["bad"])

    # Every listed row and every shortest-row family has ell = five.
    listed_ell_hist = Counter(len(row) for row in data["rows"])
    assert listed_ell_hist == Counter({5: 1383})
    adj_blue = r29.adjacency(n, data["blue"])
    distance_hist = Counter()
    path_count_hist = Counter()
    for atom in data["atoms"]:
        dist, path_count = r29.bfs(adj_blue, atom[0])
        d = dist[atom[1]]
        assert d == 4
        distance_hist[d] += 1
        path_count_hist[path_count[atom[1]]] += 1
    assert distance_hist == Counter({4: 1383})
    assert path_count_hist == Counter({1: 707, 680: 676})

    # Replace every selector with the exact all-anchor representative used by
    # the Hall falsifier.  This changes no row length and no row surplus.
    anchor_rows = list(data["rows"])
    for i, meta in enumerate(data["selectorMeta"]):
        anchor_rows[data["selectorStart"] + i] = meta["anchorRow"]
    anchor_ell_hist = Counter(len(row) for row in anchor_rows)
    assert anchor_ell_hist == Counter({5: 1383})
    length_surplus = sum(len(row) ** 2 - 25 for row in anchor_rows)
    assert length_surplus == 0

    selected = {v for row in anchor_rows for v in row}
    support = {
        r29.edge(u, v)
        for row in anchor_rows
        for u, v in zip(row, row[1:])
    }
    off_support_blue = data["blue"] - support
    assert len(selected) == 2127
    assert len(support) == 2797
    assert len(off_support_blue) == 4242

    residual = n * n - 25 * m
    hypothetical_all_door_capq = 25 * len(off_support_blue)
    assert residual == 8_626_674
    assert hypothetical_all_door_capq == 106_050

    result = {
        "verdict": "STANDALONE_R29_IS_COMPONENT_ALL_L5_NOT_BRANCH_B",
        "counts": {
            "n": n,
            "badEdges": m,
            "listedRows": len(data["rows"]),
            "selectedVerticesAllAnchor": len(selected),
            "selectedSupportBlueEdgesAllAnchor": len(support),
            "offSupportBlueEdgesAllAnchor": len(off_support_blue),
        },
        "rowFacts": {
            "listedEllHistogram": dict(sorted(listed_ell_hist.items())),
            "allAnchorEllHistogram": dict(sorted(anchor_ell_hist.items())),
            "shortestBlueDistanceHistogram": dict(sorted(distance_hist.items())),
            "shortestPathCountHistogram": dict(sorted(path_count_hist.items())),
            "lengthSurplusSum": length_surplus,
            "componentAllL5ForEveryComponentTable": True,
            "branchBRowsUnderProductionDispatch": 0,
        },
        "scaleFacts": {
            "globalResidualN2Minus25m": residual,
            "hypothetical25CapQPerOffSupportDoor": hypothetical_all_door_capq,
            "residualAfterHypotheticalAllDoors": residual - hypothetical_all_door_capq,
            "note": "Numeric room is not a graph-derived Door provider.",
        },
        "scopeConclusion": (
            "The exact 28-unit ActiveScoped Hall defect is not a standalone "
            "Branch-B/FullBank falsifier. To make it production-relevant one "
            "must embed this cage in a mixed K2 component and re-run all loads, "
            "source incidence, and component-reserve accounting."
        ),
        "sha256": {
            "r29LeadGate": sha256(R29),
            "rowPartitionCore": sha256(ROW_PARTITION),
            "rowPartitionProvider": sha256(ROW_PROVIDER),
            "canonicalR29Payload": hashlib.sha256(r29.canonical_bytes(data)).hexdigest(),
        },
    }
    out = Path(__file__).with_name("lead_dispatch_audit.json")
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
