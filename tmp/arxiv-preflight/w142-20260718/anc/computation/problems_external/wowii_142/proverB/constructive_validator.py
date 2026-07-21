#!/usr/bin/env python3
"""Angle B step 3: CONSTRUCTIVE validation of the complete proof of C142's
hard branch (G connected cyclic, f >= 1): execute the proof's construction
verbatim on every corpus graph and verify the produced certificate exactly.

Proof case tree (t target = f + ceil(2g/3); q := f + 1 - floor(g/3)):
  P0  g = 3:            t >= D+1 >= f+2           [T4: f <= D-1; no cert]
  P1  g >= 4, f <= floor(g/3)-1: t >= g-1          [T2; no cert]
  (g = 4 only:) after T1-peel f = D-1 (T4+T1):
  P2  g = 4, D = 2:     cycle cert M(K) >= 1  -> tree of g-1+1 = 4 = f+3
  P3  g = 4, D >= 3:    path cert M_P >= 1 on P or rerouted P'
                        -> tree of D+2 = f+3
  (g >= 5:)
  P4  f >= g - 2*floor(g/3): THREE-POINT LEMMA on any shortest cycle K:
      descents T_x, T_b, T_w from x (f-realizer), (b0,w0) (diametral pair);
      if some pair interacts -> SPLICE component U, |U| >= d(pair)+1 >= q;
      else 3 tails, S3 = hx+hb+hw >= ceil((2f+D-g)/2) >= q
      -> tree of g-1+q >= f+ceil(2g/3)
  P5  g >= 5, f = floor(g/3) (q=1): singleton depth-1 cert
  P6  g >= 5, f = floor(g/3)+1 (q=2, g = 2 mod 3):
      ecc(K) >= 2 -> 2-tail; else all depth 1: n >= g+2 -> two depth-1
      vertices (2 singletons or adjacent pair + z); n = g+1 -> tadpole(g,1)
      whose f = ceil(floor(g/2)/2) <= floor(g/3) contradicts f = floor(g/3)+1
      (case vacuous; verified).

Certificates are verified from scratch:
  cycle cert (K, z, F): F cap K = empty; G[F] forest; every component of
      G[F] sends exactly one edge into K-{z} (edges to z unrestricted);
      THEN G[(K-{z}) u F] must be an induced tree; size g-1+|F| >= f+c23.
  path cert (P, F): P an induced path; every component of G[F] sends exactly
      one edge into P; G[P u F] induced tree; size |P|+|F| >= f+c23.
Every certificate is checked by networkx is_tree on the induced subgraph.
Failures are collected and dumped; ANY failure = gap in the proof.
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

RNG = None      # set by --seed: randomize all free choices of the proof

ROOT = Path(__file__).resolve().parent
W142 = ROOT.parent
PE = W142.parent
sys.path.insert(0, str(W142 / "bridge_oracle"))
sys.path.insert(0, str(PE / "wowii_141" / "oracle"))
sys.path.insert(0, str(PE / "wowii_144" / "oracle"))
sys.path.insert(0, str(PE / "wowii_144" / "wave2"))

from invariants import (  # noqa: E402
    all_pairs_dist, ecc_set, eccentricities, girth, graph_connected,
    nx_to_bitadj)
from bridge_tests import shortest_cycles  # noqa: E402
from bridge_oracle import bits_list, build_corpus  # noqa: E402

OUT = ROOT / "constructive_validator_results.json"
EQ_JSON = W142 / "oracle" / "equality_cases.json"


# ------------------------------------------------------------ basic helpers

def dist_to_mask(n, adj, mask):
    INF = 10 ** 9
    dist = [INF] * n
    frontier = []
    for v in bits_list(mask):
        dist[v] = 0
        frontier.append(v)
    d = 0
    while frontier:
        d += 1
        nxt = []
        for u in frontier:
            nb = adj[u]
            while nb:
                b = nb & -nb
                nb ^= b
                w = b.bit_length() - 1
                if dist[w] > d:
                    dist[w] = d
                    nxt.append(w)
        frontier = nxt
    return dist


def descent(n, adj, dK, u):
    """Geodesic descent u -> K (excluding the K-vertex): [u, ..., depth-1].
    Deterministic: smallest-index neighbor of smaller depth (random when
    RNG is set: the proof must be choice-independent)."""
    path = []
    cur = u
    while dK[cur] > 0:
        path.append(cur)
        cands = []
        nb = adj[cur]
        while nb:
            b = nb & -nb
            nb ^= b
            w = b.bit_length() - 1
            if dK[w] == dK[cur] - 1:
                cands.append(w)
        cur = RNG.choice(cands) if RNG else min(cands)
    return path            # ordered u (depth h) ... bottom (depth 1)


def check_cycle_cert(G, n, adj, Kl, z, F, need, ctx):
    """Verify Lemma-M certificate; return error string or None."""
    km = 0
    for v in Kl:
        km |= 1 << v
    fs = set()
    for comp in F:
        for v in comp:
            if v in fs:
                return f"{ctx}: overlapping F vertices"
            fs.add(v)
    if any((1 << v) & km for v in fs):
        return f"{ctx}: F intersects K"
    H = G.subgraph(fs)
    if H.number_of_nodes() and not nx.is_forest(H):
        return f"{ctx}: G[F] not forest"
    comps_actual = [set(c) for c in nx.connected_components(H)] if fs else []
    declared = [set(c) for c in F]
    if sorted(map(sorted, comps_actual)) != sorted(map(sorted, declared)):
        return f"{ctx}: declared components mismatch actual"
    kz = km & ~(1 << z)
    for comp in declared:
        cnt = 0
        for v in comp:
            cnt += (adj[v] & kz).bit_count()
        if cnt != 1:
            return f"{ctx}: component {sorted(comp)} sends {cnt} edges"
    treeset = set(bits_list(kz)) | fs
    T = G.subgraph(treeset)
    if not nx.is_tree(T):
        return f"{ctx}: G[(K-z) u F] not a tree"
    if len(treeset) < need:
        return f"{ctx}: size {len(treeset)} < needed {need}"
    return None


def check_path_cert(G, n, adj, Pl, F, need, ctx):
    pm = 0
    for v in Pl:
        pm |= 1 << v
    Pi = G.subgraph(Pl)
    if not (nx.is_tree(Pi) and max(dict(Pi.degree()).values()) <= 2
            and Pi.number_of_edges() == len(Pl) - 1):
        return f"{ctx}: P not an induced path"
    fs = set()
    for comp in F:
        fs.update(comp)
    if any((1 << v) & pm for v in fs):
        return f"{ctx}: F intersects P"
    H = G.subgraph(fs)
    if fs and not nx.is_forest(H):
        return f"{ctx}: G[F] not forest"
    for comp in ([set(c) for c in nx.connected_components(H)] if fs else []):
        cnt = 0
        for v in comp:
            cnt += (adj[v] & pm).bit_count()
        if cnt != 1:
            return f"{ctx}: component sends {cnt} edges into P"
    treeset = set(Pl) | fs
    T = G.subgraph(treeset)
    if not nx.is_tree(T):
        return f"{ctx}: G[P u F] not a tree"
    if len(treeset) < need:
        return f"{ctx}: size {len(treeset)} < needed {need}"
    return None


# ------------------------------------------------------- splice machinery

def interactions(Tu, Tv, adj):
    """List of (j, i): Tv[j'] (depth j) shares/adjacent with Tu[i'] (depth i).
    Depth of Tu[k] is len(Tu)-k ... we store paths ordered top..bottom, so
    depth of element idx k in Tu is len(Tu)-k.  Returns list of
    (depth_on_Tv, depth_on_Tu)."""
    out = []
    hu, hv = len(Tu), len(Tv)
    for jj, tv in enumerate(Tv):
        dv = hv - jj
        for ii, tu in enumerate(Tu):
            du = hu - ii
            if tv == tu or (adj[tv] >> tu) & 1:
                out.append((dv, du, tv, tu))
    return out


def three_point(G, n, adj, dist, Kl, x, b0, w0, f, g, D, q):
    """Execute the three-point lemma; return (kind, cert) where cert is
    (K, z, F components).  Raises AssertionError on internal gap."""
    km = 0
    for v in Kl:
        km |= 1 << v
    dK = dist_to_mask(n, adj, km)
    tails = {}
    for u in (x, b0, w0):
        tails[u] = descent(n, adj, dK, u) if dK[u] > 0 else []
    pairs = [(b0, w0, D), (x, b0, dist[x][b0]), (x, w0, dist[x][w0])]
    for (u, v, duv) in pairs:
        Tu, Tv = tails[u], tails[v]
        if not Tu or not Tv or u == v:
            continue
        inter = interactions(Tu, Tv, adj)
        if not inter:
            continue
        # SPLICE on this pair
        hu, hv = len(Tu), len(Tv)
        # case A: v on Tu (shared vertex at max must be v itself)
        if v in Tu:
            U = list(Tu)
            assert len(U) >= duv + 1, "splice A size"
            comp = U
            atts = [w for w in Kl if any((adj[t] >> w) & 1 for t in comp)]
            # single attachment expected (bottom, g>=5)
            assert len(set(atts)) == 1, f"splice A attachments {atts}"
            z = next(w for w in Kl if w != atts[0])
            return ("splice_A", (Kl, z, [comp]))
        nu_v = max(j for (j, i, tv, tu) in inter)
        # s' = Tv vertex at depth nu_v; kept = depths >= nu_v
        sprime = Tv[hv - nu_v]
        assert sprime not in Tu, "shared vertex at max depth (not v): gap!"
        nbrs_in_Tu = [t for t in Tu if (adj[sprime] >> t) & 1]
        assert len(nbrs_in_Tu) == 1, f"s' has {len(nbrs_in_Tu)} Tu-nbrs"
        kept = Tv[:hv - nu_v + 1]        # depths hv .. nu_v
        U = list(Tu) + kept
        assert len(set(U)) == len(U), "splice B overlap"
        nu_u = len(Tu) - Tu.index(nbrs_in_Tu[0])
        assert len(U) >= duv + nu_u and len(U) >= duv + 1, "splice B size"
        katt = [w for w in Kl if any((adj[t] >> w) & 1 for t in U)]
        if nu_v == 1:
            assert len(set(katt)) == 2, f"splice B nu=1 atts {katt}"
            a_bot = [w for w in Kl if (adj[Tu[-1]] >> w) & 1]
            a_sp = [w for w in Kl if (adj[sprime] >> w) & 1]
            assert len(a_bot) == 1 and len(a_sp) == 1 and a_bot != a_sp
            z = a_sp[0]
        else:
            assert len(set(katt)) == 1, f"splice B atts {katt}"
            z = next(w for w in Kl if w != katt[0])
        return ("splice_B", (Kl, z, [U]))
    # no interaction anywhere: three separate tails
    comps = [t for t in (tails[x], tails[b0], tails[w0]) if t]
    # dedupe identical vertex sets (x=b0 impossible; but tails could... no)
    S3 = sum(len(t) for t in comps)
    assert 2 * f + D <= 2 * S3 + g, "3-arc bound violated?!"
    assert S3 >= q, "S3 < q with no interaction: gap!"
    atts = set()
    for t in comps:
        a = [w for w in Kl if (adj[t[-1]] >> w) & 1]
        assert len(a) == 1, f"tail bottom multi-attach {a}"
        atts.add(a[0])
    z = next(w for w in Kl if w not in atts)
    return ("three_tails", (Kl, z, comps))


# ------------------------------------------------------------ main routine

def prove_one(name, g6s):
    """Return (branch_tag, error_or_None)."""
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
    Bl = bits_list(periph)
    f = ecc_set(n, dist, periph)
    if f == 0:
        return None                       # not the hard branch
    c23 = (2 * g + 2) // 3
    fl3 = g // 3
    q = f + 1 - fl3
    need = f + c23
    ctx = f"{name}[{g6s}] n={n} g={g} D={D} f={f}"
    t_true = None                          # computed only on failure paths

    if g == 3:
        if not f <= D - 1:
            return ("P0", f"{ctx}: T4 violated")
        return ("P0", None)                # t >= D+1 >= f+2, rigorous
    if f <= fl3 - 1:
        return ("P1", None)                # T2
    # x realizer, diametral pair (first deterministic choices, or random)
    xs = [v for v in range(n) if min(dist[v][b] for b in Bl) == f]
    prs = [(b, w) for b in range(n) for w in range(n) if dist[b][w] == D]
    x = RNG.choice(xs) if RNG else xs[0]
    b0, w0 = RNG.choice(prs) if RNG else prs[0]

    if g == 4:
        if f != D - 1:
            # T1 must close: f <= D+1-3 = D-2
            return ("P1t1", None if f <= D - 2 else
                    (f"{ctx}: g4 slice broken"))
        Ks = shortest_cycles(G, g)
        Kl = sorted(RNG.choice(Ks) if RNG else Ks[0])
        # order cycle
        Kl = order_cycle(G, Kl)
        if D == 2:
            # proof: VACUOUS (f>=1, D=2 -> universal non-peripheral vertex
            # -> girth 3); reaching here is a gap
            return ("P2", f"{ctx}: g=4 D=2 f>=1 reached (should be vacuous)")
        # D >= 3: path certificate
        P = geodesic(n, adj, dist, b0, w0)
        pm = 0
        for v in P:
            pm |= 1 << v
        dP = dist_to_mask(n, adj, pm)
        delta = dP[x]
        if delta < 1:
            return ("P3", f"{ctx}: delta=0 at g=4 D>=3")
        Tx = descent(n, adj, dP, x)        # descent to P
        u1 = Tx[-1]
        att = [i for i, p in enumerate(P) if (adj[u1] >> p) & 1]
        if len(att) == 1:
            err = check_path_cert(G, n, adj, P, [[u1]], D + 2, ctx)
            return ("P3a", err)
        if len(att) == 2 and att[1] - att[0] == 2:
            if delta == 1:
                return ("P3", f"{ctx}: x double-attaches, delta=1: gap!")
            a = att[0]
            P2 = P[:a + 1] + [u1] + P[a + 2:]
            u2 = Tx[-2]
            err = check_path_cert(G, n, adj, P2, [[u2]], D + 2, ctx)
            return ("P3b", err)
        return ("P3", f"{ctx}: unexpected attach pattern {att}")

    # g >= 5
    Ks = shortest_cycles(G, g)
    Kpick = sorted(RNG.choice(Ks) if RNG else Ks[0])
    if f >= g - 2 * fl3:
        Kl = order_cycle(G, Kpick)
        try:
            kind, (Kl2, z, F) = three_point(G, n, adj, dist, Kl,
                                            x, b0, w0, f, g, D, q)
        except AssertionError as e:
            return ("P4", f"{ctx}: three_point assert: {e}")
        err = check_cycle_cert(G, n, adj, Kl2, z, F, g - 1 + q, ctx)
        # note: tree size is g-1+|F|>=g-1+q = need exactly when |F|=q;
        # |F| can exceed q - the cert needs >= need = f+c23 = g-1+q
        return (f"P4_{kind}", err)
    # leftover: f in {fl3, fl3+1}, q in {1,2}
    Kl = order_cycle(G, Kpick)
    km = 0
    for v in Kl:
        km |= 1 << v
    dK = dist_to_mask(n, adj, km)
    if q == 1:
        if n == g:
            return ("P5", f"{ctx}: G=C_g but f>=1?!")
        v = next(v for v in range(n) if dK[v] == 1)
        return ("P5", attach_with_z(G, n, adj, Kl, [[v]], need, ctx))
    if q == 2:
        hK = max(dK)
        if hK >= 2:
            v = next(v for v in range(n) if dK[v] == hK)
            T = descent(n, adj, dK, v)[-2:]
            return ("P6a", attach_with_z(G, n, adj, Kl, [T], need, ctx))
        if n == g + 1:
            # proof: this case is VACUOUS (tadpole(g,1) has
            # f = ceil(floor(g/2)/2) <= floor(g/3) < floor(g/3)+1 = f);
            # reaching it at all is a gap
            return ("P6c", f"{ctx}: n=g+1 reached with q=2 (should be "
                           f"vacuous; tadpole f={(g // 2 + 1) // 2})")
        d1 = [v for v in range(n) if dK[v] == 1]
        if len(d1) < 2:
            return ("P6", f"{ctx}: fewer than 2 depth-1 vertices")
        v = d1[0]
        vp = next((w for w in d1[1:] if not (adj[v] >> w) & 1), None)
        if vp is not None:
            return ("P6b", attach_with_z(G, n, adj, Kl, [[v], [vp]],
                                         need, ctx))
        vp = d1[1]                      # adjacent pair
        return ("P6b", attach_with_z(G, n, adj, Kl, [[v, vp]], need, ctx))
    return ("??", f"{ctx}: fell through case tree (q={q})")


def order_cycle(G, Kl):
    """Return the cycle's vertices in cyclic order."""
    Ks = set(Kl)
    start = Kl[0]
    order = [start]
    prev = None
    cur = start
    while len(order) < len(Kl):
        nxt = next(w for w in G.neighbors(cur)
                   if w in Ks and w != prev and w not in order[1:])
        order.append(nxt)
        prev, cur = cur, nxt
    return order


