#!/usr/bin/env python3
"""Verifier for Lemma Y (clash repair), testing the CONSTRUCTION of the proof.

Lemma Y (as in PROOF_142_C.md): G with girth g >= 5, K a shortest cycle,
S, R distinct vertices outside K with K-geodesic tails T_S, T_R (shortest
paths to K minus the K-endpoint).  Suppose the tails CLASH (share a vertex or
some edge joins them) and lambda_S = d(S,K) <= g - 2 (spine condition).
Then the construction

  j0 := max level of a T_R vertex involved in a clash pair
  v  := the T_R vertex at level j0
  if v in T_S (shared):        Y := T_S  u  { w in T_R : lev(w) >= j0 }
  else: v has a UNIQUE T_S-neighbor u (unique-partner claim);
                               Y := T_S  u  { w in T_R : lev(w) >= j0 }

yields Y inducing a tree, with exactly one edge into K - {z} for an explicit
z in K, and |Y| >= d(S,R) + 1.  Hence M(K) >= d(S,R) + 1.

This script rebuilds Y per the recipe on corpus graphs (g >= 5, n <= 12) for
ALL clashing tail pairs found (capped), and asserts every claim exactly:
  A1 unique-partner: v not shared and #partners >= 2  ==>  lambda_S >= g - 1
     (when lambda_S <= g-2 the partner is unique)
  A2 Y induces a tree (connected, edges = |Y| - 1)
  A3 the K-attachment: at most 2 attach vertices; if 2, they are distinct
     (C3/C4 argument) and z := kappa(v) leaves exactly one edge into K-{z};
     if 1, any other z works; exactly one edge counted WITH multiplicity
  A4 |Y| >= dist(S,R) + 1
  A5 M(K) >= dist(S,R) + 1 (via the certificate Y itself; A2+A3 imply it)

Exact integers throughout.  Any assertion failure = proof bug.
"""

from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "bridge_oracle"))

import bridge_oracle as bo  # noqa: E402
from invariants import dist_to_set, edges_in_mask  # noqa: E402
from lemma_e_tests import components_of_mask  # noqa: E402

TAILS_PER_VERTEX = 12
PAIR_CAP = 4000  # clash pairs tested per graph
GRAPH_CAP = 4000


def tails_of(n, adj, dist, kmask, v, cap):
    """K-geodesic tails from v as level-indexed vertex lists (level 1..lam)."""
    lev = [dist_to_set(dist, u, kmask) for u in range(n)]
    lam = lev[v]
    out = []
    stack = [(v, (v,))]
    while stack and len(out) < cap:
        x, path = stack.pop()
        if lev[x] == 1:
            out.append(tuple(reversed(path)))  # index i -> level i+1
            continue
        nb = adj[x]
        while nb:
            b = nb & -nb
            nb ^= b
            y = b.bit_length() - 1
            if not ((1 << y) & kmask) and lev[y] == lev[x] - 1:
                stack.append((y, path + (y,)))
    # sanity: each tail has exactly one vertex per level 1..lam
    for t in out:
        assert len(t) == lam
        for i, w in enumerate(t):
            assert lev[w] == i + 1
    return out


