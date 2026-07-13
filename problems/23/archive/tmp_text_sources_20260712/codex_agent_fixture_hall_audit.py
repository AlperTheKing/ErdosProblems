from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRITEUP = ROOT / "problems" / "23" / "writeup"
sys.path.insert(0, str(WRITEUP))

from _codex_internal_offsupport_gate import endpoint_flow_hall_margin
from _codex_internal_offsupport_resume import graph_records
from _codex_k2t_switch_probe import adj_from_edges
from _codex_singleton_vertexslack_gate import geos_paths, residuals, structured_records


def norm_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def internal_gate_record(record):
    name, n, edges, side = record
    adj = adj_from_edges(n, edges)
    cd = residuals(n, adj, side)
    assert cd is not None

    core = set()
    short = set()
    for a, b in cd["M"]:
        paths = geos_paths(adj, side, a, b)
        assert paths
        for path in paths:
            core.update(path)
            short.update(norm_edge(path[i], path[i + 1]) for i in range(len(path) - 1))

    cut_edges = {
        (u, v)
        for u in range(n)
        for v in adj[u]
        if u < v and side[u] != side[v]
    }
    outside = {e for e in cut_edges if (e[0] in core or e[1] in core) and e not in short}
    internal = {e for e in outside if e[0] in core and e[1] in core}
    boundary = outside - internal

    vertices = sorted(core)
    index = {v: i for i, v in enumerate(vertices)}
    remapped = {(index[u], index[v]) for u, v in internal}
    loads = [cd["T"][v] for v in vertices]
    margin, mask, caps = endpoint_flow_hall_margin(
        len(vertices), remapped, loads, ambient_n=n
    )
    return {
        "name": name,
        "ambientN": n,
        "atoms": len(cd["M"]),
        "coreVertices": vertices,
        "shortEdges": len(short),
        "outsideEdges": len(outside),
        "internalOffSupport": sorted(internal),
        "boundaryPorts": len(boundary),
        "gateMinMargin": str(margin),
        "gateMinSubset": [vertices[i] for i in range(len(vertices)) if (mask >> i) & 1],
        "violating": margin < 0,
        "zeroCapCoreVertices": [vertices[i] for i, cap in enumerate(caps) if cap == 0],
    }


def main():
    m15 = []
    for n in range(8, 16):
        rows = graph_records(n, 15)
        m15.append({"n": n, "records": len(rows), "unique": len(set(rows))})
    print("M15_REGENERATED", json.dumps(m15, separators=(",", ":")))
    print("M15_TOTAL", sum(x["records"] for x in m15), sum(x["unique"] for x in m15))

    wanted = {"canonical24", "canonical24+waistDoor", "canonical359"}
    for record in structured_records():
        if record[0] in wanted:
            print("FIXTURE", json.dumps(internal_gate_record(record), separators=(",", ":")))


if __name__ == "__main__":
    main()