def geodesic(n, adj, dist, u, v):
    """Geodesic u -> v (smallest-index next hop; random when RNG set)."""
    path = [u]
    cur = u
    while cur != v:
        nb = adj[cur]
        cands = []
        while nb:
            b = nb & -nb
            nb ^= b
            w = b.bit_length() - 1
            if dist[w][v] == dist[cur][v] - 1:
                cands.append(w)
        cur = RNG.choice(cands) if RNG else min(cands)
        path.append(cur)
    return path


def attach_with_z(G, n, adj, Kl, F, need, ctx):
    """Choose z avoiding component attachments per the proof's recipe, favor
    z = a paired/extra attachment when a component has 2 K-edges."""
    km = 0
    for v in Kl:
        km |= 1 << v
    # collect per-component K-attachments
    catts = []
    for comp in F:
        atts = []
        for t in comp:
            nb = adj[t] & km
            while nb:
                b = nb & -nb
                nb ^= b
                atts.append(b.bit_length() - 1)
        catts.append(atts)
    # if some component has 2 attachments, z must be one of them (and the
    # other components must not attach at z); try all z in K
    for z in Kl:
        ok = True
        for atts in catts:
            if sum(1 for a in atts if a != z) != 1:
                ok = False
                break
        if ok:
            return check_cycle_cert(G, n, adj, Kl, z, F, need, ctx)
    return f"{ctx}: no admissible z for F={F} atts={catts}"