def check_pair(n, adj, dist, g, kmask, S, R, TS, TR, stats):
    """Run the Y construction for spine TS (from S), branch TR (from R)."""
    lamS, lamR = len(TS), len(TR)
    setS = set(TS)
    # clash pairs
    cp = []
    for b in TR:
        for a in TS:
            if a == b or (adj[a] >> b) & 1:
                cp.append((a, b))
    if not cp:
        return False
    levR = {w: i + 1 for i, w in enumerate(TR)}
    j0 = max(levR[b] for _, b in cp)
    v = TR[j0 - 1]
    shared = v in setS
    if not shared:
        partners = [a for a in TS if (adj[a] >> v) & 1]
        if len(partners) >= 2:
            # A1: only possible when lambda_S >= g - 1
            levs = sorted(TS.index(a) + 1 for a in partners)
            assert levs[-1] - levs[0] >= g - 2, ("A1 gap", levs, g)
            assert lamS >= g - 1, ("A1", lamS, g)
            stats["multi_partner"] += 1
            if lamS > g - 2:
                return False  # spine condition fails; lemma silent
            raise AssertionError("unique-partner violated under spine cond")
    if lamS > g - 2:
        stats["spine_skip"] += 1
        return False
    # build Y
    Y = list(TS) + [w for w in TR[j0 - 1:] if w not in setS]
    ymask = 0
    for w in Y:
        ymask |= 1 << w
    assert ymask.bit_count() == len(Y)
    # A2: induced tree
    ne = edges_in_mask(adj, ymask)
    comps = components_of_mask(adj, ymask)
    assert len(comps) == 1, ("A2 connected", S, R)
    assert ne == len(Y) - 1, ("A2 tree", S, R, ne, len(Y))
    # A3: attachments
    att = {}  # K-vertex -> number of edges from Y
    for w in Y:
        m = adj[w] & kmask
        while m:
            b = m & -m
            m ^= b
            att[b.bit_length() - 1] = att.get(b.bit_length() - 1, 0) + 1
    assert all(c == 1 for c in att.values()), ("A3 multiplicity", att)
    assert 1 <= len(att) <= 2, ("A3 count", att)
    if len(att) == 2:
        # z := kappa(v) (v is T_R's foot then; j0 == 1 non-shared)
        assert j0 == 1 and not shared, ("A3 two-attach shape", j0, shared)
        kv = adj[v] & kmask
        assert kv.bit_count() == 1
        z = kv.bit_length() - 1
        assert z in att and len([k for k in att if k != z]) == 1
    else:
        z = next(k for k in range(n) if ((1 << k) & kmask)
                 and k not in att)
    edges_into_base = sum(c for k, c in att.items() if k != z)
    assert edges_into_base == 1, ("A3 final", att, z)
    # A4
    assert len(Y) >= dist[S][R] + 1, ("A4", len(Y), dist[S][R])
    stats["checked"] += 1
    stats["max_gain"] = max(stats["max_gain"], len(Y) - dist[S][R] - 1)
    return True


def main():
    tasks = bo.build_corpus()
    stats = {"graphs": 0, "checked": 0, "multi_partner": 0,
             "spine_skip": 0, "max_gain": 0}
    for name, g6s in tasks:
        if stats["graphs"] >= GRAPH_CAP:
            break
        G = nx.from_graph6_bytes(g6s.encode("ascii"))
        n, adj = bo.nx_to_bitadj(G)
        if n < 5 or n > 12 or not bo.graph_connected(n, adj):
            continue
        g = bo.girth(n, adj)
        if g < 5:
            continue
        dist = bo.all_pairs_dist(n, adj)
        Ks = bo.shortest_cycles(G, g)[:4]
        used = False
        for K in Ks:
            kmask = 0
            for x in K:
                kmask |= 1 << x
            outside = [v for v in range(n) if not ((1 << v) & kmask)]
            tails = {v: tails_of(n, adj, dist, kmask, v, TAILS_PER_VERTEX)
                     for v in outside}
            pairs = 0
            for ii, S in enumerate(outside):
                for R in outside[ii + 1:]:
                    for TS in tails[S]:
                        for TR in tails[R]:
                            if pairs >= PAIR_CAP:
                                break
                            pairs += 1
                            # both orientations (spine S / spine R)
                            if check_pair(n, adj, dist, g, kmask,
                                          S, R, TS, TR, stats):
                                used = True
                            if check_pair(n, adj, dist, g, kmask,
                                          R, S, TR, TS, stats):
                                used = True
        if used:
            stats["graphs"] += 1
        if stats["graphs"] % 400 == 0 and used:
            print(f"  {stats}", flush=True)
    print("FINAL:", stats)
    print("All Lemma-Y construction assertions passed.")


if __name__ == "__main__":
    main()
