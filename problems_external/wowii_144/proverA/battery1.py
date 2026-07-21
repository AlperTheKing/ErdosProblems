#!/usr/bin/env python3
"""proverA battery 1: falsifier-test every intermediate claim of the planned
general (Angle A) proof of Lemma E, on general connected cyclic graphs.

Claims tested (exact integer arithmetic throughout):
  TR   : g <= 2r+1
  TE   : e <= r
  TA   : attachment structure of v outside K: g>=5 -> <=1 K-neighbour;
         g=4 -> K-neighbours inside one antipodal pair; g=3 -> record max.
  C1   : M(K) >= H(K) for every shortest cycle K (g>=4; n-g<=13 only).
  WIN  : for x* (realizer of e), K, m (nearest K-vertex to x*),
         delta = e - h_x >= 1, delta <= floor(g/2)  [arc case]:
     WIN-noncentral: every sigma in W0 = ball_K(m, delta-1) has ecc >= r+1
     WIN-devK      : far vertices (d(sigma,.) >= r+1) never lie on K
     S6g           : no far vertex of any sigma in W0 lies in B(x*)
     TENT          : every sigma in W0 covered by some branch != B_x
     CAP           : |cov(B) cap W0| <= max(0, g-2r-1+2 D_B) for every branch
     MASS          : min over covers J (branches != B_x, every sigma covered)
                     of sum_{B in J} D_B  >= delta
  BIG  : delta > floor(g/2)  [only possible if h_c >= 1]:
     BIG-hc        : h_c >= delta - floor(g/2) for every center c at dist e
     BIG-allnc     : all K-positions noncentral
     BIG-mass      : min cover mass of ALL of K (branches != B_x) + h_x >= e?
     BIG-Dc        : D(B_c) >= e?  D(B_c) >= r+1-h_c?  (record slacks)
Output: battery1_results.json (counts, min slacks, up to 40 witnesses each).
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent / "wowii_141" / "oracle"))
sys.path.insert(0, str(ROOT.parent / "oracle"))
sys.path.insert(0, str(ROOT.parent / "wave2"))

from invariants import (all_pairs_dist, dist_to_set, eccentricities, girth,
                        graph_connected, nx_to_bitadj)
from bridge_tests import shortest_cycles, adversarial_graphs
from sweep_families import build_family_graphs, random_graphs
from route_b_tests import (cycle_random_legs, cycle_random_trees,
                           chorded_cycle, gen_theta, forced_girth_random,
                           trap_family, graph6)
from stress_lemma_e import subdivided_multigraph, webbed_annulus
from lemma_e_tests import M_of_cycle, components_of_mask

SEED = 20260718
OUT = ROOT / "battery1_results.json"
MAXW = 40


def rec(sec, key, wit, slack=None):
    s = sec.setdefault(key, {"count": 0, "min": None, "wit": []})
    s["count"] += 1
    if slack is not None and (s["min"] is None or slack < s["min"]):
        s["min"] = slack
    if len(s["wit"]) < MAXW:
        s["wit"].append(wit)


def main() -> None:
    rng = random.Random(SEED)
    corpora = []
    for A in nx.graph_atlas_g():
        if A.number_of_nodes() >= 2 and nx.is_connected(A):
            corpora.append(("atlas", A))
    corpora += build_family_graphs()
    corpora += random_graphs(random.Random(SEED))
    corpora += adversarial_graphs()
    corpora += trap_family()
    for _ in range(600):
        corpora.append(cycle_random_legs(rng))
    for _ in range(400):
        corpora.append(cycle_random_trees(rng))
    for _ in range(300):
        corpora.append(chorded_cycle(rng))
    for _ in range(300):
        corpora.append(gen_theta(rng))
    for i in range(500):
        corpora.append((f"subdiv{i}", subdivided_multigraph(rng)))
    for i in range(400):
        corpora.append((f"annulus{i}", webbed_annulus(rng)))
    got = tries = 0
    while got < 400 and tries < 9000:
        tries += 1
        r_ = forced_girth_random(rng, gmin=5)
        if r_ is not None:
            corpora.append(r_)
            got += 1

    seen = set()
    viol = {}          # claim -> record
    ok = Counter()     # claim -> #checks passed
    slackmin = {}      # claim -> (min slack, witness)
    graphs_used = 0

    def note_slack(key, slack, wit):
        if key not in slackmin or slack < slackmin[key][0]:
            slackmin[key] = (slack, wit)

    for name, G in corpora:
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        n, adj = nx_to_bitadj(G)
        if n < 3 or not graph_connected(n, adj):
            continue
        g = girth(n, adj)
        if g == 0:
            continue
        g6 = graph6(G)
        if g6 in seen:
            continue
        seen.add(g6)
        dist = all_pairs_dist(n, adj)
        ecc = eccentricities(n, dist)
        r = min(ecc)
        cmask = 0
        for v in range(n):
            if ecc[v] == r:
                cmask |= 1 << v
        e = max(dist_to_set(dist, v, cmask) for v in range(n))
        # TR / TE
        if g > 2 * r + 1:
            rec(viol, "TR", f"{name} [{g6}] g={g} r={r}")
        else:
            ok["TR"] += 1
        if e > r:
            rec(viol, "TE", f"{name} [{g6}] e={e} r={r}")
        else:
            ok["TE"] += 1
        if e == 0:
            continue
        graphs_used += 1

        cycles = shortest_cycles(G, g)
        if len(cycles) > 40:
            cycles = cycles[:40]
        xs = [v for v in range(n) if dist_to_set(dist, v, cmask) == e][:6]
        half = g // 2

        for K in cycles:
            kv = sorted(K)
            kmask = 0
            for v in kv:
                kmask |= 1 << v
            outmask = ((1 << n) - 1) & ~kmask
            # TA
            for v in range(n):
                if kmask >> v & 1:
                    continue
                nbrs = [u for u in kv if adj[v] >> u & 1]
                if g >= 5 and len(nbrs) > 1:
                    rec(viol, "TA5", f"{name} [{g6}] v={v} nbrs={nbrs}")
                elif g == 4 and len(nbrs) > 1:
                    if len(nbrs) != 2 or dist[nbrs[0]][nbrs[1]] != 2:
                        rec(viol, "TA4", f"{name} [{g6}] v={v} nbrs={nbrs}")
                    else:
                        ok["TA4"] += 1
                else:
                    ok["TA"] += 1
            # branches
            comps = components_of_mask(adj, outmask)
            binfo = []   # (mask, depth)
            for cm in comps:
                D = 0
                mm = cm
                while mm:
                    b = mm & -mm
                    mm ^= b
                    v = b.bit_length() - 1
                    D = max(D, dist_to_set(dist, v, kmask))
                binfo.append((cm, D))
            H = max((D for _, D in binfo), default=0)
            # C1
            if g >= 4 and n - g <= 13:
                mk = M_of_cycle(n, adj, kv)
                sl = mk - H
                note_slack("C1", sl, f"{name} [{g6}] g={g} M={mk} H={H}")
                if sl < 0:
                    rec(viol, "C1", f"{name} [{g6}] g={g} M={mk} H={H}", sl)
                else:
                    ok["C1"] += 1

            for xstar in xs:
                hx = dist_to_set(dist, xstar, kmask)
                delta = e - hx
                if delta <= 0:
                    sl = H - e
                    note_slack("CASE0", sl, f"{name} [{g6}]")
                    if sl < 0:
                        rec(viol, "CASE0", f"{name} [{g6}] H={H} e={e}", sl)
                    else:
                        ok["CASE0"] += 1
                    continue
                bx = None
                if hx >= 1:
                    for cm, D in binfo:
                        if cm >> xstar & 1:
                            bx = cm
                            break
                ms = [a for a in kv if dist[xstar][a] == hx]
                for m in ms:
                    if delta <= half:
                        W0 = [a for a in kv if dist[m][a] <= delta - 1]
                        if len(W0) != 2 * delta - 1:
                            rec(viol, "WINLEN",
                                f"{name} [{g6}] |W0|={len(W0)} delta={delta}")
                        covers = {}
                        bad = False
                        for sig in W0:
                            if ecc[sig] <= r:
                                rec(viol, "WIN-noncentral",
                                    f"{name} [{g6}] sig={sig}")
                                bad = True
                                break
                            far = [u for u in range(n)
                                   if dist[sig][u] >= r + 1]
                            if any(kmask >> u & 1 for u in far):
                                rec(viol, "WIN-devK", f"{name} [{g6}]")
                                bad = True
                                break
                            cbs = set()
                            s6 = False
                            for u in far:
                                for i, (cm, D) in enumerate(binfo):
                                    if cm >> u & 1:
                                        if bx is not None and cm == bx:
                                            s6 = True
                                        else:
                                            cbs.add(i)
                            if s6:
                                rec(viol, "S6g",
                                    f"{name} [{g6}] sig={sig} x={xstar} "
                                    f"m={m} K={kv} e={e} hx={hx}")
                            if not cbs:
                                rec(viol, "TENT",
                                    f"{name} [{g6}] sig={sig} x={xstar} "
                                    f"m={m} K={kv}")
                                bad = True
                                break
                            covers[sig] = cbs
                        if bad:
                            continue
                        ok["WIN"] += 1
                        # CAP per branch
                        for i, (cm, D) in enumerate(binfo):
                            cnt = sum(1 for sig in W0
                                      if i in covers.get(sig, ()))
                            capv = max(0, g - 2 * r - 1 + 2 * D)
                            if cnt > capv:
                                rec(viol, "CAP",
                                    f"{name} [{g6}] Bi={i} D={D} cov={cnt} "
                                    f"cap={capv} g={g} r={r}", capv - cnt)
                            else:
                                ok["CAP"] += 1
                        # MASS: min cover mass by branch subsets
                        cand = sorted(set().union(*covers.values()))
                        best = None
                        if len(cand) <= 18:
                            for sub in range(1 << len(cand)):
                                js = [cand[i] for i in range(len(cand))
                                      if sub >> i & 1]
                                jset = set(js)
                                if all(covers[s] & jset for s in W0):
                                    mass = sum(binfo[j][1] for j in js)
                                    if best is None or mass < best:
                                        best = mass
                        if best is not None:
                            sl = best - delta
                            note_slack("MASS", sl,
                                       f"{name} [{g6}] x={xstar} m={m} "
                                       f"K={kv} delta={delta} mass={best}")
                            if sl < 0:
                                rec(viol, "MASS",
                                    f"{name} [{g6}] x={xstar} m={m} K={kv} "
                                    f"delta={delta} mass={best} e={e} "
                                    f"hx={hx} g={g} r={r}", sl)
                            else:
                                ok["MASS"] += 1
                    else:
                        # BIG case
                        cs = [c for c in range(n)
                              if (cmask >> c & 1) and dist[xstar][c] == e]
                        for c in cs:
                            hc = dist_to_set(dist, c, kmask)
                            sl = hc - (delta - half)
                            note_slack("BIG-hc", sl, f"{name} [{g6}]")
                            if sl < 0:
                                rec(viol, "BIG-hc",
                                    f"{name} [{g6}] hc={hc} delta={delta}",
                                    sl)
                            else:
                                ok["BIG-hc"] += 1
                            bc = None
                            for cm, D in binfo:
                                if cm >> c & 1:
                                    bc = (cm, D)
                            if bc is not None:
                                note_slack("BIG-Dc-e", bc[1] - e,
                                           f"{name} [{g6}] D={bc[1]} e={e}")
                                note_slack("BIG-Dc-r", bc[1] - (r + 1 - hc),
                                           f"{name} [{g6}]")
                                if bc[1] < e:
                                    rec(viol, "BIG-Dc-e",
                                        f"{name} [{g6}] x={xstar} c={c} "
                                        f"K={kv} D={bc[1]} e={e} g={g} "
                                        f"r={r} hc={hc}", bc[1] - e)
                                else:
                                    ok["BIG-Dc-e"] += 1
                        if all(ecc[a] > r for a in kv):
                            ok["BIG-allnc"] += 1
                        else:
                            rec(viol, "BIG-allnc", f"{name} [{g6}]")

    out = {"seed": SEED, "graphs_cyclic_e1": graphs_used,
           "distinct": len(seen), "ok": dict(ok),
           "min_slacks": {k: v for k, v in slackmin.items()},
           "violations": {k: v for k, v in viol.items()}}
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("graphs used:", graphs_used)
    for k in sorted(slackmin):
        print(f"slack {k}: {slackmin[k][0]}  @ {slackmin[k][1][:90]}")
    for k in sorted(viol):
        print(f"VIOL {k}: count={viol[k]['count']} min={viol[k]['min']}")
        for w in viol[k]["wit"][:3]:
            print("   ", str(w)[:150])


if __name__ == "__main__":
    main()