def main():
    global RNG
    if len(sys.argv) > 1 and sys.argv[1].startswith("--seed="):
        RNG = random.Random(int(sys.argv[1].split("=")[1]))
        print(f"randomized-choice mode, seed {sys.argv[1].split('=')[1]}")
    tasks = build_corpus()
    eq_raw = json.loads(EQ_JSON.read_text())["equality_cases"]
    tasks += [(f"eq[{c['first_seen_as']}]", c["g6"]) for c in eq_raw]
    print(f"corpus+eq: {len(tasks)}")
    counts = Counter()
    fails = []
    done = 0
    for name, g6s in tasks:
        done += 1
        if done % 2000 == 0:
            print(f"  {done}/{len(tasks)} fails={len(fails)}", flush=True)
        try:
            r = prove_one(name, g6s)
        except Exception as exc:
            fails.append(f"{name}[{g6s}]: EXC {exc!r}")
            counts["EXC"] += 1
            continue
        if r is None:
            continue
        tag, err = r
        counts[tag] += 1
        if err:
            fails.append(err)
    out = {"counts": dict(counts), "n_failures": len(fails),
           "randomized": RNG is not None,
           "failures": fails[:200]}
    dest = OUT if RNG is None else ROOT / (
        "constructive_validator_results_" + sys.argv[1][2:] + ".json")
    dest.write_text(json.dumps(out, indent=2))
    print("counts:", dict(counts))
    print("FAILURES:", len(fails))
    for x in fails[:25]:
        print("  ", x)


if __name__ == "__main__":
    main()
