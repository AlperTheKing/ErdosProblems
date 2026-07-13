#!/usr/bin/env python3
"""Fiber-intersection / tail-starvation exact check for the two t=5 zero-vector hits.

Independent reconstruction (own graph6 decoder, own BFS/path/matching code) of the
two triangle-free zero-vector 25/24 profile circuits (#298 and #264), followed by:

  (A) full circuit-axiom re-verification (bipartite/connected/24 edges/25 atoms/
      triangle-free bad graph/multiplicity>=2/deletion-SDR all-24);
  (B) profile re-verification (classifier vector (0,0,0,0) recomputed);
  (C) structural lemma checks over the complete row database:
        L-cooccur : any row containing owner v and active x0 uses edge vx0
        L-onepair : any row contains at most one selected-star pair {x0,y_i}
        FI-1      : every coverage witness row for pair {x0,y_i} places x0,y_i at
                    row-distance exactly 2, through a common neighbour
                    q in C_i = N(x0) cap N(y_i) minus {v}, using edge x0-q
  (D) fiber computation: W_i = all selectable witnesses per pair, X_i = the
      intersection of their x0-edge sets, C_i sets;
  (E) the SC (singleton-fiber) certificate: every non-v support edge x0-w is
      forced-selected because some pair i has C_i = {w}; consequence: in EVERY
      profile-consistent row selection the latent component of v is exactly
      {v, x0}, which contains no same-shore pair, hence no captured atom
      (intrinsic-F* scope-vacuity) -- an enumeration-free, SAT-free certificate;
  (F) cross-checks against the archived engine artifacts (verification JSONs,
      CP-SAT scope gate, CaDiCaL tail-blanket certificate).

Integer/rational arithmetic only. No floats anywhere.
"""

from __future__ import annotations

import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path

BASE = Path(r"E:\Projects\ErdosProblems\tmp\fanout\r42_graph_specific_exclusion")
OUT = Path(r"E:\Projects\ErdosProblems\tmp\agent_hunt\fiber_intersection")

HITS = {
    "298": {
        "source": BASE / "t5_classifier_v_l9_r9_1000.json",
        "verification": BASE / "t5_classifier_v_l9_r9_hit_verification.json",
        "scope_cpsat": BASE / "t5_classifier_v_l9_r9_active_scope.json",
        "scope_cadical": BASE / "t5_classifier_v_l9_r9_active_scope_cadical.json",
        "blanket": None,
    },
    "264": {
        "source": BASE / "t5_live_x_classifier_v_l9_r9_5000.json",
        "verification": BASE / "t5_live_x_classifier_v_l9_r9_hit_verification.json",
        "scope_cpsat": BASE / "t5_live_x_classifier_v_l9_r9_active_scope.json",
        "scope_cadical": BASE / "t5_live_x_classifier_v_l9_r9_active_scope_cadical.json",
        "blanket": BASE / "t5_live_x_tail_blanket_cadical.json",
    },
}


def norm(u, v):
    return (u, v) if u < v else (v, u)


