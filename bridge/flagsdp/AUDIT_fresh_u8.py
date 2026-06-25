#!/usr/bin/env python3
"""FRESH INDEPENDENT AUDIT of CLAIM 2:  d_mono(W_G) <= U_8(W_G) for triangle-free G.

Written from scratch (own d_mono, own U_8) to cross-check validate_dmono_le_u8.py.
Enumerates ALL triangle-free graphs on n=6 and n=7 and checks d_mono <= U_8 for each.

Definitions (matching the claim / validate_dmono_le_u8.py):
  d_mono(W_G) = 2 (e - maxcut(G)) / n^2      [edge-density minus max-cut-density, normalized by n^2]
  W_G = blow-up graphon (10 i.i.d. samples from n parts, each part weight 1/n)
  U_8(W_G): for each count-vector of how the 10 samples land in the n parts, with multinomial weight,
            build the order-10 blow-up graph; for every ordered EDGE (i,j) the other 8 vertices are anchors,
            R = canonical induced graph on anchors, A=profile(i) wrt anchors, B=profile(j) wrt anchors;
            accumulate w_R(A,B) += weight/90  (90 = 10*9 ordered pairs).
            Per canonical R: profile graph, MaxCut over 2-colorings of profile nodes; self-loops (A==B) always mono.
            min_mono_R = selfloop_R + (offdiag_total_R - MaxCut_R);  U_8 = sum_R min_mono_R.

EVERYTHING here is reimplemented independently; canonical labeling of R uses brute n!=8! permutations
within nauty-free code (own canon, NOT compute_U8.canon_label) so a bug in canon_label cannot hide here.
"""
import itertools
from math import factorial
from fractions import Fraction as F
import flag_engine as fe


def popc(x):
    return bin(x).count("1")


def edges_count(n, A):
    return sum(popc(A[v]) for v in range(n)) // 2


def maxcut_int(n, A):
    """Exact integer max-cut by brute over 2^(n-1) bipartitions (fix vertex 0 in side 0)."""
    best = 0
    for mask in range(1 << (n - 1)):
        full = mask << 1  # vertex0 -> side 0
        c = 0
        for u in range(n):
            au = A[u]
            su = (full >> u) & 1
            w = au >> (u + 1)
            v = u + 1
            while w:
                if (w & 1) and (((full >> v) & 1) != su):
                    c += 1
                w >>= 1
                v += 1
        if c > best:
            best = c
    return best


def d_mono(n, A):
    e = edges_count(n, A)
    mc = maxcut_int(n, A)
    return F(2 * (e - mc), n * n)


# ---- independent canonical form for an 8-vertex graph ----
# WL color refinement to break vertices into color classes, then brute over
# permutations WITHIN color classes only (lex-min upper-tri). Independent of compute_U8.
def _refine_colors(n, adj):
    col = [popc(adj[v]) for v in range(n)]
    for _ in range(n + 2):
        sig = [(col[v], tuple(sorted(col[u] for u in range(n) if (adj[v] >> u) & 1)))
               for v in range(n)]
        ren = {s: i for i, s in enumerate(sorted(set(sig)))}
        newcol = [ren[s] for s in sig]
        if newcol == col:
            break
        col = newcol
    return col


def canon8(adj):
    """Return (canon_key, perm) with perm[old]=new_position; canon_key=lexmin upper-tri tuple.
    Brute only over permutations within WL color classes (sound: any iso preserves WL color).
    """
    n = 8
    col = _refine_colors(n, adj)
    order0 = sorted(range(n), key=lambda v: col[v])
    groups = []
    i = 0
    while i < n:
        j = i
        while j < n and col[order0[j]] == col[order0[i]]:
            j += 1
        groups.append(order0[i:j])
        i = j
    best = None
    bestperm = None

    def gen(idx, cur):
        nonlocal best, bestperm
        if idx == len(groups):
            # cur = ordering of OLD vertices into new positions 0..n-1
            kk = []
            for a in range(n):
                oa = cur[a]
                for b in range(a + 1, n):
                    ob = cur[b]
                    kk.append(1 if (adj[oa] >> ob) & 1 else 0)
            kt = tuple(kk)
            if best is None or kt < best:
                best = kt
                # perm[old]=newpos
                p = [0] * n
                for pos, old in enumerate(cur):
                    p[old] = pos
                bestperm = p
            return
        for pr in itertools.permutations(groups[idx]):
            gen(idx + 1, cur + list(pr))

    gen(0, [])
    return best, bestperm


# memoize canon by raw adjacency tuple
_canon_memo = {}


def canon8_memo(adj):
    rk = tuple(adj)
    v = _canon_memo.get(rk)
    if v is None:
        v = canon8(adj)
        _canon_memo[rk] = v
    return v


