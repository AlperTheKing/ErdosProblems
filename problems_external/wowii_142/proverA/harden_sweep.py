#!/usr/bin/env python3
"""Hardening sweep for the PROOF_142_A construction (fresh seed 987654321).

1. 20k+ fresh random graphs (cycle+random forests, forced girth, random
   bipartite, theta/chorded, subdivisions) run through the full construction
   simulator, iterating over ALL realizers x (cap 6), ALL diametral pairs
   (cap 8), ALL shortest cycles (cap 25), and all 3 merge-pair orders.
2. Unit test of the g=4 swap lemma on every girth-4 graph encountered:
   for every diametral geodesic P, every 2-attached u in N(P), every
   neighbor v of u with d(v,P)=2: P' = swap(P,u) is a diametral geodesic
   and {v} is a valid M-P' component.
3. Random search for members of the suspect-vacuous bad-zone boxes
   (7,3,2),(8,4,2),(8,4,3),(11,5,3),(11,5,4),(5,2,1) — report any found
   and run the box dichotomy on them.
"""

from __future__ import annotations

import random
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
W142 = ROOT.parent
PE = W142.parent
sys.path.insert(0, str(W142 / "bridge_oracle"))
sys.path.insert(0, str(ROOT))
for p in (PE / "wowii_141" / "oracle", PE / "wowii_144" / "oracle",
          PE / "wowii_144" / "wave2"):
    sys.path.insert(0, str(p))

from invariants import (  # noqa: E402
    all_pairs_dist, ecc_set, eccentricities, girth, graph_connected,
    nx_to_bitadj,
)
from bridge_tests import shortest_cycles  # noqa: E402
from bridge_oracle import bits_list, diametral_geodesic_sets  # noqa: E402
from route_b_tests import (  # noqa: E402
    chorded_cycle, cycle_random_legs, cycle_random_trees,
    forced_girth_random, gen_theta,
)
import verify_construction as VC  # noqa: E402

SEED = 987654321


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


# ------------------------------------------------------------ generators

def forked_cycle(rng):
    """Cycle + forking trees: designed to force shared components and
    tail contacts."""
    g = rng.randrange(5, 16)
    G = nx.cycle_graph(g)
    nid = g
    for _ in range(rng.randrange(1, 4)):
        pos = rng.randrange(g)
        stem = rng.randrange(0, 4)
        cur = pos
        for _ in range(stem):
            G.add_edge(cur, nid)
            cur = nid
            nid += 1
        arms = rng.randrange(2, 4)
        for _ in range(arms):
            c2 = cur
            for _ in range(rng.randrange(1, 7)):
                G.add_edge(c2, nid)
                c2 = nid
                nid += 1
    return f"forked(g={g})", G


def double_ear(rng):
    """Cycle + ears (paths between two cycle vertices) keeping girth."""
    g = rng.randrange(5, 14)
    G = nx.cycle_graph(g)
    nid = g
    for _ in range(rng.randrange(1, 3)):
        a = rng.randrange(g)
        span = rng.randrange(2, g - 1)
        b = (a + span) % g
        arc = min(span, g - span)
        L = max(g - arc, arc) + rng.randrange(0, 4)   # ear length >= g - arc
        cur = a
        for _ in range(L - 1):
            G.add_edge(cur, nid)
            cur = nid
            nid += 1
        G.add_edge(cur, b)
    if girth(*nx_to_bitadj(nx.convert_node_labels_to_integers(G))) < g:
        return None
    return f"doubleEar(g={g})", G


def build_extra_corpus():
    rng = random.Random(SEED)
    out = []
    for _ in range(6000):
        out.append(cycle_random_legs(rng))
    for _ in range(5000):
        out.append(cycle_random_trees(rng))
    for _ in range(2000):
        out.append(chorded_cycle(rng))
    for _ in range(1500):
        out.append(gen_theta(rng))
    for _ in range(4000):
        r = forked_cycle(rng)
        out.append(r)
    for _ in range(2500):
        r = double_ear(rng)
        if r is not None:
            out.append(r)
    got = tries = 0
    while got < 1500 and tries < 30000:
        tries += 1
        r = forced_girth_random(rng, gmin=5)
        if r is not None:
            out.append(r)
            got += 1
    got = tries = 0
    while got < 800 and tries < 16000:
        tries += 1
        r = forced_girth_random(rng, gmin=4)
        if r is not None:
            out.append(r)
            got += 1
    for i in range(1200):
        a = rng.randrange(3, 9)
        b = rng.randrange(3, 9)
        p = (0.25, 0.4, 0.6)[i % 3]
        G = nx.bipartite.random_graph(a, b, p, seed=rng.randrange(2 ** 31))
        if G.number_of_nodes() >= 2 and nx.is_connected(G):
            out.append((f"bip({a},{b},{p})", G))
    tasks, seen = [], set()
    for item in out:
        if item is None:
            continue
        name, G = item
        if G is None or G.number_of_nodes() < 2 or not nx.is_connected(G):
            continue
        Gi = nx.convert_node_labels_to_integers(G)
        g6s = nx.to_graph6_bytes(Gi, header=False).decode().strip()
        if g6s in seen:
            continue
        seen.add(g6s)
        tasks.append((name, g6s))
    return tasks