def canonical_sha(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def decode_graph6(text):
    """Own graph6 decoder (n < 63 case), independent of networkx."""
    data = [ord(c) - 63 for c in text]
    assert all(0 <= x < 64 for x in data), "invalid graph6 characters"
    n = data[0]
    assert n < 63
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    need = n * (n - 1) // 2
    assert len(bits) >= need and all(b == 0 for b in bits[need:])
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


def bfs_dist(adj, src, n):
    dist = [-1] * n
    dist[src] = 0
    queue = [src]
    head = 0
    while head < len(queue):
        cur = queue[head]
        head += 1
        for nxt in adj[cur]:
            if dist[nxt] == -1:
                dist[nxt] = dist[cur] + 1
                queue.append(nxt)
    return dist


def all_shortest_paths(adj, dist_to_target, src, target):
    """All shortest src->target paths, walking dist-to-target strictly down."""
    paths = []

    def extend(path):
        cur = path[-1]
        if cur == target:
            paths.append(tuple(path))
            return
        for nxt in adj[cur]:
            if dist_to_target[nxt] == dist_to_target[cur] - 1:
                extend(path + [nxt])

    extend([src])
    return paths


def kuhn_matching(left_count, adjacency):
    """Maximum bipartite matching; adjacency[l] = iterable of right ids."""
    match_right = {}
    match_left = {}

    def try_augment(l, seen):
        for r in adjacency[l]:
            if r in seen:
                continue
            seen.add(r)
            if r not in match_right or try_augment(match_right[r], seen):
                match_right[r] = l
                match_left[l] = r
                return True
        return False

    size = 0
    for l in range(left_count):
        if try_augment(l, set()):
            size += 1
    return size, match_left


def row_edges(row):
    return {norm(row[k], row[k + 1]) for k in range(4)}


def check_hit(tag, files):
    report = {"hit": tag}
    source = json.loads(files["source"].read_text(encoding="utf-8"))
    claimed = dict(source)
    claimed_sha = claimed.pop("canonicalSha256")
    assert canonical_sha(claimed) == claimed_sha, "source canonical sha mismatch"
    report["sourceCanonicalSha256"] = claimed_sha

    left_n, right_n = source["left"], source["right"]
    n_expected = left_n + right_n
    hit = source["hit"]

    # ---- independent graph6 decode + support checks -------------------------
    n, edges = decode_graph6(hit["graph6"])
    assert n == n_expected == 18
    support = sorted(norm(*e) for e in edges)
    assert support == sorted(norm(*e) for e in hit["supportEdges"])
    assert len(support) == 24
    shore = ["L"] * left_n + ["R"] * right_n
    assert all(shore[u] != shore[v] for u, v in support), "support not bipartite L/R"
    adj = [[] for _ in range(n)]
    for u, v in support:
        adj[u].append(v)
        adj[v].append(u)
    dist0 = bfs_dist(adj, 0, n)
    assert all(d >= 0 for d in dist0), "support not connected"

    # ---- independent atom/row database --------------------------------------
    dists = [bfs_dist(adj, s, n) for s in range(n)]
    atoms = []
    for side in ("L", "R"):
        verts = [x for x in range(n) if shore[x] == side]
        for u, v in combinations(verts, 2):
            if dists[u][v] != 4:
                continue
            rows = sorted(all_shortest_paths(adj, dists[v], u, v))
            fp = sorted(set().union(*(row_edges(r) for r in rows)))
            atoms.append({"u": u, "v": v, "shore": side, "rows": rows, "fp": fp})
    index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
    report["atomsAvailable"] = len(atoms)

    chosen = []
    for rec in hit["selectedAtoms"]:
        i = index[(rec["shore"], rec["u"], rec["v"])]
        assert set(map(tuple, rec["rows"])) == set(atoms[i]["rows"]), "row DB mismatch"
        assert set(map(tuple, map(sorted, rec["footprintEdges"]))) == set(
            atoms[i]["fp"]
        ), "footprint mismatch"
        chosen.append(i)
    assert len(chosen) == len(set(chosen)) == 25

    # ---- circuit axioms ------------------------------------------------------
    bad = sorted(norm(atoms[i]["u"], atoms[i]["v"]) for i in chosen)
    full_adj = [set() for _ in range(n)]
    for u, v in support + bad:
        full_adj[u].add(v)
        full_adj[v].add(u)
    triangles = sum(
        1
        for a in range(n)
        for b in full_adj[a]
        if b > a
        for c in full_adj[b]
        if c > b and c in full_adj[a]
    )
    assert triangles == 0, f"triangle count {triangles}"
    report["triangleCount"] = 0

    edge_id = {e: k for k, e in enumerate(support)}
    mult = [0] * 24
    for i in chosen:
        for e in atoms[i]["fp"]:
            mult[edge_id[e]] += 1
    assert min(mult) >= 2
    report["minMultiplicity"] = min(mult)

    sdr_sizes = []
    for out in range(25):
        rest = [i for k, i in enumerate(chosen) if k != out]
        adjacency = [[edge_id[e] for e in atoms[i]["fp"]] for i in rest]
        size, _ = kuhn_matching(len(rest), adjacency)
        sdr_sizes.append(size)
    assert sdr_sizes == [24] * 25, "deletion-SDR failure"
    report["deletionSdrAll24"] = True

    # ---- profile ------------------------------------------------------------
    owner = 0
    x0 = source["hit"]["selectionMeta"]["localClassifiers"][str(owner)][
        "activeNeighbour"
    ]
    nb_owner = sorted(adj[owner])
    assert len(nb_owner) == 5 and x0 in nb_owner
    ys = [y for y in nb_owner if y != x0]
    assert len(ys) == 4
    report["owner"] = owner
    report["activeNeighbour"] = x0
    report["ownerNeighbours"] = nb_owner

    incident = [i for i in chosen if owner in (atoms[i]["u"], atoms[i]["v"])]
    nonincident = [i for i in chosen if i not in incident]
    assert len(incident) == 5, "owner bad degree != 5"
    forced_nonincident = [
        i for i in nonincident if all(owner in r for r in atoms[i]["rows"])
    ]
    e_forced = len(forced_nonincident)

    def first_step(row):
        if row[0] == owner:
            return row[1]
        assert row[-1] == owner
        return row[-2]

    step_pairs = set()
    empty_steps = 0
    for i in incident:
        steps = {first_step(r) for r in atoms[i]["rows"]} & set(ys)
        if not steps:
            empty_steps += 1
        step_pairs.update((y, i) for y in steps)
    y_id = {y: k for k, y in enumerate(ys)}
    inc_id = {i: k for k, i in enumerate(incident)}
    non_id = {i: k for k, i in enumerate(nonincident)}
    adjacency = [[] for _ in ys]
    for y, i in step_pairs:
        adjacency[y_id[y]].append(inc_id[i])
    step_rank, _ = kuhn_matching(4, adjacency)

    vx0 = norm(owner, x0)
    cov_pairs = set()
    for y in ys:
        for i in nonincident:
            if any(
                owner not in r and x0 in r and y in r for r in atoms[i]["rows"]
            ):
                cov_pairs.add((y, i))
    adjacency = [[] for _ in ys]
    for y, i in cov_pairs:
        adjacency[y_id[y]].append(non_id[i])
    cov_rank, _ = kuhn_matching(4, adjacency)

    vector = [e_forced, empty_steps, 4 - step_rank, 4 - cov_rank]
    assert vector == [0, 0, 0, 0], f"classifier vector {vector}"
    report["classifierVector"] = vector

    # ---- structural lemma checks over the FULL row database ------------------
    # L-cooccur over ALL atoms (chosen or not): v,x0 in a row => edge vx0 in row.
    cooccur_rows = 0
    for a in atoms:
        for r in a["rows"]:
            if owner in r and x0 in r:
                cooccur_rows += 1
                assert vx0 in row_edges(r), f"L-cooccur fails: {r}"
    report["lemmaCooccurRowsChecked"] = cooccur_rows

    # L-onepair over all rows of chosen atoms: at most one y_i beside x0.
    for i in chosen:
        for r in atoms[i]["rows"]:
            if x0 in r:
                assert sum(1 for y in ys if y in r) <= 1, f"L-onepair fails: {r}"
    report["lemmaOnePair"] = True

    # FI-1 over every selectable coverage witness of every pair.
    fibers = {}
    forced_by_pair = {}
    c_sets = {}
    for y in ys:
        witnesses = []
        for i in chosen:
            for r in atoms[i]["rows"]:
                if x0 in r and y in r and vx0 not in row_edges(r):
                    witnesses.append((i, r))
        assert witnesses, f"pair (x0={x0}, y={y}) has no selectable witness"
        c_i = sorted((set(adj[x0]) & set(adj[y])) - {owner})
        c_sets[y] = c_i
        assert c_i, f"C_i empty for y={y}"
        x0_edge_sets = []
        for i, r in witnesses:
            assert owner not in r, "witness contains owner"
            assert i not in incident, "witness atom is incident"
            p_x0, p_y = r.index(x0), r.index(y)
            assert abs(p_x0 - p_y) == 2, f"FI-1 distance fails: {r}"
            q = r[(p_x0 + p_y) // 2]
            assert q in c_i, f"FI-1 middle not in C_i: {r}"
            assert norm(x0, q) in row_edges(r)
            x0_edge_sets.append(
                frozenset(e for e in row_edges(r) if x0 in e)
            )
        inter = frozenset.intersection(*x0_edge_sets)
        fibers[y] = {
            "witnessCount": len(witnesses),
            "witnessAtoms": sorted({i for i, _ in witnesses}),
            "witnessRows": [list(r) for _, r in sorted(witnesses)],
            "intersectionX0Edges": sorted(map(list, map(sorted, inter))),
            "commonNeighbourhoodC": c_i,
        }
        if len(c_i) == 1:
            assert norm(x0, c_i[0]) in inter, "singleton C_i not in intersection"
        forced_by_pair[y] = inter
    report["fibers"] = {str(y): fibers[y] for y in ys}

    # ---- SC certificate -------------------------------------------------------
    tail_targets = sorted(w for w in adj[x0] if w != owner)
    report["x0SupportDegree"] = len(adj[x0])
    certificate = {}
    missing = []
    for w in tail_targets:
        owners_of_w = [y for y in ys if c_sets[y] == [w]]
        if owners_of_w:
            certificate[str(w)] = owners_of_w
        else:
            missing.append(w)
    report["scCertificate"] = certificate
    report["scMissingEdges"] = missing
    sc_holds = not missing
    report["scHolds"] = sc_holds

    # Blanket consequence, stated exactly:
    # for every profile-consistent selection, each pair y is covered by a selected
    # witness; every witness for y uses edge x0-q with q in C_y; if C_y={w} the edge
    # x0-w is selected. SC => all non-owner x0-edges selected => latent component of
    # owner = {owner, x0} (owner keeps only the latent vx0) => no same-shore pair
    # inside => activeBadAtoms empty for EVERY selection.
    if sc_holds:
        report["verdict"] = (
            "SC_CERTIFICATE_VALID: every profile-consistent selection selects all "
            "non-owner x0-edges; latent component = {owner, x0}; intrinsic-F* "
            "scope-vacuity PROVED enumeration-free for this circuit"
        )
    else:
        report["verdict"] = "SC_FAILS: fallback (disjunctive/LRAT) certificate needed"

    # Stronger archived claim check (#264): edge 9-1 in EVERY pair's intersection.
    universal_edges = sorted(
        map(list, map(sorted, frozenset.intersection(*forced_by_pair.values())))
    )
    report["edgesInEveryPairIntersection"] = universal_edges
    if tag == "264":
        assert fibers[15]["witnessCount"] == 1, "R50 unique-witness claim"
        assert fibers[15]["witnessRows"] == [[15, 2, 9, 1, 17]], (
            fibers[15]["witnessRows"]
        )
        assert universal_edges == [[1, 9]], "R50 every-witness-uses-9-1 claim"

    # ---- cross-checks vs archived artifacts ----------------------------------
    cross = {}
    ver = json.loads(files["verification"].read_text(encoding="utf-8"))
    assert ver["sourceCanonicalSha256"] == claimed_sha
    assert ver["activeOwner"] is False
    assert ver["classifierVector"] == [0, 0, 0, 0]
    assert ver["activeNeighbour"] == x0
    assert sorted(ver["activeComponent"]) == sorted([owner, x0]), (
        "archived constructed-selection component differs from {v,x0}"
    )

    # Replay the archived CONSTRUCTED selection through my theory:
    # (1) it is profile-consistent; (2) its coverage witnesses' middles lie in C_y;
    # (3) its latent graph has owner-component exactly {owner, x0} -- as Theorem 2
    # predicts from the SC certificate (blanket => all non-owner x0-edges selected).
    sel_rows = {int(k): tuple(v) for k, v in ver["selectedRows"].items()}
    assert set(sel_rows) == set(chosen)
    sel_edges = set()
    for i, r in sel_rows.items():
        assert tuple(r) in set(atoms[i]["rows"]), "archived row not in my DB"
        sel_edges |= row_edges(r)
    assert vx0 not in sel_edges
    assert all(norm(owner, y) in sel_edges for y in ys)
    assert sum(owner in r for r in sel_rows.values()) == 5
    for y in ys:
        cover = [
            (i, r) for i, r in sel_rows.items() if x0 in r and y in r and owner not in r
        ]
        assert cover, f"archived selection misses pair y={y}"
        for i, r in cover:
            q = r[(r.index(x0) + r.index(y)) // 2]
            assert q in c_sets[y], "archived witness middle outside C_y"
    latent = set(support) - sel_edges
    if sc_holds:
        assert all(not (x0 in e and owner not in e) for e in latent), (
            "SC blanket violated by archived selection"
        )
    comp = {owner}
    frontier = [owner]
    latent_adj = {}
    for u, v2 in latent:
        latent_adj.setdefault(u, []).append(v2)
        latent_adj.setdefault(v2, []).append(u)
    while frontier:
        cur = frontier.pop()
        for nxt in latent_adj.get(cur, []):
            if nxt not in comp:
                comp.add(nxt)
                frontier.append(nxt)
    assert comp == {owner, x0}, f"latent component {sorted(comp)}"
    report["archivedSelectionReplay"] = {
        "latentEdges": sorted(map(list, latent)),
        "latentComponentOfOwner": sorted(comp),
        "profileConsistent": True,
    }
    cross["verification"] = {
        "sha": ver["canonicalSha256"],
        "activeOwner": ver["activeOwner"],
        "activeComponent": ver["activeComponent"],
    }
    for key in ("scope_cpsat", "scope_cadical"):
        path = files[key]
        if path is None or not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        verdict = data.get("verdict") or data.get("status")
        cross[key] = {"verdict": verdict, "sha": data.get("canonicalSha256")}
        ok = (
            ("NO_ACTIVE_SCOPE" in json.dumps(data))
            or (data.get("status") in ("INFEASIBLE", "UNSAT"))
            or (data.get("satisfiable") is False)
            or ("UNSAT" in str(data.get("verdict", "")))
        )
        assert ok, f"archived scope artifact not UNSAT-like: {path}"
    if files["blanket"] and files["blanket"].exists():
        data = json.loads(files["blanket"].read_text(encoding="utf-8"))
        assert data["verdict"] == "PASS_ALL_NONOWNER_TAIL_EDGES_FORCED_SELECTED"
        archived_edges = sorted(tuple(sorted(t["edge"])) for t in data["tests"])
        mine = sorted(norm(x0, w) for w in tail_targets)
        assert archived_edges == mine, (archived_edges, mine)
        cross["blanket"] = {
            "verdict": data["verdict"],
            "edges": [list(e) for e in archived_edges],
            "sha": data["canonicalSha256"],
        }
    report["crossChecks"] = cross
    return report


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reports = []
    for tag, files in HITS.items():
        rep = check_hit(tag, files)
        reports.append(rep)
        print(f"== hit #{tag} ==")
        print(f"  source sha       : {rep['sourceCanonicalSha256'][:16]}")
        print(f"  axioms           : 24 edges, 25 atoms, tri-free, mult>=2, SDR all-24 OK")
        print(f"  classifier       : {rep['classifierVector']}")
        print(f"  owner/x0         : {rep['owner']} / {rep['activeNeighbour']}")
        print(f"  deg_F*(x0)       : {rep['x0SupportDegree']}")
        for y, f in rep["fibers"].items():
            print(
                f"  pair y={y:>2}: |W|={f['witnessCount']:>2}  C_i={f['commonNeighbourhoodC']}"
                f"  forced-at-x0={f['intersectionX0Edges']}"
            )
        print(f"  SC certificate   : {rep['scCertificate']}  missing={rep['scMissingEdges']}")
        print(f"  every-pair edges : {rep['edgesInEveryPairIntersection']}")
        print(f"  verdict          : {rep['verdict']}")
        print()
    payload = {"schema": "t5-fiber-starvation-check-v1", "reports": reports}
    payload["canonicalSha256"] = canonical_sha(payload)
    out_file = OUT / "fiber_starvation_report.json"
    out_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"report sha: {payload['canonicalSha256']}")
    print(f"written   : {out_file}")


if __name__ == "__main__":
    main()