def blowup(counts, Tadj):
    parts = []
    for p, c in enumerate(counts):
        parts += [p] * c
    n = len(parts)
    A = [0] * n
    for u in range(n):
        for w in range(u + 1, n):
            if parts[u] != parts[w] and (Tadj[parts[u]] >> parts[w]) & 1:
                A[u] |= 1 << w
                A[w] |= 1 << u
    return n, A


def comps(total, parts):
    if parts == 1:
        yield (total,)
        return
    for f in range(total + 1):
        for rest in comps(total - f, parts - 1):
            yield (f,) + rest


def maxcut_profile(nodes, edges):
    """edges: dict {(a,b): w} a<b. brute MaxCut over 2-colorings of nodes (Fractions)."""
    nn = len(nodes)
    if nn == 0:
        return F(0)
    idx = {v: i for i, v in enumerate(nodes)}
    el = [(idx[a], idx[b], w) for (a, b), w in edges.items()]
    best = F(0)
    for mask in range(1 << (nn - 1)):
        c = F(0)
        for a, b, w in el:
            if ((mask >> a) & 1) != ((mask >> b) & 1):
                c += w
        if c > best:
            best = c
    return best


def U8(n_parts, Tadj):
    """U_8 of the uniform blow-up graphon of (n_parts, Tadj). Exact via Fractions."""
    alpha = F(1, n_parts)
    W = {}  # canon_key -> {(Aset,Bset): weight}
    for counts in comps(10, n_parts):
        # multinomial(10; counts) * alpha^10
        w = factorial(10)
        for c in counts:
            w //= factorial(c)
        wt = w * (alpha ** 10)
        if wt == 0:
            continue
        nn, A = blowup(counts, Tadj)  # nn==10
        for i in range(10):
            Ai = A[i]
            for j in range(10):
                if i != j and (Ai >> j) & 1:
                    anch = [v for v in range(10) if v != i and v != j]
                    idx = {v: p for p, v in enumerate(anch)}
                    Radj = [0] * 8
                    for p in range(8):
                        for q in range(p + 1, 8):
                            if (A[anch[p]] >> anch[q]) & 1:
                                Radj[p] |= 1 << q
                                Radj[q] |= 1 << p
                    key, perm = canon8_memo(Radj)  # perm[oldpos]=newpos
                    Aset = frozenset(perm[idx[v]] for v in anch if (A[i] >> v) & 1)
                    Bset = frozenset(perm[idx[v]] for v in anch if (A[j] >> v) & 1)
                    d = W.setdefault(key, {})
                    d[(Aset, Bset)] = d.get((Aset, Bset), F(0)) + wt / 90
    total = F(0)
    for key, ed in W.items():
        offdiag = {}
        sl = F(0)
        profiles = set()
        for (Aset, Bset), w in ed.items():
            profiles.add(Aset)
            profiles.add(Bset)
            if Aset == Bset:
                sl += w
            else:
                a, b = tuple(sorted([Aset, Bset], key=lambda s: (len(s), sorted(s))))
                offdiag[(a, b)] = offdiag.get((a, b), F(0)) + w
        mc = maxcut_profile(list(profiles), offdiag) if offdiag else F(0)
        total += sl + (sum(offdiag.values(), F(0)) - mc)
    return total


def main():
    print("FRESH AUDIT: d_mono <= U_8 for ALL triangle-free graphs on n=6, n=7", flush=True)
    worst_slack = None
    worst_graph = None
    count = 0
    viol = 0
    for n in [6, 7]:
        graphs = fe.enumerate_graphs(n, triangle_free=True)
        print(f"\n--- n={n}: {len(graphs)} triangle-free graphs ---", flush=True)
        for (nn, A) in graphs:
            # sanity: triangle-free
            assert fe.is_triangle_free(nn, A), "geng emitted a triangle!"
            dm = d_mono(nn, A)
            u8 = U8(nn, A)
            slack = u8 - dm  # want >= 0
            count += 1
            if slack < 0:
                viol += 1
                print(f"  !!! VIOLATION  e={edges_count(nn,A)} d_mono={float(dm):.6f} U_8={float(u8):.6f} slack={float(slack):.3e}", flush=True)
                print(f"      adjacency={A}", flush=True)
            if worst_slack is None or slack < worst_slack:
                worst_slack = slack
                worst_graph = (n, A, dm, u8)
        print(f"  done n={n}; cumulative worst slack so far = {float(worst_slack):.6e}", flush=True)
    print("\n==================== SUMMARY ====================", flush=True)
    print(f"graphs checked = {count}", flush=True)
    print(f"violations (U_8 < d_mono) = {viol}", flush=True)
    print(f"worst slack (min over all of U_8 - d_mono) = {worst_slack}  = {float(worst_slack):.6e}", flush=True)
    g = worst_graph
    print(f"worst graph: n={g[0]} d_mono={float(g[2]):.6f} U_8={float(g[3]):.6f} adj={g[1]}", flush=True)
    print(f"\nCLAIM 2 (d_mono <= U_8) for n=6,7: {'CONFIRMED' if viol==0 else 'REFUTED'}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
