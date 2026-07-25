"""H4 constructive lower-bound search at N = 15..19.

Two exact generators of candidate graphs, both with EXHAUSTIVE 2^(N-1) maxcut:

  (A) blow-up + attachment: take any C5 blow-up on N-k vertices and attach k new
      vertices, each to an arbitrary independent set of the current graph
      (independent sets of a C5 blow-up are exactly the subsets of V_i u V_{i+2});
  (B) exhaustive one-vertex extension of any given seed graph: for EVERY
      independent set S of the seed, form seed+v with N(v)=S and evaluate bip.
      Repeated to depth d.  Complete for the "seed + d vertices" family.

Usage:  python h4_construct.py [--seeds g6,...] [--n N] [--depth d]
"""

import sys
import argparse
from itertools import combinations

from h4_lib import (g6_encode, g6_decode, bip, num_edges, is_triangle_free,
                    is_maximal_triangle_free, maxcut_exact)


def c5_blowup(parts):
    n = sum(parts)
    off, s = [], 0
    for p in parts:
        off.append(s)
        s += p
    adj = [0] * n
    for i in range(5):
        j = (i + 1) % 5
        for a in range(off[i], off[i] + parts[i]):
            for b in range(off[j], off[j] + parts[j]):
                adj[a] |= 1 << b
                adj[b] |= 1 << a
    return n, adj


def independent_sets(n, adj, maxsize=None):
    """all independent sets (as bitmasks), by simple DFS with pruning."""
    out = []

    def rec(v, cur, allowed):
        out.append(cur)
        u = v
        while u < n:
            if (allowed >> u) & 1:
                rec(u + 1, cur | (1 << u), allowed & ~adj[u] & ~((1 << (u + 1)) - 1))
            u += 1

    rec(0, 0, (1 << n) - 1)
    return out


def add_vertex(n, adj, S):
    adj2 = list(adj) + [S]
    for u in range(n):
        if (S >> u) & 1:
            adj2[u] |= 1 << n
    return n + 1, adj2


def maximalise(n, adj, order=None):
    """greedily add every addable edge (result is maximal triangle-free)."""
    adj = list(adj)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    if order is not None:
        pairs = [pairs[k] for k in order]
    changed = True
    while changed:
        changed = False
        for (i, j) in pairs:
            if (adj[i] >> j) & 1:
                continue
            if adj[i] & adj[j]:
                continue
            adj[i] |= 1 << j
            adj[j] |= 1 << i
            changed = True
    return adj


def extend_best(n, adj, target_n, keep=200, verbose=True):
    """breadth-first exhaustive one-vertex extension up to target_n, keeping the
    `keep` best (by bip) canonical-ish representatives at each level."""
    import hashlib
    level = [(bip(n, adj), n, tuple(adj))]
    while level[0][1] < target_n:
        nxt = {}
        for (b0, nn, aa) in level:
            aa = list(aa)
            for S in independent_sets(nn, aa):
                n2, a2 = add_vertex(nn, aa, S)
                a2 = maximalise(n2, a2)
                key = g6_encode(n2, a2)
                if key in nxt:
                    continue
                nxt[key] = (bip(n2, a2), n2, tuple(a2))
        level = sorted(nxt.values(), key=lambda z: -z[0])[:keep]
        if verbose:
            print(f"  level n={level[0][1]}: {len(nxt)} distinct, best bip={level[0][0]}",
                  flush=True)
    return level


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=16)
    ap.add_argument("--keep", type=int, default=400)
    ap.add_argument("--seeds", type=str, default="")
    args = ap.parse_args()

    seeds = []
    if args.seeds:
        for s in args.seeds.split(","):
            if s.strip():
                seeds.append(g6_decode(s.strip()))
    else:
        # every C5 blow-up with 10..15 vertices, plus the known census extremals
        for p1 in range(1, 5):
            for p2 in range(1, 5):
                for p3 in range(1, 5):
                    for p4 in range(1, 5):
                        for p5 in range(1, 5):
                            tot = p1 + p2 + p3 + p4 + p5
                            if 10 <= tot <= args.target:
                                seeds.append(c5_blowup([p1, p2, p3, p4, p5]))
        for g in ("K?ABBBwerwBw", "K?BD@g]Qvo^?", "L??ED@_~?~^_Fw",
                  "M?AE@bH{AYN_LgBs?", "LsaBb@KQ@`aiBq", "Ms`rQo`GOdASBKBF?"):
            seeds.append(g6_decode(g))

    # dedupe seeds by graph6 of maximalised form
    seen, uniq = set(), []
    for (n, adj) in seeds:
        if n > args.target:
            continue
        a = maximalise(n, adj)
        k = g6_encode(n, a)
        if k in seen:
            continue
        seen.add(k)
        uniq.append((n, a))
    print(f"[seeds] {len(uniq)} maximalised seeds, sizes "
          f"{sorted(set(n for n, _ in uniq))}", flush=True)

    best = (-1, None)
    pool = {}
    for (n, adj) in uniq:
        pool.setdefault(n, []).append((bip(n, adj), n, tuple(adj)))

    for nn in sorted(pool):
        lvl = sorted(pool[nn], key=lambda z: -z[0])[:args.keep]
        print(f"[start n={nn}] best seed bip={lvl[0][0]}", flush=True)
        res = extend_best(nn, list(lvl[0][2]), args.target, keep=args.keep) if False else None
        # extend the whole level, not just one
        level = lvl
        while level[0][1] < args.target:
            nxt = {}
            for (b0, k, aa) in level:
                aa = list(aa)
                for S in independent_sets(k, aa):
                    n2, a2 = add_vertex(k, aa, S)
                    a2 = maximalise(n2, a2)
                    key = g6_encode(n2, a2)
                    if key not in nxt:
                        nxt[key] = (bip(n2, a2), n2, tuple(a2))
            level = sorted(nxt.values(), key=lambda z: -z[0])[:args.keep]
            print(f"   n={level[0][1]}: {len(nxt)} distinct, best bip={level[0][0]}", flush=True)
        if level[0][0] > best[0]:
            best = (level[0][0], list(level[0][2]))

    b, adj = best
    n = args.target
    m = num_edges(n, adj)
    mc, _ = maxcut_exact(n, adj)
    print(f"\nBEST at N={n}: bip={b} (recheck {m}-{mc}={m-mc}) "
          f"tf={is_triangle_free(n, adj)} maximal={is_maximal_triangle_free(n, adj)}")
    print(f"  g6={g6_encode(n, adj)}")
    print(f"  25*bip={25*b} vs N^2={n*n}  "
          f"{'*** VIOLATION ***' if 25*b > n*n else 'consistent'}")


if __name__ == "__main__":
    sys.exit(main())
