#!/usr/bin/env python3
"""proverA battery 4 (g>=5): the RIGID REGIME  rho_hat(K) <= e-1.

rho_hat(K) = max over
   tau-tails : tau_z(u) = d_{G-z}(u, K\\z)  (finite), any z in K, u not in K
   strands   : s(B,a) = min_{w in B, N(w) cap (K\\a) != 0} d_{G[B+a]}(a,w),
               wide branches B (>=2 doors), any door a of B
Both are valid single-component donations at g>=5 (proved), so
M(K) >= rho_hat(K); if rho_hat >= e we are DONE (Step 1 of the proof).

This battery: in the regime rho_hat(K) <= e-1 test, for all x*, m:
  R-O1 : delta = e - h_x <= g//2                     (BIG impossible)
  R-O2 : every sigma in W0 has a far vertex in a branch != B_x
  R-O3 : exists z: tau_z(x*) finite  and  min-cover mass_z >= delta
  R-CAPn: narrow branches: |cov cap W0| <= max(0, g-2r-1+2 D_B) (thm check)
  R-CAPw: wide branches: |cov cap W0| <= 2*T_z(B) for the winning z
  R-WIDE: wide branch exists in regime ==> e >= ceil(g/2)  (rigidity)
Output battery4_results.json
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
from battery2 import bfs_dist_avoid

SEED = 20260718
OUT = ROOT / "battery4_results.json"


def bfs_in_mask(n, adj, srcs, mask):
    INF = 10 ** 9
    d = [INF] * n
    dq = deque()
    for v in srcs:
        d[v] = 0
        dq.append(v)
    while dq:
        v = dq.popleft()
        nb = adj[v] & mask
        while nb:
            b = nb & -nb
            nb ^= b
            u = b.bit_length() - 1
            if d[u] > d[v] + 1:
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
        if len(s["wit"]) < 40:
            s["wit"].append(wit)

    def note(key, s, wit):
        if key not in slackmin or s < slackmin[key][0]:
            slackmin[key] = (s, wit)

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
        half = g // 2
        xs = [v for v in range(n) if dist_to_set(dist, v, cmask) == e][:6]
        for K in shortest_cycles(G, g)[:40]:
            kv = sorted(K)
            kmask = 0
            for v in kv:
                kmask |= 1 << v
            comps = components_of_mask(adj, ((1 << n) - 1) & ~kmask)
            doors = []
            for cm in comps:
                ds = set()
                mm = cm
                while mm:
                    b = mm & -mm
                    mm ^= b
                    v = b.bit_length() - 1
                    for a in kv:
                        if adj[v] >> a & 1:
                            ds.add(a)
                doors.append(sorted(ds))
            tauz = {z: bfs_dist_avoid(n, adj, kmask & ~(1 << z), z)
                    for z in kv}
            # rho_hat
            rho = 0
            for z in kv:
                for u in range(n):
                    if not (kmask >> u & 1) and tauz[z][u] < 10 ** 8:
                        rho = max(rho, tauz[z][u])
            for bi, cm in enumerate(comps):
                if len(doors[bi]) < 2:
                    continue
                for a in doors[bi]:
                    dpa = bfs_in_mask(n, adj, [a], cm | (1 << a))
                    s = min((dpa[w] for w in range(n)
                             if (cm >> w & 1) and dpa[w] < 10 ** 8
                             and (adj[w] & kmask & ~(1 << a))), default=None)
                    if s is not None:
                        note("STRAND-LB", s - ((g + 1) // 2 - 1),
                             f"{name} [{g6}] s={s} g={g}")
                        rho = max(rho, s)
            if rho >= e:
                ok["STEP1"] += 1
                continue
            ok["REGIME"] += 1
            widecnt = sum(1 for ds in doors if len(ds) >= 2)
            if widecnt:
                sl = e - (g + 1) // 2
                note("R-WIDE", sl, f"{name} [{g6}] e={e} g={g}")
                if sl < 0:
                    rec("R-WIDE", f"{name} [{g6}] e={e} g={g}", sl)
            for xstar in xs:
                hx = dist_to_set(dist, xstar, kmask)
                delta = e - hx
                if delta <= 0:
                    rec("R-CASE0", f"{name} [{g6}]")  # impossible: rho>=hx
                    continue
                if delta > half:
                    rec("R-O1", f"{name} [{g6}] x={xstar} K={kv} "
                        f"delta={delta} g={g} e={e} hx={hx} rho={rho}",
                        half - delta)
                    continue
                ok["R-O1"] += 1
                bxi = None
                if hx >= 1:
                    for i, cm in enumerate(comps):
                        if cm >> xstar & 1:
                            bxi = i
                            break
                for m in [a for a in kv if dist[xstar][a] == hx]:
                    W0 = [a for a in kv if dist[m][a] <= delta - 1]
                    covers = {}
                    failed = False
                    for sig in W0:
                        cbs = set()
                        for u in range(n):
                            if kmask >> u & 1 or dist[sig][u] <= r:
                                continue
                            for i, cm in enumerate(comps):
                                if (cm >> u & 1) and i != bxi:
                                    cbs.add(i)
                        if not cbs:
                            rec("R-O2", f"{name} [{g6}] sig={sig} x={xstar} "
                                f"m={m} K={kv} g={g} r={r} e={e} hx={hx}")
                            failed = True
                            break
                        covers[sig] = cbs
                    if failed:
                        continue
                    ok["R-O2"] += 1
                    cand = sorted(set().union(*covers.values()))
                    bestz, besttot = None, None
                    for z in kv:
                        if hx >= 1 and tauz[z][xstar] >= 10 ** 8:
                            continue
                        Tz = []
                        for i, cm in enumerate(comps):
                            b = 0
                            mm = cm
                            while mm:
                                bb = mm & -mm
                                mm ^= bb
                                v = bb.bit_length() - 1
                                t = tauz[z][v]
                                if t < 10 ** 8 and t > b:
                                    b = t
                            Tz.append(b)
                        bestm = None
                        if len(cand) <= 16:
                            for sub in range(1 << len(cand)):
                                js = [cand[i] for i in range(len(cand))
                                      if sub >> i & 1]
                                jset = set(js)
                                if all(covers[s] & jset for s in W0):
                                    mass = sum(Tz[j] for j in js)
                                    if bestm is None or mass < bestm:
                                        bestm = mass
                        if bestm is None:
                            continue
                        if besttot is None or bestm > besttot:
                            besttot, bestz = bestm, z
                            bestTz = Tz
                    if besttot is None:
                        rec("R-NOZ", f"{name} [{g6}] x={xstar} m={m} K={kv}")
                        continue
                    sl = besttot - delta
                    note("R-O3", sl, f"{name} [{g6}] x={xstar} m={m} K={kv} "
                                     f"mass={besttot} delta={delta}")
                    if sl < 0:
                        rec("R-O3", f"{name} [{g6}] x={xstar} m={m} K={kv} "
                            f"g={g} r={r} e={e} hx={hx} delta={delta} "
                            f"mass={besttot} rho={rho}", sl)
                        continue
                    ok["R-O3"] += 1
                    # capacities for winning z
                    for i in cand:
                        cnt = sum(1 for s in W0 if i in covers[s])
                        if len(doors[i]) <= 1:
                            D = bestTz[i]
                            capv = max(0, g - 2 * r - 1 + 2 * D)
                            if cnt > capv:
                                rec("R-CAPn", f"{name} [{g6}] z={bestz} "
                                    f"Bi={i} D={D} cov={cnt} cap={capv} "
                                    f"g={g} r={r}", capv - cnt)
                            else:
                                ok["R-CAPn"] += 1
                        else:
                            if cnt > 2 * bestTz[i]:
                                rec("R-CAPw", f"{name} [{g6}] z={bestz} "
                                    f"Bi={i} T={bestTz[i]} cov={cnt} "
                                    f"g={g} r={r} e={e}",
                                    2 * bestTz[i] - cnt)
                            else:
                                ok["R-CAPw"] += 1

    out = {"seed": SEED, "distinct_g5": len(seen), "ok": dict(ok),
           "min_slacks": {k: v for k, v in slackmin.items()},
           "violations": viol}
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("graphs g>=5:", len(seen))
    print("ok:", dict(ok))
    for k in sorted(slackmin):
        print(f"slack {k}: {slackmin[k][0]}  @ {slackmin[k][1][:100]}")
    for k in sorted(viol):
        print(f"VIOL {k}: count={viol[k]['count']} min={viol[k]['min']}")
        for w in viol[k]["wit"][:4]:
            print("   ", str(w)[:170])


if __name__ == "__main__":
    main()
