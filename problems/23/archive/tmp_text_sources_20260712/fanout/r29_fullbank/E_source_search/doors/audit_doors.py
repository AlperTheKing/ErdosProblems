"""Exact R29 restriction-exit Door census under compiled typed semantics."""
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
TYPED = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean"
ADAPTER = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/TypedOwnDoorHalfLayer.lean"
SINKS = ROOT / "problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    spec = importlib.util.spec_from_file_location("r29", LEAD)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    d = mod.build()

    rows = tuple(tuple(r) for r in d["rows"])
    core = {v for r in rows for v in r}
    support = {mod.edge(x, y) for r in rows for x, y in zip(r, r[1:])}
    off_support = set(d["blue"]) - support
    exits = sorted(e for e in off_support if (e[0] in core) ^ (e[1] in core))
    internal = sorted(e for e in off_support if e[0] in core and e[1] in core)
    external = sorted(e for e in off_support if e[0] not in core and e[1] not in core)

    assert len(core) == 2803
    assert len(support) == 2797
    assert len(off_support) == 4242
    assert (len(exits), len(internal), len(external)) == (56, 4074, 112)
    assert len(exits) == len(set(exits))

    ports = []
    inside_hist = Counter()
    for i, e in enumerate(exits):
        inside = e[0] if e[0] in core else e[1]
        outside = e[1] if e[0] in core else e[0]
        inside_hist[inside] += 1
        ports.append({"port": i, "exit_edge_key": list(e), "inside": inside,
                      "outside": outside, "load": "1/2"})

    total_load = sum((Fraction(1, 2) for _ in ports), Fraction())
    assert total_load == 28
    # The owner shore is {0,1,2}; none of its vertices is an endpoint of a
    # restriction-exit port, so these ports do not supply owner incidence.
    assert all(0 not in e and 1 not in e and 2 not in e for e in exits)

    # Repository-wide production search, deliberately excluding audit outputs,
    # found no concrete R29 OwnEdgeDoorSourceData/adapter instantiation.  The
    # compiled APIs therefore justify keys and conditional checks, but no token.
    cert = {
        "schema": "r29-typed-restriction-exit-door-census-v1",
        "payload": {"n": d["n"], "rows": len(rows), "core_vertices": len(core),
                    "selected_support": len(support), "off_support": len(off_support)},
        "door_universe": {
            "definition": "blue-minus-selected-support edges with exactly one endpoint in the all-anchor core",
            "restriction_exit_keys": len(exits),
            "internal_off_support_rejected": len(internal),
            "external_off_support_rejected": len(external),
            "ports": ports,
            "inside_port_degree": {str(k): v for k, v in sorted(inside_hist.items())},
            "source_key_injective": True,
            "proof": "ports are indexed by distinct normalized graph edges; portEdge is the identity on this finite set",
        },
        "incidence": {
            "load_per_port": "1/2", "total_port_load": str(total_load),
            "hub_owner_shore": [0, 1, 2], "ports_incident_to_hub_owner_shore": 0,
            "typed_own_incidence_rule": "token.source = CapSource.door(portEdge(port))",
        },
        "compiled_capacity": {
            "realized_r29_typed_tokens": 0, "available_hall_cap": "0",
            "conditional_raw_cap_per_key": "at least 25",
            "conditional_hall_cap_per_key": "at least 1",
            "conditional_total_hall_cap": "at least 56",
            "conditional_spend_per_key": "1/2",
            "conditional_no_double_spend": "one distinct token per injective key; 1/2 <= 1",
            "blocker": "no concrete R29 OwnEdgeDoorSourceData.Checked and DoorWallAdapter instantiation exists",
        },
        "absorber": {
            "target": "28", "smallest_if_typed_tokens_existed": 28,
            "explanation": "28 ports would provide 28 capacity units, but all 56 ports are needed to route the exact 28 half-unit port load",
            "realized_absorbed_units": "0", "status": "not justified",
        },
        "hall_dual_certificate": {
            "left_set": "all 56 justified restriction-exit ports", "left_demand": "28",
            "compiled_realized_neighbor_tokens": 0, "neighbor_capacity": "0",
            "defect": "28", "dual_weights": "y_p=1 for every port; z_t=1 for every realized neighbor (empty)",
        },
        "sha256": {str(p.relative_to(ROOT)).replace("/", "\\"): sha(p)
                   for p in (LEAD, TYPED, ADAPTER, SINKS)},
    }
    out = HERE / "door_certificate.json"
    out.write_text(json.dumps(cert, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"certificate_sha256": sha(out), "restriction_exits": len(exits),
                      "port_load": str(total_load), "realized_cap": 0,
                      "hall_defect": 28}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
