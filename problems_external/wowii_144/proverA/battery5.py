#!/usr/bin/env python3
"""proverA battery 5: targeted bridge tests for the final proof document.

g>=5 (regime rho_hat <= e-1):
  BR-A  : instances with delta > g//2 AND B_c wide          (expect NONE)
  BR-B  : every sigma in W0 has far vertex in NARROW branch != B_x
  ASM   : full assembly: J = minimum narrow cover (|J|<=2 by prefix/suffix),
          z avoiding the <=3 doors: mass = tau_z(x*) + sum D_B >= e
g=4:
  G4    : exists z: valid-donation assembly >= e, OR single donation >= e,
          where valid tails respect the exactly-one-edge-into-K\\z rule
          (terminal with antipodal-pair attachment needs z in the pair).
          Tested per-K (E_forall regime) - record failures per K and
          whether SOME K works.
g=3:
  G3    : exists shortest triangle K, z: same valid-donation assembly >= e.
Exact integer arithmetic. Output battery5_results.json
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
OUT = ROOT / "battery5_results.json"


def bfs_masked(n, adj, srcs, allowed_mask):
    INF = 10 ** 9
    d = [INF] * n
    dq = deque()
    for v in srcs:
        if allowed_mask >> v & 1:
            d[v] = 0
            dq.append(v)
    while dq:
        v = dq.popleft()
        nb = adj[v] & allowed_mask
        while nb:
            b = nb & -nb
            nb ^= b
            u = b.bit_length() - 1
            if d[u] > d[v] + 1:
                d[u] = d[v] + 1
                dq.append(u)
    return d


def valid_tau(n, adj, kv, kmask, z):
    """tau'_z(u): length of shortest VALID tail from u: path in G-z with
    interior having no K\\z-edges, terminal with exactly one K\\z-edge.
    Returns list (10**9 = none). Length counted as #vertices of the tail
    = distance(u, terminal) + 1."""
    INF = 10 ** 9
    kz = kmask & ~(1 << z)
    terminals = []
    interior_ok = 0
    for v in range(n):
        if kmask >> v & 1:
            continue
        cnt = bin(adj[v] & kz).count("1")
        if cnt == 0:
            interior_ok |= 1 << v
        elif cnt == 1:
            terminals.append(v)
    # BFS from terminals through interior_ok vertices
    allowed = interior_ok
    d = [INF] * n
    dq = deque()
    for t in terminals:
        d[t] = 1                       # tail consisting of terminal alone
        dq.append(t)
    while dq:
        v = dq.popleft()
        nb = adj[v] & allowed
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
        if e == 0:
            continue
        half = g // 2
        xs = [v for v in range(n) if dist_to_set(dist, v, cmask) == e][:6]
        cycles = shortest_cycles(G, g)[:40]

        if g >= 5:
            for K in cycles:
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
                rho = 0
                for z in kv:
                    for u in range(n):
                        if not (kmask >> u & 1) and tauz[z][u] < 10 ** 8:
                            rho = max(rho, tauz[z][u])
                for bi, cm in enumerate(comps):
                    if len(doors[bi]) < 2:
                        continue
                    for a in doors[bi]:
                        dpa = bfs_masked(n, adj, [a], cm | (1 << a))
                        s = min((dpa[w] for w in range(n)
                                 if (cm >> w & 1) and dpa[w] < 10 ** 8
                                 and (adj[w] & kmask & ~(1 << a))),
                                default=None)
                        if s is not None:
                            rho = max(rho, s)
                if rho >= e:
                    ok["g5-STEP1"] += 1
                    continue
                # depth of narrow branches (single door): D_B
                Dn = {}
                for bi, cm in enumerate(comps):
                    if len(doors[bi]) == 1:
                        a = doors[bi][0]
                        dd = bfs_masked(n, adj, [a], cm | (1 << a))
                        Dn[bi] = max(dd[v] for v in range(n) if cm >> v & 1)
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
                    if delta > half:
                        # BR-A: is B_c wide?
                        for c in range(n):
                            if (cmask >> c & 1) and dist[xstar][c] == e:
                                bci = next(i for i, cm in enumerate(comps)
                                           if cm >> c & 1)
                                w = len(doors[bci]) >= 2
                                rec("BR-A", f"{name} [{g6}] x={xstar} c={c} "
                                    f"wide={w} K={kv} g={g} e={e} "
                                    f"delta={delta}")
                        continue
                    for m in [a for a in kv if dist[xstar][a] == hx]:
                        W0 = [a for a in kv if dist[m][a] <= delta - 1]
                        covs = {}
                        bad = False
                        for sig in W0:
                            cbs = set()
                            for u in range(n):
                                if kmask >> u & 1 or dist[sig][u] <= r:
                                    continue
                                for i, cm in enumerate(comps):
                                    if (cm >> u & 1) and i != bxi \
                                            and len(doors[i]) == 1:
                                        cbs.add(i)
                            if not cbs:
                                rec("BR-B", f"{name} [{g6}] sig={sig} "
                                    f"x={xstar} m={m} K={kv} g={g} r={r} "
                                    f"e={e} hx={hx}")
                                bad = True
                                break
                            covs[sig] = cbs
                        if bad:
                            continue
                        ok["BR-B"] += 1
                        # minimum narrow cover, <= 2 branches expected
                        cand = sorted(set().union(*covs.values()))
                        best = None
                        for j1 in cand:
                            if all(j1 in covs[s] for s in W0):
                                m1 = Dn[j1]
                                if best is None or m1 < best[0]:
                                    best = (m1, [j1])
                        if best is None:
                            for j1 in cand:
                                for j2 in cand:
                                    if j2 <= j1:
                                        continue
                                    if all(j1 in covs[s] or j2 in covs[s]
                                           for s in W0):
                                        mm2 = Dn[j1] + Dn[j2]
                                        if best is None or mm2 < best[0]:
                                            best = (mm2, [j1, j2])
                        if best is None:
                            rec("ASM-cover2",
                                f"{name} [{g6}] x={xstar} m={m} K={kv}")
                            continue
                        ok["ASM-cover2"] += 1
                        mass, J = best
                        used_doors = {doors[j][0] for j in J}
                        if bxi is not None and len(doors[bxi]) == 1:
                            used_doors.add(doors[bxi][0])
                        zs = [z for z in kv if z not in used_doors]
                        if not zs:
                            rec("ASM-z", f"{name} [{g6}]")
                            continue
                        z = zs[0]
                        xmass = 0
                        if hx >= 1:
                            xmass = tauz[z][xstar]
                            if xmass >= 10 ** 8:
                                rec("ASM-xtail", f"{name} [{g6}] z={z}")
                                continue
                        sl = xmass + mass - e
                        note("ASM", sl, f"{name} [{g6}] x={xstar} m={m} "
                                        f"K={kv} mass={xmass}+{mass} e={e}")
                        if sl < 0:
                            rec("ASM", f"{name} [{g6}] x={xstar} m={m} "
                                f"K={kv} g={g} r={r} e={e} hx={hx} "
                                f"delta={delta} mass={xmass}+{mass}", sl)
                        else:
                            ok["ASM"] += 1
        elif g in (3, 4):
            tag = f"G{g}"
            per_graph_allK = True
            some_K = False
            for K in cycles:
                kv = sorted(K)
                kmask = 0
                for v in kv:
                    kmask |= 1 << v
                comps = components_of_mask(adj, ((1 << n) - 1) & ~kmask)
                okK = True
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
                    donez = False
                    for z in kv:
                        tv = valid_tau(n, adj, kv, kmask, z)
                        # single donation
                        single = max((tv[u] for u in range(n)
                                      if not (kmask >> u & 1)
                                      and tv[u] < 10 ** 8), default=0)
                        if single >= e:
                            donez = True
                            break
                        Tz = []
                        for i, cm in enumerate(comps):
                            b = 0
                            mm = cm
                            while mm:
                                bb = mm & -mm
                                mm ^= bb
                                v = bb.bit_length() - 1
                                if tv[v] < 10 ** 8 and tv[v] > b:
                                    b = tv[v]
                            Tz.append(b)
                        xmass = 0
                        if hx >= 1:
                            xmass = tv[xstar]
                            if xmass >= 10 ** 8:
                                continue
                        # cover: window positions
                        msx = [a for a in kv if dist[xstar][a] == hx]
                        okm = False
                        for m in msx:
                            W0 = [a for a in kv
                                  if dist[m][a] <= delta - 1]
                            need = 0
                            covsets = []
                            failed = False
                            for sig in W0:
                                cbs = set()
                                for u in range(n):
                                    if kmask >> u & 1 or \
                                            dist[sig][u] <= r:
                                        continue
                                    for i, cm in enumerate(comps):
                                        if (cm >> u & 1) and i != bxi:
                                            cbs.add(i)
                                if not cbs:
                                    failed = True
                                    break
                                covsets.append(cbs)
                            if failed:
                                continue
                            cand = sorted(set().union(*covsets)) \
                                if covsets else []
                            bestm = 0 if not covsets else None
                            for sub in range(1 << len(cand)):
                                js = [cand[i] for i in range(len(cand))
                                      if sub >> i & 1]
                                jset = set(js)
                                if all(cs & jset for cs in covsets):
                                    mval = sum(Tz[j] for j in js)
                                    if bestm is None or mval < bestm:
                                        bestm = mval
                            if bestm is not None and \
                                    xmass + bestm >= e:
                                okm = True
                                break
                        if okm:
                            donez = True
                            break
                    if not donez:
                        okK = False
                        break
                if okK:
                    some_K = True
                else:
                    per_graph_allK = False
            if cycles:
                if some_K:
                    ok[f"{tag}-existsK"] += 1
                else:
                    rec(f"{tag}-existsK", f"{name} [{g6}] g={g} r={r} e={e}")
                if per_graph_allK:
                    ok[f"{tag}-allK"] += 1
                else:
                    ok[f"{tag}-allK-fail"] += 1

    out = {"seed": SEED, "distinct": len(seen), "ok": dict(ok),
           "min_slacks": {k: v for k, v in slackmin.items()},
           "violations": viol}
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print("distinct graphs:", len(seen))
    print("ok:", dict(ok))
    for k in sorted(slackmin):
        print(f"slack {k}: {slackmin[k][0]}  @ {slackmin[k][1][:100]}")
    for k in sorted(viol):
        print(f"VIOL {k}: count={viol[k]['count']} min={viol[k]['min']}")
        for w in viol[k]["wit"][:5]:
            print("   ", str(w)[:170])


if __name__ == "__main__":
    main()
