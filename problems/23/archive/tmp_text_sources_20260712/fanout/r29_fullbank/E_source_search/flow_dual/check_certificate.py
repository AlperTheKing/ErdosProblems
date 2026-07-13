#!/usr/bin/env python3
"""Exact checker for the conservative, proved-incidence R29 FullBank flow."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
KINDS = {"door", "vertexSlack", "c5Base", "prune"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value):
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    raise TypeError("rational fields must be JSON integers or strings")


def check(data):
    assert data["schema"] == "r29_fullbank_residual_flow_v1"
    ref = data["provenance"]["ownerHallCertificate"]
    owner_path = ROOT / ref["path"]
    assert sha256(owner_path) == ref["sha256"]
    owner = json.loads(owner_path.read_text(encoding="utf-8"))

    demand = {k: q(v["demand"]) for k, v in owner["owners"].items()}
    assert demand == {"0": Fraction(6651), "1": Fraction(6651), "2": Fraction(6651)}
    alloc_raw = owner["flow_certificate_by_source_mask_to_owner"]
    alloc = {
        "0": q(alloc_raw["1->0"]) + q(alloc_raw["7->0"]),
        "1": q(alloc_raw["2->1"]) + q(alloc_raw["7->1"]),
        "2": q(alloc_raw["4->2"]) + q(alloc_raw["7->2"]),
    }
    residual = {k: demand[k] - alloc[k] for k in demand}
    assert residual == {"0": 0, "1": 0, "2": 28}
    assert {k: q(v) for k, v in data["baseline"]["residualDemand"].items()} == residual

    tokens = data["provedTokens"]
    arcs = data["provedArcs"]
    token_ids = [t["id"] for t in tokens]
    assert len(token_ids) == len(set(token_ids))
    assert all(t["kind"] in KINDS and q(t["capacity"]) >= 0 for t in tokens)
    assert len({(t["component"], t["kind"], t["source"]) for t in tokens}) == len(tokens)
    assert all(a["token"] in token_ids and q(a["capacity"]) >= 0 for a in arcs)

    # Unknown semantic incidences are metadata, never arcs of the certified network.
    unknown = data["unknownSemanticIncidences"]
    assert {x["kind"] for x in unknown} == KINDS
    assert all(x["status"] in {"unknown_not_absent", "proved_absent_in_audited_tuple"} for x in unknown)
    assert {x["kind"] for x in unknown if x["status"] == "unknown_not_absent"} == {
        "door", "vertexSlack", "c5Base"
    }
    assert data["provedAbsent"]["pruneTokens"]["count"] == 0

    cert = data["certificate"]
    hall_nodes = cert["hallDemandSet"]
    assert hall_nodes == ["owner:2:residual"]
    hall_demand = residual["2"]
    neighbor_ids = {a["token"] for a in arcs if a["demand"] in hall_nodes}
    capacities = {t["id"]: q(t["capacity"]) for t in tokens}
    neighbor_capacity = sum((capacities[t] for t in neighbor_ids), Fraction())
    assert neighbor_ids == set(cert["neighborTokens"])
    assert hall_demand == q(cert["demand"]) == 28
    assert neighbor_capacity == q(cert["neighborCapacity"]) == 0
    assert q(cert["defect"]) == hall_demand - neighbor_capacity == 28
    assert q(cert["maxFlow"]) == 0
    assert q(cert["minCutCapacity"]) == neighbor_capacity == 0
    assert {k: q(v) for k, v in cert["farkasMultiplier"].items()} == {hall_nodes[0]: 1}
    assert neighbor_capacity < hall_demand  # exact Hall/Farkas contradiction
    return {
        "ok": True,
        "arithmetic": "fractions.Fraction",
        "ownerHallSha256": sha256(owner_path),
        "provedTokenCount": len(tokens),
        "provedArcCount": len(arcs),
        "unknownKinds": ["door", "vertexSlack", "c5Base"],
        "provedAbsentKinds": ["prune"],
        "residualDemand": str(hall_demand),
        "maxFlow": "0",
        "minCutCapacity": str(neighbor_capacity),
        "defect": str(hall_demand - neighbor_capacity),
    }


if __name__ == "__main__":
    path = HERE / "flow_instance.json"
    result = check(json.loads(path.read_text(encoding="utf-8")))
    result["instanceSha256"] = sha256(path)
    out = HERE / "check_result.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