# ------------------------------------------------------------ g4 swap unit

def g4_swap_unit(n, adj, dist, D, g6s):
    """Test swap lemma instances; returns number tested."""
    tested = 0
    gsets, _ = diametral_geodesic_sets(n, adj, dist, D, 300)
    for pm in sorted(gsets)[:20]:
        pv = bits_list(pm)
        ends = [v for v in pv if (adj[v] & pm).bit_count() == 1]
        if len(ends) != 2:
            continue
        order = [ends[0]]
        seen = 1 << ends[0]
        while len(order) < len(pv):
            nxt = None
            for w in VC.nbrs(adj, order[-1]):
                if (pm >> w & 1) and not (seen >> w & 1):
                    nxt = w
                    break
            if nxt is None:
                break
            order.append(nxt)
            seen |= 1 << nxt
        if len(order) != len(pv):
            continue
        for u in range(n):
            if pm >> u & 1:
                continue
            att = [i for i, p in enumerate(order) if adj[u] >> p & 1]
            if len(att) != 2:
                continue
            assert att[1] - att[0] == 2, f"g4 window {g6s}"
            i = att[0]
            for v in VC.nbrs(adj, u):
                if dist_to_mask(dist[v], pm) != 2:
                    continue
                newp = order[:i + 1] + [u] + order[i + 2:]
                pm2 = 0
                for p in newp:
                    pm2 |= 1 << p
                assert len(newp) == D + 1
                for a in range(len(newp) - 1):
                    assert adj[newp[a]] >> newp[a + 1] & 1, f"walk {g6s}"
                assert dist[newp[0]][newp[-1]] == D
                err = VC.check_mp_forest(n, adj, pm2, 1 << v)
                assert err is True, f"swap unit {g6s}: {err}"
                tested += 1
    return tested


