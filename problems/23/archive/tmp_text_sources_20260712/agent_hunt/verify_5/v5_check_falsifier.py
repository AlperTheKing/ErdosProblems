#!/usr/bin/env python3
"""Claims 1/2/6a checks on the fiberhunter 18-vertex object.
ALL input data below is transcribed from the REPORT TEXT (not from fiberhunter
files). Every check is my own code (v5_core)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from v5_core import (  # noqa: E402
    available_atoms,
    build_adj,
    bfs_dist,
    capture_decision,
    classifier_vector,
    deletion_sdr_sizes,
    factored_feasible,
    graph6_decode,
    is_connected,
    min_cut_sigma,
    norm,
    per_edge_latent_feasible,
    supersaturation,
    triangle_count,
    verify_selection,
)

# ---- data transcribed from the REPORT text -----------------------------
N = 18
LEFT = 9
EDGES = sorted(
    [
        (0, 9), (0, 10), (0, 11), (0, 12), (0, 13),
        (1, 14), (1, 15),
        (2, 16),
        (3, 15),
        (4, 15),
        (5, 15),
        (6, 9), (6, 10), (6, 14),
        (7, 9), (7, 13), (7, 16), (7, 17),
        (8, 9), (8, 10), (8, 11), (8, 12), (8, 14), (8, 15),
    ]
)
CHOSEN = sorted(
    [
        (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
        (1, 7), (2, 8), (3, 6), (3, 7), (4, 6), (4, 7), (5, 6), (5, 7),
        (10, 16), (10, 17), (11, 16), (11, 17), (12, 16), (12, 17),
        (13, 14), (13, 15), (14, 16), (14, 17), (15, 16), (15, 17),
    ]
)
GRAPH6 = "Q??????_{DOC_G_OGSAx?GO?@??"
OWNER, ACTIVE = 0, 9
CLAIMED_LATENT = sorted([(0, 9), (1, 14), (6, 9), (6, 14)])
CLAIMED_S = {0, 6, 7, 8, 9, 10, 11, 12, 13, 14}  # maxcut switch from report

report = {}
fails = []


def check(name, ok, detail=""):
    report[name] = {"ok": bool(ok), "detail": detail}
    if not ok:
        fails.append(name)
    print(("PASS " if ok else "FAIL ") + name + (f" | {detail}" if detail else ""))


# ---- structural axioms --------------------------------------------------
adj = build_adj(N, EDGES)
check("edge_count_24", len(EDGES) == 24, f"{len(EDGES)}")
check(
    "bipartite_shores_as_stated",
    all(u < 9 <= v for u, v in EDGES),
    "all edges L(0-8) x R(9-17)",
)
check("connected", is_connected(adj, N))

n6, e6 = graph6_decode(GRAPH6)
check(
    "graph6_matches_edges",
    n6 == 18 and sorted(map(tuple, e6)) == EDGES,
    f"decoded n={n6}, {len(e6)} edges",
)

atoms_all = available_atoms(N, EDGES, LEFT)
avail_pairs = sorted((a["u"], a["v"]) for a in atoms_all)
check("available_atoms_26", len(avail_pairs) == 26, f"{len(avail_pairs)}")
check(
    "chosen_25_subset_available",
    len(CHOSEN) == 25 and set(CHOSEN) <= set(avail_pairs),
    f"missing atom(s) from chosen: {sorted(set(avail_pairs) - set(CHOSEN))}",
)
atom_by_pair = {(a["u"], a["v"]): a for a in atoms_all}
chosen_atoms = [atom_by_pair[p] for p in CHOSEN]

check(
    "triangle_free_support_plus_bad",
    triangle_count(N, EDGES + CHOSEN) == 0,
    f"count={triangle_count(N, EDGES + CHOSEN)}",
)

mult = {
    tuple(e): sum(tuple(e) in set(map(tuple, a["footprint"])) for a in chosen_atoms)
    for e in EDGES
}
check("mu_min_ge_2", min(mult.values()) >= 2, f"min mu = {min(mult.values())}")

sdr = deletion_sdr_sizes(chosen_atoms, EDGES)
check("deletion_sdr_25x24_perfect", sdr == [24] * 25, f"sizes={sorted(set(sdr))}")

# owner census
census = {}
for v in range(N):
    dM = len(adj[v])
    dB = sum(v in (a["u"], a["v"]) for a in chosen_atoms)
    census[v] = (dM, dB)
profile_shaped = [v for v, (dM, dB) in census.items() if dM == 5 and dB == 5]
check(
    "owner_census_only_v0",
    profile_shaped == [0],
    f"profile-shaped={profile_shaped}; census={census}",
)

# classifier at (0,9) and alternates
vec = classifier_vector(chosen_atoms, adj, OWNER, ACTIVE)
check(
    "classifier_0_9_zero_vector",
    [vec[k] for k in ("eForced", "iStep", "dStep", "dCoverage")] == [0, 0, 0, 0],
    str([vec[k] for k in ("eForced", "iStep", "dStep", "dCoverage")]),
)
alt = {}
for x0 in (10, 11, 12, 13):
    v2 = classifier_vector(chosen_atoms, adj, OWNER, x0)
    alt[x0] = [v2[k] for k in ("eForced", "iStep", "dStep", "dCoverage")]
check(
    "alternate_x0_fail_coverage_0003",
    all(alt[x0] == [0, 0, 0, 3] for x0 in alt),
    str(alt),
)

# ---- claim 2: fibers + forced x0-edges ----------------------------------
nonincident = [
    a for a in chosen_atoms if OWNER not in (a["u"], a["v"])
]
star = [y for y in sorted(adj[OWNER]) if y != ACTIVE]
fiber = {}
forced_at_x0 = {}
x0_edges = {norm(ACTIVE, w) for w in adj[ACTIVE]}
for y in star:
    fiber[y] = sorted((set(adj[ACTIVE]) & set(adj[y])) - {OWNER})
    wits = [
        r
        for a in nonincident
        for r in a["rows"]
        if OWNER not in r and ACTIVE in r and y in r
    ]
    inter = None
    for r in wits:
        re = {norm(r[k], r[k + 1]) for k in range(4)} & x0_edges
        inter = re if inter is None else (inter & re)
    forced_at_x0[y] = sorted(inter) if inter else []
check(
    "fiber_C10_is_6_8",
    fiber[10] == [6, 8],
    f"fibers={fiber}",
)
check(
    "forced_x0_edges_per_pair",
    forced_at_x0[10] == [(7, 9)]
    and forced_at_x0[11] == [(7, 9), (8, 9)]
    and forced_at_x0[12] == [(7, 9), (8, 9)]
    and forced_at_x0[13] == [(7, 9)],
    str(forced_at_x0),
)

# ---- capture: solver-free exact decision --------------------------------
has_capture, witnesses, feas = capture_decision(chosen_atoms, adj, OWNER, ACTIVE, N)
feas_edges = sorted(e for e, ok in feas.items() if ok)
check(
    "per_edge_latent_feasible_8_edges",
    len(feas_edges) == 8 and norm(OWNER, ACTIVE) in feas_edges,
    f"feasible={feas_edges} (vx0 + {len(feas_edges)-1} others)",
)
check("CAPTURE_EXISTS", has_capture, f"{len(witnesses)} witness(es)")
uniq = {(w["atomIndex"], json.dumps(w["unionEdges"])) for w in witnesses}
check(
    "capture_witness_unique_and_expected",
    len(witnesses) == 1
    and witnesses[0]["badEdge"] == [0, 1]
    and sorted(map(tuple, witnesses[0]["unionEdges"]))
    == [(1, 14), (6, 9), (6, 14)],
    f"witnesses={[(w['badEdge'], w['unionEdges']) for w in witnesses]}",
)

# verify the constructed witness selection end-to-end with the plain checker
if witnesses:
    sel = witnesses[0]["selection"]
    info = verify_selection(chosen_atoms, adj, OWNER, ACTIVE, sel, N)
    cap_pairs = [
        (chosen_atoms[i]["u"], chosen_atoms[i]["v"]) for i in info["capturedAtoms"]
    ]
    check(
        "witness_selection_verifies",
        (0, 1) in cap_pairs,
        f"latent={info['latent']} comp={info['ownerComponent']} captured={cap_pairs}",
    )

# the exact claimed latent set: selection with latent EXACTLY the 4 edges
ok_cl, sel_cl = factored_feasible(
    chosen_atoms, adj, OWNER, ACTIVE, set(CLAIMED_LATENT) - {norm(OWNER, ACTIVE)}
)
exact_ok = False
detail = "factored infeasible"
if ok_cl:
    info_cl = verify_selection(chosen_atoms, adj, OWNER, ACTIVE, sel_cl, N)
    exact_ok = info_cl["latent"] == CLAIMED_LATENT
    detail = f"latent={info_cl['latent']} |S|={info_cl['selectedCount']}"
    if not exact_ok:
        # try to greedily add coverage of the extra-latent edges: brute repair
        # (the claim is existence of a selection with EXACTLY this latent set)
        import itertools as it

        forbidden = set(CLAIMED_LATENT)
        allowed = []
        incident_ids = [
            i
            for i, a in enumerate(chosen_atoms)
            if OWNER in (a["u"], a["v"])
        ]
        for i, a in enumerate(chosen_atoms):
            rows = [
                r
                for r in a["rows"]
                if not ({norm(r[k], r[k + 1]) for k in range(4)} & forbidden)
                and (i in incident_ids or OWNER not in r)
            ]
            allowed.append(rows)
        # randomized/greedy search for a selection covering all 20 non-latent edges
        import random

        rng = random.Random(0)
        target = set(map(tuple, EDGES)) - set(CLAIMED_LATENT)
        best = None
        for trial in range(20000):
            cand = [rng.choice(rows) for rows in allowed]
            try:
                info_t = verify_selection(
                    chosen_atoms, adj, OWNER, ACTIVE, cand, N
                )
            except AssertionError:
                continue
            if info_t["latent"] == CLAIMED_LATENT:
                best = (cand, info_t)
                break
        if best:
            exact_ok = True
            detail = (
                f"repaired: latent={best[1]['latent']} |S|={best[1]['selectedCount']}"
            )
check("claimed_exact_latent_set_selection_exists", exact_ok, detail)

# ---- claim 6a: supersaturation ------------------------------------------
sl = supersaturation(chosen_atoms, EDGES, kmax=3)
check(
    "supersaturation_k_le_3_holds",
    all(v >= 0 for v in sl.values()),
    f"min slacks {sl}",
)

# ---- maxcut sweep --------------------------------------------------------
sigma_min, switch = min_cut_sigma(N, EDGES, CHOSEN)
sigma_at_claimed = sum(
    (u in CLAIMED_S) != (v in CLAIMED_S) for u, v in EDGES
) - sum((u in CLAIMED_S) != (v in CLAIMED_S) for u, v in CHOSEN)
check(
    "maxcut_kappa_18",
    sigma_min == -18 and sigma_at_claimed == -18,
    f"min sigma={sigma_min} at {switch}; sigma(claimed S)={sigma_at_claimed}",
)

# ---- novelty: not isomorphic to #298/#264 -------------------------------
try:
    import networkx as nx

    g_new = nx.Graph(EDGES)
    hit298 = "Q??????wE_[?EGs?D_@A?C_B???"
    hit264 = "Q??????wE_Bws?s?DCD??@?@???"
    iso = {}
    for name, g6 in (("298", hit298), ("264", hit264)):
        nn, ee = graph6_decode(g6)
        iso[name] = nx.is_isomorphic(g_new, nx.Graph(ee))
    check(
        "support_not_isomorphic_to_hits",
        not iso["298"] and not iso["264"],
        str(iso),
    )
except Exception as exc:  # pragma: no cover
    check("support_not_isomorphic_to_hits", False, f"error {exc}")

print()
print("FAILED:" if fails else "ALL CHECKS PASSED", fails if fails else "")
Path(__file__).with_name("v5_falsifier_report.json").write_text(
    json.dumps(report, indent=1, default=str), encoding="utf-8"
)
