#!/usr/bin/env python3
"""Claims 5 / 3(empirical) / 6a on the archived hits #298 and #264.
Loads the ENGINE's archived packages (sha-verified), rebuilds everything from
graph6 with my own code, and re-decides vacuity + per-edge latent feasibility
solver-free; CP-SAT cross-checks capture UNSAT."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from v5_core import (  # noqa: E402
    available_atoms,
    build_adj,
    canonical_sha,
    capture_decision,
    classifier_vector,
    deletion_sdr_sizes,
    graph6_decode,
    is_connected,
    norm,
    supersaturation,
    triangle_count,
)
from v5_cpsat import gate_capture  # noqa: E402

BASE = Path(r"E:\Projects\ErdosProblems\tmp\fanout\r42_graph_specific_exclusion")
PACKAGES = {
    "298": BASE / "t5_classifier_v_l9_r9_1000.json",
    "264": BASE / "t5_live_x_classifier_v_l9_r9_5000.json",
}
EXPECT_G6 = {
    "298": "Q??????wE_[?EGs?D_@A?C_B???",
    "264": "Q??????wE_Bws?s?DCD??@?@???",
}

out = {}
for name, path in PACKAGES.items():
    print(f"===== hit #{name} =====")
    src = json.loads(path.read_text(encoding="utf-8"))
    claimed = src.pop("canonicalSha256")
    ok_sha = canonical_sha(src) == claimed
    print("package sha ok:", ok_sha)
    hit = src["hit"]
    g6 = hit["graph6"]
    print("graph6 matches writeup:", g6 == EXPECT_G6[name])
    n, edges = graph6_decode(g6)
    left_n, right_n = src["left"], src["right"]
    assert n == left_n + right_n == 18
    edges = sorted(map(tuple, edges))
    assert edges == sorted(map(tuple, (norm(*e) for e in hit["supportEdges"])))
    adj = build_adj(n, edges)
    assert is_connected(adj, n) and len(edges) == 24

    atoms_all = available_atoms(n, edges, left_n)
    by_pair = {(a["u"], a["v"]): a for a in atoms_all}
    chosen_atoms = []
    rows_match = True
    for rec in hit["selectedAtoms"]:
        a = by_pair[(rec["u"], rec["v"])]
        if sorted(map(tuple, rec["rows"])) != a["rows"]:
            rows_match = False
        if sorted(map(tuple, rec["footprintEdges"])) != a["footprint"]:
            rows_match = False
        chosen_atoms.append(a)
    print("selectedAtoms rows+footprints == my recomputation:", rows_match)
    assert len(chosen_atoms) == 25

    bad = [(a["u"], a["v"]) for a in chosen_atoms]
    tri = triangle_count(n, edges + bad)
    sdr = deletion_sdr_sizes(chosen_atoms, edges)
    mult_min = min(
        sum(tuple(e) in set(map(tuple, a["footprint"])) for a in chosen_atoms)
        for e in edges
    )
    owner = 0
    active = hit["selectionMeta"]["localClassifiers"]["0"]["activeNeighbour"]
    vec = classifier_vector(chosen_atoms, adj, owner, active)
    vec4 = [vec[k] for k in ("eForced", "iStep", "dStep", "dCoverage")]
    print(
        f"axioms: tri={tri} sdr_all24={sdr == [24]*25} muMin={mult_min} "
        f"classifier={vec4} active={active}"
    )

    # solver-free capture decision + per-edge map
    has_cap, wits, feas = capture_decision(chosen_atoms, adj, owner, active, n)
    feas_edges = sorted(e for e, ok in feas.items() if ok)
    print("capture (factored, exact):", has_cap, "| witnesses:", len(wits))
    print("per-edge latent-feasible edges:", feas_edges)
    only_vx0 = feas_edges == [norm(owner, active)]
    print("per-edge latent-feasibility == {vx0} only:", only_vx0)

    # CP-SAT cross-check of capture
    status, _ = gate_capture(chosen_atoms, adj, owner, active, n)
    print("my-cpsat capture status:", status)

    slacks = supersaturation(chosen_atoms, edges, kmax=3)
    print("supersaturation min slacks:", slacks)

    out[name] = {
        "shaOk": ok_sha,
        "rowsMatch": rows_match,
        "triangleCount": tri,
        "sdrAll24": sdr == [24] * 25,
        "muMin": mult_min,
        "classifier": vec4,
        "captureFactored": has_cap,
        "captureCpsat": status,
        "feasibleEdges": [list(e) for e in feas_edges],
        "onlyVx0": only_vx0,
        "supersaturationSlacks": slacks,
    }

Path(__file__).with_name("v5_hits_report.json").write_text(
    json.dumps(out, indent=1), encoding="utf-8"
)
print()
print(json.dumps(out, indent=1))
