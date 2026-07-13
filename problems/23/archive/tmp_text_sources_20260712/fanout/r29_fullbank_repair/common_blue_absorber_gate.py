"""Exact R29 gate for the already-compiled common-blue C5-base terminal.

The auxiliary ActiveScoped relation contains same-first and row-companion
sources.  CheckedC5BaseTransfer.TerminalData.Valid instead permits a free
ordered pair whose two vertices are blue-adjacent to the owner and whose
two-vertex switch has dB-dM >= 2.  This script adds exactly that existing
relation and recomputes all eight owner-shore Hall inequalities.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REBUILD = ROOT / "tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py"
TERMINAL_LEAN = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean"
OWNERS = (0, 1, 2)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    hall = load_module(REBUILD, "r29_owner_hall")
    I = hall.load_untrusted_incidence()
    (
        rows,
        pair,
        load,
        support,
        active_edges,
        active_vertices,
        active_demand_edges,
        collision,
        hit,
    ) = hall.rebuild_scope(I)
    del rows, load, support, active_demand_edges

    demand = {o: collision.get(o, 0) + hit.get(o, 0) for o in OWNERS}
    masks, reasons, companions = hall.owner_sources(
        I, pair, active_edges, active_vertices
    )
    old_masks = dict(masks)

    blue_adj = defaultdict(set)
    signed_degree = Counter()
    edge_sign = {}
    for u, v in I["blue"]:
        blue_adj[u].add(v)
        blue_adj[v].add(u)
        edge_sign[hall.norm(u, v)] = 1
        signed_degree[u] += 1
        signed_degree[v] += 1
    for u, v in I["bad"]:
        edge_sign[hall.norm(u, v)] = -1
        signed_degree[u] -= 1
        signed_degree[v] -= 1

    valid_by_owner = {o: [] for o in OWNERS}
    for o in OWNERS:
        assert o in active_vertices
        for x in sorted(blue_adj[o]):
            for y in sorted(blue_adj[o]):
                if x == y or pair[x, y] != 0:
                    continue
                switch_edge = hall.norm(x, y)
                sigma = (
                    signed_degree[x]
                    + signed_degree[y]
                    - 2 * edge_sign.get(switch_edge, 0)
                )
                if sigma < 2:
                    continue
                for half in (0, 1):
                    reserved = (
                        half == 0
                        and switch_edge in active_edges
                        and x in active_vertices
                    )
                    if reserved:
                        continue
                    source = (x, y, half)
                    masks[source] = masks.get(source, 0) | (1 << o)
                    reasons[source] = reasons.get(source, 0) | 4
                    valid_by_owner[o].append(
                        {
                            "x": x,
                            "y": y,
                            "half": half,
                            "sigma": sigma,
                            "alreadyOldEligible": bool(
                                old_masks.get(source, 0) & (1 << o)
                            ),
                        }
                    )

    # For three owners, all Hall cuts are an exact max-flow certificate.
    cuts = []
    max_defect = 0
    for shore_mask in range(8):
        shore = [o for o in OWNERS if shore_mask & (1 << o)]
        shore_demand = sum(demand[o] for o in shore)
        neighborhood = sum(
            1 for source_mask in masks.values() if source_mask & shore_mask
        )
        defect = shore_demand - neighborhood
        max_defect = max(max_defect, defect)
        cuts.append(
            {
                "shoreMask": shore_mask,
                "shore": shore,
                "demand": shore_demand,
                "neighborhood": neighborhood,
                "defect": defect,
            }
        )

    old_hist = Counter(old_masks.values())
    new_hist = Counter(masks.values())
    incremental_sources = set(masks) - set(old_masks)
    incremental_owner_arcs = sum(
        (masks[s] & ~old_masks.get(s, 0)).bit_count() for s in masks
    )

    # Minimal repair of the existing exact flow certificate: keep its old
    # allocation 5775+876, 5775+876, 5775+848 and add only 28 newly licensed
    # owner-2-exclusive common-blue sources.  All obligations at one owner
    # have the same owner-level availability relation.
    old_by_mask = {
        m: sorted(s for s, sm in old_masks.items() if sm == m)
        for m in (1, 2, 4, 7)
    }
    repair_candidates = sorted(
        s for s in incremental_sources if masks[s] == 4
    )
    assert len(repair_candidates) >= 28
    repair = repair_candidates[:28]
    shared = old_by_mask[7]
    allocation = {
        0: old_by_mask[1] + shared[:876],
        1: old_by_mask[2] + shared[876:1752],
        2: old_by_mask[4] + shared[1752:2600] + repair,
    }
    assert {o: len(allocation[o]) for o in OWNERS} == demand
    flattened = [s for o in OWNERS for s in allocation[o]]
    assert len(flattened) == len(set(flattened)) == sum(demand.values())
    assert all(masks[s] & (1 << o) for o in OWNERS for s in allocation[o])
    assert all(s not in old_masks and masks[s] == 4 for s in repair)
    repair_switch_counts = []
    for x, y, half in repair:
        switch = {x, y}
        d_b = sum((u in switch) ^ (v in switch) for u, v in I["blue"])
        d_m = sum((u in switch) ^ (v in switch) for u, v in I["bad"])
        assert d_m + 2 <= d_b
        repair_switch_counts.append(
            {"x": x, "y": y, "half": half, "dB": d_b, "dM": d_m,
             "adjustedSurplus": d_b - d_m - 2}
        )
    assert {(r["dB"], r["dM"], r["adjustedSurplus"])
            for r in repair_switch_counts} == {(30, 27, 1)}
    allocation_payload = {
        "schema": "owner-indexed injective source assignment; obligations may be indexed arbitrarily within owner",
        "ownerSources": {
            str(o): [list(s) for s in allocation[o]] for o in OWNERS
        },
        "minimalRepairSources": [list(s) for s in repair],
    }
    allocation_raw = json.dumps(
        allocation_payload, sort_keys=True, separators=(",", ":")
    ).encode()
    allocation_path = Path(__file__).with_name(
        "common_blue_minimal_allocation.json"
    )
    allocation_path.write_bytes(allocation_raw + b"\n")

    result = {
        "verdict": "PASS_COMMON_BLUE_ABSORBS" if max_defect <= 0 else "FAIL",
        "demandByOwner": demand,
        "oldDistinctSources": len(old_masks),
        "newDistinctSources": len(masks),
        "incrementalDistinctSources": len(incremental_sources),
        "incrementalOwnerArcs": incremental_owner_arcs,
        "oldMaskHistogram": dict(sorted(old_hist.items())),
        "newMaskHistogram": dict(sorted(new_hist.items())),
        "validCommonBlueByOwner": {
            str(o): {
                "records": len(valid_by_owner[o]),
                "newOwnerArcs": sum(
                    not r["alreadyOldEligible"] for r in valid_by_owner[o]
                ),
                "neighbors": sorted(blue_adj[o]),
                "sources": valid_by_owner[o],
            }
            for o in OWNERS
        },
        "cuts": cuts,
        "maximumDefect": max_defect,
        "minimalRepair": {
            "count": len(repair),
            "availableOwnerExclusiveCandidates": len(repair_candidates),
            "owner": 2,
            "sources": [list(s) for s in repair],
            "checkedTerminalRecords": repair_switch_counts,
            "allocationCounts": {
                str(o): len(allocation[o]) for o in OWNERS
            },
            "allocationSha256": hashlib.sha256(allocation_raw).hexdigest(),
        },
        "sha256": {
            "ownerHallRebuild": sha256(REBUILD),
            "checkedC5BaseTransferLean": sha256(TERMINAL_LEAN),
            "canonicalIncidence": hall.incidence_sha(I),
        },
        "scope": (
            "This proves only the finite source relation on R29. A production "
            "provider must still turn each matched HitNeed into a typed c5Base "
            "token and prove global source uniqueness/no-double-spend."
        ),
    }
    out = Path(__file__).with_name("common_blue_absorber_gate.json")
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": result["verdict"],
        "old": len(old_masks),
        "new": len(masks),
        "incremental": len(incremental_sources),
        "incrementalOwnerArcs": incremental_owner_arcs,
        "maximumDefect": max_defect,
        "cuts": cuts,
        "perOwner": {
            o: {
                "records": len(valid_by_owner[o]),
                "newOwnerArcs": sum(not r["alreadyOldEligible"] for r in valid_by_owner[o]),
            }
            for o in OWNERS
        },
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
