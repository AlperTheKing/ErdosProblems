"""Exact replay of the canonical R29 all-anchor Door audit.

Raw candidates reproduce the historical r29_gate FreeHalf construction.
Compiled-admissible candidates require an instantiated legal-incidence bridge;
the repository currently supplies only the generic bridge types/theorems.
"""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
GATE = ROOT / "tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py"
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
PORTS = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean"
SOURCES = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean"
BRIDGE = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_gate():
    spec = importlib.util.spec_from_file_location("r29_owner_gate", GATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    m = load_gate()
    incidence = m.load_untrusted_incidence()
    rows, pair, load, support, active_edges, active_vertices, demand_edges, collision, hit = m.rebuild_scope(incidence)
    masks, reasons, companions = m.owner_sources(incidence, pair, active_edges, active_vertices)
    hist = Counter(masks.values())
    owners = {}
    for owner in m.OWNERS:
        raw = sum(count for mask, count in hist.items() if mask & (1 << owner))
        owners[str(owner)] = {
            "raw_candidate_count": raw,
            "raw_capacity_units": raw,
            "raw_capacity_rational": str(raw),
            "compiled_admissible_count": 0,
            "compiled_admissible_capacity_units": 0,
            "compiled_admissible_capacity_rational": "0",
            "collision_demand": collision.get(owner, 0),
            "hit_need": hit.get(owner, 0),
            "total_demand": collision.get(owner, 0) + hit.get(owner, 0),
            "companion_count": len(companions[owner]),
        }
    cert = {
        "schema": "r29-fullbank-door-audit-v1",
        "arithmetic": "integers and exact rational strings only",
        "payload": {
            "n": incidence["n"], "blue_edges": len(incidence["blue"]),
            "bad_edges": len(incidence["bad"]), "rows": len(rows),
            "canonical_incidence_sha256": m.incidence_sha(incidence),
            "all_anchor": True,
        },
        "raw_freehalf_candidates": {
            "distinct_union": len(masks),
            "capacity_units_if_unit_sink_is_assumed": len(masks),
            "owner_mask_histogram": {str(k): v for k, v in sorted(hist.items())},
            "same_first_only": sum(v for k, v in Counter(reasons.values()).items() if k == 1),
            "row_companion_only": sum(v for k, v in Counter(reasons.values()).items() if k == 2),
        },
        "owners": owners,
        "compiled_legal_incidence": {
            "admissible_distinct_union": 0,
            "capacity_units": 0,
            "status": "no R29 OwnEdgeDoorSourceData.Checked plus DoorWallAdapter instantiation found",
            "own_edge_incidence": "not graph-derived by the compiled interface",
            "reason": "FullBankPortSinks explicitly has no legal edge-to-token incidence; TypedOwnDoorHalfLayer derives legality only after supplied typed data and adapter obligations.",
        },
        "assumptions_rejected_for_admissibility": [
            "each graph-derived FreeHalf triple is a Door token",
            "each raw candidate has Hall capacity one",
            "the FreeHalf edge/triple key equals a typed extractor exit-edge key",
            "a typed ledger token embeds into the real wall Sink while preserving capacity",
        ],
        "source_sha256": {str(p.relative_to(ROOT)).replace('\\\\', '/'): sha256(p) for p in (LEAD, GATE, PORTS, SOURCES, BRIDGE)},
    }
    out = HERE / "door_certificate.json"
    out.write_text(json.dumps(cert, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(cert, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
