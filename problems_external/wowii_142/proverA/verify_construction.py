#!/usr/bin/env python3
"""Executable twin of the PROOF_142_A construction.  Falsifier for every
branch of the proposed proof of the hard branch of C142.

Branches implemented EXACTLY as in the proof:
  g = 3   : T4 + T1 (verify f <= D-1 and D+1 >= f+2).
  g = 4   : dedicated route (verify hard => f = D-1; then find witness:
            distance-1 vertex with 1 edge to some diametral geodesic P, or
            swap + distance-2 vertex, or D = 2 and M(K) >= 1); verify the
            witness makes t >= f + 3 via Lemma M-P / M respectively.
  g >= 5  : bad zone (D <= g - 2*floor(g/3)):
              m = 1: V != V(K) -> single outside vertex component (window).
              m = 2 boxes (5,3,2),(8,4,3),(11,5,4): dichotomy
                depth >= 2 tail | ear pair | two nonadjacent singletons.
            good zone (D >= g - 2*floor(g/3) + 1): tails from x,b,w on ANY
            shortest cycle K; contact dichotomy:
              no contacts  -> 3 components, check sum h >= m (perimeter)
              contact      -> topmost merge -> one component, mass >= d(u,v)+1
            All impossibility claims asserted; forest validated against the
            Lemma-M predicate (exactly one edge into K \ {z} per component);
            final check: g - 1 + |F| >= f + ceil(2g/3)  (or D+1+|F| >= .. for
            the g=4 path-base branch).

Every graph in the corpus is processed; ANY assertion failure = proof bug.
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter, deque
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
W142 = ROOT.parent
PE = W142.parent
sys.path.insert(0, str(W142 / "bridge_oracle"))
for p in (PE / "wowii_141" / "oracle", PE / "wowii_144" / "oracle",
          PE / "wowii_144" / "wave2"):
    sys.path.insert(0, str(p))

from invariants import (  # noqa: E402
    all_pairs_dist, ecc_set, eccentricities, girth, graph_connected,
    nx_to_bitadj,
)
from bridge_tests import shortest_cycles  # noqa: E402
from bridge_oracle import build_corpus, bits_list, diametral_geodesic_sets  # noqa: E402
from lemma_e_tests import components_of_mask, edges_in_mask  # noqa: E402


def nbrs(adj, v):
    return bits_list(adj[v])


def dist_to_mask(dist_v, mask):
    best = None
    m = mask
    while m:
        b = m & -m
        m ^= b
        d = dist_v[b.bit_length() - 1]
        if best is None or d < best:
            best = d
    return best


def shortest_path_to_set(n, adj, dist, src, target_mask):
    """One shortest path src -> target set (list of vertices, src first,
    target vertex last), using distances to the set (greedy descent)."""
    dts = [dist_to_mask(dist[v], target_mask) for v in range(n)]
    path = [src]
    cur = src
    while dts[cur] > 0:
        for w in nbrs(adj, cur):
            if dts[w] == dts[cur] - 1:
                cur = w
                path.append(w)
                break
        else:
            raise AssertionError("no descent neighbor")
    return path


def check_lemma_m_forest(n, adj, kmask, z, fmask):
    """Lemma-M predicate: fmask subset of V-K, induces forest, every
    component sends exactly one edge into K - {z}.  Returns True/err."""
    if fmask & kmask:
        return "F intersects K"
    base = kmask & ~(1 << z)
    sz = fmask.bit_count()
    ne = edges_in_mask(adj, fmask)
    comps = components_of_mask(adj, fmask)
    if ne != sz - len(comps):
        return "not a forest"
    for cm in comps:
        tot = 0
        cc = cm
        while cc:
            b = cc & -cc
            cc ^= b
            tot += (adj[b.bit_length() - 1] & base).bit_count()
        if tot != 1:
            return f"component has {tot} edges into base"
    return True


def check_mp_forest(n, adj, pmask, fmask):
    """Lemma-M-P predicate: every component exactly one edge into P."""
    if fmask & pmask:
        return "F intersects P"
    sz = fmask.bit_count()
    ne = edges_in_mask(adj, fmask)
    comps = components_of_mask(adj, fmask)
    if ne != sz - len(comps):
        return "not a forest"
    for cm in comps:
        tot = 0
        cc = cm
        while cc:
            b = cc & -cc
            cc ^= b
            tot += (adj[b.bit_length() - 1] & pmask).bit_count()
        if tot != 1:
            return f"component has {tot} edges into P"
    return True


def geodesic_between(n, adj, dist, u, v):
    """One geodesic u..v as vertex list."""
    path = [u]
    cur = u
    while cur != v:
        for w in nbrs(adj, cur):
            if dist[w][v] == dist[cur][v] - 1:
                cur = w
                path.append(w)
                break
        else:
            raise AssertionError("geodesic step failed")
    return path


def run_g4(n, adj, dist, D, f, m, periph, g6s):
    """g=4 dedicated branch.  Returns ('ok', info) or raises."""
    assert f == D - 1, f"g4 hard case must have f=D-1, got f={f} D={D}"
    full = (1 << n) - 1
    # try all diametral geodesics: find P and a witness
    gsets, capped = diametral_geodesic_sets(n, adj, dist, D, 20000)
    assert gsets, "no diametral geodesic"
    for pm in sorted(gsets):
        # any outside vertex with exactly one edge into P?
        out = full & ~pm
        oo = out
        while oo:
            bb = oo & -oo
            oo ^= bb
            u = bb.bit_length() - 1
            if (adj[u] & pm).bit_count() == 1:
                err = check_mp_forest(n, adj, pm, bb)
                assert err is True, err
                assert D + 1 + 1 >= f + 3
                return "g4_direct"
    # all distance-1 outside vertices are 2-attached to every P; find a
    # distance-2 vertex and do the swap
    pm = min(gsets)
    pv = bits_list(pm)
    # order P
    ends = [v for v in pv if (adj[v] & pm).bit_count() == 1]
    assert len(ends) == 2
    order = [ends[0]]
    seen = 1 << ends[0]
    while len(order) < len(pv):
        for w in nbrs(adj, order[-1]):
            if (pm >> w & 1) and not (seen >> w & 1):
                order.append(w)
                seen |= 1 << w
                break
    dP = [dist_to_mask(dist[v], pm) for v in range(n)]
    far = [v for v in range(n) if dP[v] >= 2]
    if far:
        v2 = min(far, key=lambda v: dP[v])
        assert dP[v2] == 2
        # neighbor u of v2 with dP[u] = 1
        u = next(w for w in nbrs(adj, v2) if dP[w] == 1)
        att = [i for i, p in enumerate(order) if adj[u] >> p & 1]
        assert len(att) == 2 and att[1] - att[0] == 2, (att, "g4 window")
        i = att[0]
        newp = order[:i + 1] + [u] + order[i + 2:]
        pm2 = 0
        for p in newp:
            pm2 |= 1 << p
        # verify P' is a diametral geodesic (walk of length D b/w periph ends)
        assert len(newp) == D + 1
        for a in range(len(newp) - 1):
            assert adj[newp[a]] >> newp[a + 1] & 1
        assert dist[newp[0]][newp[-1]] == D
        err = check_mp_forest(n, adj, pm2, 1 << v2)
        assert err is True, err
        return "g4_swap"
    # everything within distance 1 of P and 2-attached: proof says D <= 2
    assert D == 2, f"g4 all-2-attached forces D<=2, got D={D} {g6s}"
    # D=2, f=1, m=1: M(K) >= 1
    K = sorted(next(iter(shortest_cycles_nx(g6s, 4))))
    return run_m1(n, adj, K, g6s)


def shortest_cycles_nx(g6s, g):
    G = nx.from_graph6_bytes(g6s.encode("ascii"))
    return shortest_cycles(G, g)


def run_m1(n, adj, kv, g6s):
    """m=1 closure: some outside vertex adjacent to K; component {u} with z
    kill if 2-attached (g=4) / unique attach (g>=5)."""
    km = 0
    for v in kv:
        km |= 1 << v
    full = (1 << n) - 1
    assert full & ~km, "V=V(K) but f>=1"
    # u adjacent to K, outside
    u = None
    for v in range(n):
        if not (km >> v & 1) and (adj[v] & km):
            u = v
            break
    assert u is not None, "connected => some outside vertex adjacent to K"
    att = bits_list(adj[u] & km)
    assert 1 <= len(att) <= 2, f"window violation {g6s}"
    if len(att) == 1:
        z = next(k for k in kv if k != att[0])
    else:
        z = att[0]
    err = check_lemma_m_forest(n, adj, km, z, 1 << u)
    assert err is True, err
    return "m1"


def run_m2_box(n, adj, dist, g, kv_list, g6s):
    """m=2 boxes (5,3,2),(8,4,3),(11,5,4): dichotomy proof."""
    for kv in kv_list:
        km = 0
        for v in kv:
            km |= 1 << v
        h = [dist_to_mask(dist[v], km) for v in range(n)]
        deep = [v for v in range(n) if h[v] >= 2]
        if deep:
            v = deep[0]
            path = shortest_path_to_set(n, adj, dist, v, km)
            tail = path[:-1]
            fmask = 0
            for q in tail:
                fmask |= 1 << q
            foot_att = bits_list(adj[path[-2]] & km)
            assert len(foot_att) == 1, "window g>=5"
            z = next(k for k in kv if k != foot_att[0])
            err = check_lemma_m_forest(n, adj, km, z, fmask)
            assert err is True, err
            assert fmask.bit_count() >= 2
            return "m2_tail"
    # all heights <= 1 for every shortest cycle; use the first K
    kv = kv_list[0]
    km = 0
    for v in kv:
        km |= 1 << v
    outside = [v for v in range(n) if not (km >> v & 1)]
    assert len(outside) >= 2, f"box forces >=2 outside {g6s}"
    # nonadjacent pair?
    pair = None
    for i, u1 in enumerate(outside):
        for u2 in outside[i + 1:]:
            if not (adj[u1] >> u2 & 1):
                pair = (u1, u2)
                break
        if pair:
            break
    if pair:
        u1, u2 = pair
        a1 = bits_list(adj[u1] & km)
        a2 = bits_list(adj[u2] & km)
        assert len(a1) == 1 and len(a2) == 1, "window g>=5"
        z = next(k for k in kv if k not in (a1[0], a2[0]))
        err = check_lemma_m_forest(n, adj, km, z, (1 << u1) | (1 << u2))
        assert err is True, err
        return "m2_two_singletons"
    # outside is a clique: at girth>=5 it has size exactly 2 (ear)
    assert len(outside) == 2, f"triangle-free clique <=2 {g6s}"
    u1, u2 = outside
    assert g == 5, f"adjacent outside pair impossible at g={g} {g6s}"
    a1 = bits_list(adj[u1] & km)
    a2 = bits_list(adj[u2] & km)
    assert len(a1) == 1 and len(a2) == 1
    z = a1[0]
    err = check_lemma_m_forest(n, adj, km, z, (1 << u1) | (1 << u2))
    assert err is True, err
    return "m2_ear"


def run_good_zone(n, adj, dist, g, D, f, m, periph, kv, g6s):
    """Good zone g>=5: tails from x,b,w on shortest cycle K (ANY K given);
    contact dichotomy.  Returns branch tag."""
    km = 0
    for v in kv:
        km |= 1 << v
    h = [dist_to_mask(dist[v], km) for v in range(n)]
    # realizer x, diametral pair (b,w)
    x = next(v for v in range(n) if dist_to_mask(dist[v], periph) == f)
    Bv = bits_list(periph)
    b = w = None
    for i, bb in enumerate(Bv):
        for ww in Bv[i + 1:]:
            if dist[bb][ww] == D:
                b, w = bb, ww
                break
        if b is not None:
            break
    assert b is not None
    trio = [(x, "x"), (b, "b"), (w, "w")]
    tails = {}
    feet = {}
    for v, tag in trio:
        if h[v] >= 1:
            path = shortest_path_to_set(n, adj, dist, v, km)
            tail = path[:-1]            # v = tail[0] ... foot = tail[-1]
            # index by height: tail[k] has height h[v]-k; reverse so
            # q[1..h] with q[j] at height j
            q = [None] + tail[::-1]     # q[j] = vertex at height j
            for j in range(1, len(q)):
                assert dist_to_mask(dist[q[j]], km) == j
                assert dist[v][q[j]] == h[v] - j
            tails[tag] = q
            fa = bits_list(adj[q[1]] & km)
            assert len(fa) == 1, f"foot window g>=5 {g6s}"
            feet[tag] = fa[0]
    # pairwise contacts
    def contacts(qa, qb):
        out = []
        for j in range(1, len(qa)):
            for i in range(1, len(qb)):
                if qa[j] == qb[i]:
                    out.append((j, i, 0))
                elif adj[qa[j]] >> qb[i] & 1:
                    out.append((j, i, 1))
        return out

    pair_names = [("b", "w"), ("x", "b"), ("x", "w")]
    vert_of = {"x": x, "b": b, "w": w}
    for ua, va in pair_names:
        if ua not in tails or va not in tails:
            continue
        con = contacts(tails[ua], tails[va])
        if not con:
            continue
        # merge branch
        qu, qv = tails[ua], tails[va]
        hu, hv = len(qu) - 1, len(qv) - 1
        phi = dist[vert_of[ua]][vert_of[va]]
        # contact inequality check (proof step)
        for (j, i, d) in con:
            assert i + j <= hu + hv + d - phi, (
                f"contact ineq fail {g6s} {(j,i,d,hu,hv,phi)}")
        j1 = max(j for (j, i, d) in con)
        at_top = [(j, i, d) for (j, i, d) in con if j == j1]
        d0 = [(j, i, d) for (j, i, d) in at_top if d == 0]
        z = None
        if d0:
            j1, i1, _ = d0[0]
            omass = set(qv[1:]) | {qu[j] for j in range(j1 + 1, hu + 1)}
            attach = [feet[va]]
        else:
            assert len(at_top) == 1, f"window: two cross at top {g6s}"
            j1, i1, _ = at_top[0]
            if j1 >= 2:
                omass = set(qv[1:]) | {qu[j] for j in range(j1, hu + 1)}
                attach = [feet[va]]
            else:
                # side swap
                conT = [(i, j, d) for (j, i, d) in con]
                i1p = max(i for (i, j, d) in conT)
                at_topT = [(i, j, d) for (i, j, d) in conT if i == i1p]
                d0T = [c for c in at_topT if c[2] == 0]
                if d0T:
                    i1p, jj, _ = d0T[0]
                    omass = set(qu[1:]) | {qv[i] for i in range(i1p + 1,
                                                                hv + 1)}
                    attach = [feet[ua]]
                elif i1p >= 2:
                    assert len(at_topT) == 1, f"window T {g6s}"
                    omass = set(qu[1:]) | {qv[i] for i in range(i1p, hv + 1)}
                    attach = [feet[ua]]
                else:
                    # unique contact (1,1,1): feet adjacent
                    assert con == [(1, 1, 1)], f"corner shape {g6s} {con}"
                    assert feet[ua] != feet[va], f"triangle corner {g6s}"
                    omass = set(qu[1:]) | set(qv[1:])
                    z = feet[va]
                    attach = [feet[ua]]
        if z is None:
            z = next(k for k in kv if k not in attach)
        fmask = 0
        for q in omass:
            fmask |= 1 << q
        err = check_lemma_m_forest(n, adj, km, z, fmask)
        assert err is True, f"{g6s} merge invalid: {err}"
        comps = components_of_mask(adj, fmask)
        assert len(comps) == 1, f"{g6s} merged not single component"
        assert fmask.bit_count() >= phi + 1, (
            f"{g6s} merge mass {fmask.bit_count()} < phi+1={phi+1}")
        assert fmask.bit_count() >= m, f"{g6s} merge mass < m"
        assert g - 1 + fmask.bit_count() >= f + (2 * g + 2) // 3
        return f"merge_{ua}{va}"
    # no contacts anywhere: three tails
    hsum = sum(len(q) - 1 for q in tails.values())
    # perimeter guarantee
    kx = tails["x"][1] if "x" in tails else x
    kb = tails["b"][1] if "b" in tails else b
    kw = tails["w"][1] if "w" in tails else w
    # gates = feet (or the vertex itself if on K)
    gx = feet.get("x", x)
    gb = feet.get("b", b)
    gw = feet.get("w", w)
    pos = {v: i for i, v in enumerate(kv)}
    # d_K between gates via cycle positions: need K in cyclic order
    # (kv is sorted, not cyclic!) -- compute d_K by BFS on K alone
    dK = {}
    kmset = set(kv)
    for a in (gx, gb, gw):
        dd = {a: 0}
        dq = deque([a])
        while dq:
            c = dq.popleft()
            for t in nbrs(adj, c):
                if t in kmset and t not in dd:
                    dd[t] = dd[c] + 1
                    dq.append(t)
        dK[a] = dd
    s_pair = dK[gx].get(gb, 10 ** 9) + dK[gx].get(gw, 10 ** 9) \
        + dK[gb].get(gw, 10 ** 9)
    assert s_pair <= g, f"{g6s} cycle perimeter violated"
    lhs = 2 * f + D - s_pair
    assert 2 * hsum >= lhs - 0, f"{g6s} gate-triangle chain broken"
    assert hsum >= m, (
        f"{g6s} PERIMETER BRANCH FAIL hsum={hsum} m={m} "
        f"h=({h[x]},{h[b]},{h[w]}) dK sum={s_pair} f={f} D={D} g={g}")
    fmask = 0
    for q in tails.values():
        for v in q[1:]:
            fmask |= 1 << v
    z = next(k for k in kv if k not in feet.values())
    err = check_lemma_m_forest(n, adj, km, z, fmask)
    assert err is True, f"{g6s} three-tail forest invalid: {err}"
    assert g - 1 + fmask.bit_count() >= f + (2 * g + 2) // 3
    return "three_tails"


def eval_one(task):
    name, g6s = task
    G = nx.from_graph6_bytes(g6s.encode("ascii"))
    n, adj = nx_to_bitadj(G)
    if n < 2 or not graph_connected(n, adj):
        return None
    g = girth(n, adj)
    if g == 0:
        return None
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    D = max(ecc)
    periph = 0
    for v in range(n):
        if ecc[v] == D:
            periph |= 1 << v
    f = ecc_set(n, dist, periph)
    c23 = (2 * g + 2) // 3
    s = f + c23 - D - 1
    m = f + 1 - g // 3
    try:
        if g == 3:
            assert f <= D - 1 or D == 0
            assert D + 1 >= f + 2 or f == 0
            return ("g3", None)
        if s <= 0:
            return ("T1", None)
        if m <= 0:
            return ("T2", None)
        # hard branch
        if g == 4:
            tag = run_g4(n, adj, dist, D, f, m, periph, g6s)
            return (tag, None)
        Ks = [sorted(K) for K in shortest_cycles(G, g)]
        if D <= g - 2 * (g // 3):
            # bad zone boxes
            box = (g, D, f)
            assert box in {(5, 2, 1), (5, 3, 1), (5, 3, 2), (7, 3, 2),
                           (8, 4, 2), (8, 4, 3), (11, 5, 3), (11, 5, 4)}, \
                f"unexpected bad-zone box {box} {g6s}"
            if m == 1:
                return (run_m1(n, adj, Ks[0], g6s), None)
            assert m == 2
            return (run_m2_box(n, adj, dist, g, Ks, g6s), None)
        # good zone: run for EVERY shortest cycle (proof claims any K works)
        tags = Counter()
        for kv in Ks[:50]:
            tag = run_good_zone(n, adj, dist, g, D, f, m, periph, kv, g6s)
            tags[tag] += 1
        return ("good:" + ",".join(sorted(tags)), None)
    except AssertionError as e:
        return ("FAIL", f"{name} [{g6s}] n={n} g={g} D={D} f={f} m={m}: {e}")


def main():
    t0 = time.time()
    tasks = build_corpus()
    print(f"corpus: {len(tasks)}", flush=True)
    tags = Counter()
    fails = []
    with Pool(8) as pool:
        for rec in pool.imap_unordered(eval_one, tasks, chunksize=32):
            if rec is None:
                continue
            tag, err = rec
            tags[tag] += 1
            if tag == "FAIL":
                fails.append(err)
    print("branch tags:")
    for k, v in sorted(tags.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v}")
    print("FAILURES:", len(fails))
    for e in fails[:40]:
        print("  ", e)
    json.dump({"tags": dict(tags), "failures": fails},
              open(ROOT / "verify_construction_results.json", "w"), indent=2)
    print(f"total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
