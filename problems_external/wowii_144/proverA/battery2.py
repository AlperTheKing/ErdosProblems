#!/usr/bin/env python3
"""proverA battery 2 (g >= 5): tau-tail machinery.

tau_z(u) = d_{G-z}(u, K\\{z}) ; tau-tail = shortest such path minus endpoint:
induced path inside branch B(u), interior has no K\\z-neighbours, terminal
vertex has exactly one K-neighbour (g>=5), z-edges free.
T_z(B) = max_u in B tau_z(u) (0 if unreachable).

For every cyclic G with g>=5, e>=1, every shortest K (<=40), every realizer
x* (<=6), every nearest m:
  delta = e - h_x; skip delta<=0 (CASE0, battery1 clean).
  If delta <= floor(g/2): window W0 = ball_K(m, delta-1).
    TENT5 : every sigma in W0 has a far vertex (d >= r+1) in some branch
            != B_x  (record separately: covered only by B_x, or not at all)
    SUCC  : exists z in K with
              (h_x = 0  or  tau_z(x*) finite)   [x*-tail exists, >= h_x]
            and min-cover mass_z >= delta, where
            mass_z = min over covers J subset branches\\{B_x} of W0
                     of sum T_z(B)   (cover: every sigma far-covered)
    CAPt  : for all z,B: |cov(B) cap W0| <= max(0, g-2r-1+2*T_z(B))
  Else (delta > floor(g/2)): BIG case, battery1 says D(B_c) >= e; recheck
    with tau: exists z: T_z(B_c) >= e   (single-branch donation).
Output battery2_results.json
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter, deque
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
from lemma_e_tests import components_of_mask

SEED = 20260718
OUT = ROOT / "battery2_results.json"
MAXW = 40


def bfs_dist_avoid(n, adj, src_mask, avoid):
    """distances from the set src_mask in G-avoid (avoid = single vertex)."""
    INF = 10 ** 9
    d = [INF] * n
    dq = deque()
    m = src_mask
    while m:
        b = m & -m
        m ^= b
        v = b.bit_length() - 1
        if v != avoid:
            d[v] = 0
            dq.append(v)
    while dq:
        v = dq.popleft()
        nb = adj[v]
        while nb:
            b = nb & -nb
            nb ^= b
            u = b.bit_length() - 1
            if u != avoid and d[u] > d[v] + 1:
                d[u] = d[v] + 1
                dq.append(u)
    return d


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
    for _ in range(500):
        corpora.append(cycle_random_legs(rng))
    for _ in range(400):
        corpora.append(cycle_random_trees(rng))
    for _ in range(250):
        corpora.append(chorded_cycle(rng))
    for _ in range(400):
        corpora.append(gen_theta(rng))
    for i in range(600):
        corpora.append((f"subdiv{i}", subdivided_multigraph(rng)))
    for i in range(600):
        corpora.append((f"annulus{i}", webbed_annulus(rng)))
    got = tries = 0
    while got < 600 and tries < 15000:
        tries += 1
        r_ = forced_girth_random(rng, gmin=5)
        if r_ is not None:
            corpora.append(r_)
            got += 1

    seen = set()
    ok = Counter()
    viol = {}
    slackmin = {}

    def rec(key, wit, slack=None):
        s = viol.setdefault(key, {"count": 0, "min": None, "wit": []})
        s["count"] += 1
        if slack is not None and (s["min"] is None or slack < s["min"]):
            s["min"] = slack
        if len(s["wit"]) < MAXW:
            s["wit"].append(wit)

    def note(key, slack, wit):
        if key not in slackmin or slack < slackmin[key][0]:
            slackmin[key] = (slack, wit)

    for name, G in corpora:
        G = nx.convert_node_labels_to_integers(G, ordering="default")
        n, adj = nx_to_bitadj(G)
        if n < 3 or not graph_connected(n, adj):
            continue
        g = girth(n, adj)
        if g < 5:
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
        if e == 0:
            continue
        cycles = shortest_cycles(G, g)[:40]
        xs = [v for v in range(n) if dist_to_set(dist, v, cmask) == e][:6]
        half = g // 2

        for K in cycles:
            kv = sorted(K)
            kmask = 0
            for v in kv:
                kmask |= 1 << v
            comps = components_of_mask(adj, ((1 << n) - 1) & ~kmask)
            nb = len(comps)
            # T_z per branch for each z
            Tz = {}      # z -> list per branch
            tauz = {}    # z -> per-vertex distance to K\z in G-z
            for z in kv:
                dz = bfs_dist_avoid(n, adj, kmask & ~(1 << z), z)
                tauz[z] = dz
                Tz[z] = []
                for cm in comps:
                    best = 0
                    mm = cm
                    while mm:
                        b = mm & -mm
                        mm ^= b
                        v = b.bit_length() - 1
                        if dz[v] < 10 ** 8 and dz[v] > best:
                            best = dz[v]
                    Tz[z].append(best)
            for xstar in xs:
                hx = dist_to_set(dist, xstar, kmask)
                delta = e - hx
                if delta <= 0:
                    continue
                bxi = None
                if hx >= 1:
                    for i, cm in enumerate(comps):
                        if cm >> xstar & 1:
                            bxi = i
                            break
                ms = [a for a in kv if dist[xstar][a] == hx]
                if delta > half:
                    # BIG: single-branch donation from c's branch
                    cs = [c for c in range(n)
                          if (cmask >> c & 1) and dist[xstar][c] == e]
                    for c in cs:
                        bci = None
                        for i, cm in enumerate(comps):
                            if cm >> c & 1:
                                bci = i
                        if bci is None:
                            rec("BIG-conK", f"{name} [{g6}]")
                            continue
                        bestT = max(Tz[z][bci] for z in kv)
                        sl = bestT - e
                        note("BIG-T", sl, f"{name} [{g6}] T={bestT} e={e}")
                        if sl < 0:
                            rec("BIG-T", f"{name} [{g6}] x={xstar} c={c} "
                                f"K={kv} T={bestT} e={e} g={g} r={r}", sl)
                        else:
                            ok["BIG-T"] += 1
                    continue
                for m in ms:
                    W0 = [a for a in kv if dist[m][a] <= delta - 1]
                    covers = {}
                    tent_fail = False
                    for sig in W0:
                        cbs = set()
                        only_bx = False
                        for u in range(n):
                            if kmask >> u & 1 or dist[sig][u] <= r:
                                continue
                            for i, cm in enumerate(comps):
                                if cm >> u & 1:
                                    if i == bxi:
                                        only_bx = True
                                    else:
                                        cbs.add(i)
                        if not cbs:
                            rec("TENT5" if only_bx else "TENT5-none",
                                f"{name} [{g6}] sig={sig} x={xstar} m={m} "
                                f"K={kv} g={g} r={r} e={e} hx={hx}")
                            tent_fail = True
                            break
                        covers[sig] = cbs
                    if tent_fail:
                        continue
                    cand = sorted(set().union(*covers.values()))
                    best_over_z = None
                    for z in kv:
                        if hx >= 1 and tauz[z][xstar] >= 10 ** 8:
                            continue
                        # min cover mass with T_z
                        bestm = None
                        if len(cand) <= 16:
                            for sub in range(1 << len(cand)):
                                js = [cand[i] for i in range(len(cand))
                                      if sub >> i & 1]
                                jset = set(js)
                                if all(covers[s] & jset for s in W0):
                                    mass = sum(Tz[z][j] for j in js)
                                    if bestm is None or mass < bestm:
                                        bestm = mass
                        if bestm is None:
                            continue
                        tot = bestm + (tauz[z][xstar] if hx >= 1 else 0)
                        if best_over_z is None or tot > best_over_z:
                            best_over_z = tot
                        # CAPt for this z
                        for i in cand:
                            cnt = sum(1 for s in W0 if i in covers[s])
                            capv = max(0, g - 2 * r - 1 + 2 * Tz[z][i])
                            if cnt > capv:
                                rec("CAPt", f"{name} [{g6}] z={z} Bi={i} "
                                    f"T={Tz[z][i]} cov={cnt} cap={capv} "
                                    f"g={g} r={r}", capv - cnt)
                            else:
                                ok["CAPt"] += 1
                    if best_over_z is None:
                        rec("NOZ", f"{name} [{g6}] x={xstar} m={m} K={kv}")
                        continue
                    sl = best_over_z - e
                    note("SUCC", sl, f"{name} [{g6}] x={xstar} m={m} K={kv} "
                                     f"tot={best_over_z} e={e}")
                    if sl < 0:
                        rec("SUCC", f"{name} [{g6}] x={xstar} m={m} K={kv} "
                            f"g={g} r={r} e={e} hx={hx} delta={delta} "
                            f"tot={best_over_z}", sl)
                    else:
                        ok["SUCC"] += 1

    out = {"seed": SEED, "distinct_g5": len(seen), "ok": dict(ok),
           "min_slacks": {k: v for k, v in slackmin.items()},
           "violations": viol}
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("graphs g>=5:", len(seen))
    for k in sorted(slackmin):
        print(f"slack {k}: {slackmin[k][0]}  @ {slackmin[k][1][:100]}")
    print("ok:", dict(ok))
    for k in sorted(viol):
        print(f"VIOL {k}: count={viol[k]['count']} min={viol[k]['min']}")
        for w in viol[k]["wit"][:4]:
            print("   ", str(w)[:170])


if __name__ == "__main__":
    main()