# ------------------------------------------------------------ full check

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
    tags = Counter()
    fails = []
    swap_units = 0
    boxes_found = []
    try:
        if g == 4 and D >= 2:
            swap_units = g4_swap_unit(n, adj, dist, D, g6s)
        if g == 3:
            if f >= 1:
                assert f <= D - 1 and D + 1 >= f + 2
            tags["g3"] += 1
            return (tags, fails, swap_units, boxes_found)
        if s <= 0 or m <= 0:
            tags["easy"] += 1
            return (tags, fails, swap_units, boxes_found)
        if g == 4:
            tags[VC.run_g4(n, adj, dist, D, f, m, periph, g6s)] += 1
            return (tags, fails, swap_units, boxes_found)
        Ks = [sorted(K) for K in shortest_cycles(G, g)]
        if D <= g - 2 * (g // 3):
            box = (g, D, f)
            boxes_found.append(box)
            assert box in {(5, 2, 1), (5, 3, 1), (5, 3, 2), (7, 3, 2),
                           (8, 4, 2), (8, 4, 3), (11, 5, 3), (11, 5, 4)}, \
                f"unexpected box {box} {g6s}"
            if m == 1:
                tags[VC.run_m1(n, adj, Ks[0], g6s)] += 1
            else:
                tags[VC.run_m2_box(n, adj, dist, g, Ks, g6s)] += 1
            return (tags, fails, swap_units, boxes_found)
        # good zone: all K (cap 25) x all realizers (cap 6) x all pairs (cap 8)
        X = [v for v in range(n)
             if dist_to_mask(dist[v], periph) == f][:6]
        Bv = bits_list(periph)
        pairs = [(bb, ww) for i, bb in enumerate(Bv) for ww in Bv[i + 1:]
                 if dist[bb][ww] == D][:8]
        for kv in Ks[:25]:
            for x in X:
                for (b, w) in pairs:
                    tag = run_good_zone_choice(n, adj, dist, g, D, f, m,
                                               x, b, w, kv, g6s)
                    tags[tag] += 1
        return (tags, fails, swap_units, boxes_found)
    except AssertionError as e:
        fails.append(f"{name} [{g6s}] n={n} g={g} D={D} f={f} m={m}: {e}")
        return (tags, fails, swap_units, boxes_found)


def run_good_zone_choice(n, adj, dist, g, D, f, m, x, b, w, kv, g6s):
    """Same as VC.run_good_zone but with prescribed x, b, w."""
    import types
    # monkey-ish: inline the body with fixed trio
    km = 0
    for v in kv:
        km |= 1 << v
    h = [dist_to_mask(dist[v], km) for v in range(n)]
    trio = [(x, "x"), (b, "b"), (w, "w")]
    tails = {}
    feet = {}
    for v, tag in trio:
        if h[v] >= 1:
            path = VC.shortest_path_to_set(n, adj, dist, v, km)
            tail = path[:-1]
            q = [None] + tail[::-1]
            for j in range(1, len(q)):
                assert dist_to_mask(dist[q[j]], km) == j
                assert dist[v][q[j]] == h[v] - j
            tails[tag] = q
            fa = bits_list(adj[q[1]] & km)
            assert len(fa) == 1, f"foot window {g6s}"
            feet[tag] = fa[0]

    def contacts(qa, qb):
        out = []
        for j in range(1, len(qa)):
            for i in range(1, len(qb)):
                if qa[j] == qb[i]:
                    out.append((j, i, 0))
                elif adj[qa[j]] >> qb[i] & 1:
                    out.append((j, i, 1))
        return out

    vert_of = {"x": x, "b": b, "w": w}
    from lemma_e_tests import components_of_mask
    for ua, va in [("b", "w"), ("x", "b"), ("x", "w")]:
        if ua not in tails or va not in tails:
            continue
        con = contacts(tails[ua], tails[va])
        if not con:
            continue
        qu, qv = tails[ua], tails[va]
        hu, hv = len(qu) - 1, len(qv) - 1
        phi = dist[vert_of[ua]][vert_of[va]]
        for (j, i, d) in con:
            assert i + j <= hu + hv + d - phi, f"contact ineq {g6s}"
            if d == 0:
                assert i == j, f"shared level mismatch {g6s}"
            else:
                assert abs(i - j) <= 1, f"cross level gap {g6s}"
        j1 = max(j for (j, i, d) in con)
        at_top = [(j, i, d) for (j, i, d) in con if j == j1]
        d0 = [c for c in at_top if c[2] == 0]
        z = None
        if d0:
            j1, i1, _ = d0[0]
            omass = set(qv[1:]) | {qu[j] for j in range(j1 + 1, hu + 1)}
            attach = [feet[va]]
        else:
            assert len(at_top) == 1, f"two cross at top {g6s}"
            j1, i1, _ = at_top[0]
            if j1 >= 2:
                omass = set(qv[1:]) | {qu[j] for j in range(j1, hu + 1)}
                attach = [feet[va]]
            else:
                conT = [(i, j, d) for (j, i, d) in con]
                i1p = max(i for (i, j, d) in conT)
                at_topT = [c for c in conT if c[0] == i1p]
                d0T = [c for c in at_topT if c[2] == 0]
                if d0T:
                    i1p = d0T[0][0]
                    omass = set(qu[1:]) | {qv[i]
                                           for i in range(i1p + 1, hv + 1)}
                    attach = [feet[ua]]
                elif i1p >= 2:
                    assert len(at_topT) == 1, f"two cross at topT {g6s}"
                    omass = set(qu[1:]) | {qv[i] for i in range(i1p, hv + 1)}
                    attach = [feet[ua]]
                else:
                    assert set(con) == {(1, 1, 1)}, f"corner {g6s} {con}"
                    assert feet[ua] != feet[va], f"triangle {g6s}"
                    omass = set(qu[1:]) | set(qv[1:])
                    z = feet[va]
                    attach = [feet[ua]]
        if z is None:
            z = next(k for k in kv if k not in attach)
        fmask = 0
        for q in omass:
            fmask |= 1 << q
        err = VC.check_lemma_m_forest(n, adj, km, z, fmask)
        assert err is True, f"{g6s} merge: {err}"
        assert len(components_of_mask(adj, fmask)) == 1, f"{g6s} comps"
        assert fmask.bit_count() >= phi + 1, f"{g6s} mass<phi+1"
        assert fmask.bit_count() >= m, f"{g6s} mass<m"
        return f"merge_{ua}{va}"
    hsum = sum(len(q) - 1 for q in tails.values())
    assert hsum >= m, f"{g6s} perimeter fail hsum={hsum} m={m}"
    fmask = 0
    for q in tails.values():
        for v in q[1:]:
            fmask |= 1 << v
    z = next(k for k in kv if k not in feet.values())
    err = VC.check_lemma_m_forest(n, adj, km, z, fmask)
    assert err is True, f"{g6s} three-tails: {err}"
    return "three_tails"


def main():
    t0 = time.time()
    tasks = build_extra_corpus()
    print(f"extra corpus: {len(tasks)}", flush=True)
    tags = Counter()
    fails = []
    swap_total = 0
    boxes = Counter()
    with Pool(8) as pool:
        for rec in pool.imap_unordered(eval_one, tasks, chunksize=16):
            if rec is None:
                continue
            tg, fl, su, bx = rec
            tags.update(tg)
            fails.extend(fl)
            swap_total += su
            boxes.update(bx)
    print("tags:", dict(sorted(tags.items(), key=lambda kv: -kv[1])))
    print("g4 swap unit instances validated:", swap_total)
    print("bad-zone boxes encountered:", dict(boxes))
    print("FAILURES:", len(fails))
    for e in fails[:40]:
        print("  ", e)
    print(f"total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
