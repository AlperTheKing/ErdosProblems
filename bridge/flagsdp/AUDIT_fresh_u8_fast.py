#!/usr/bin/env python3
"""FRESH INDEPENDENT AUDIT of CLAIM 2:  d_mono(W_G) <= U_8(W_G), triangle-free G, n=6 and n=7.
EXACT integer arithmetic (everything scaled by SCALE = n^10 * 90 so weights are integers;
profile-graph MaxCut is exact integer). Compares U_8 vs d_mono as exact Fractions => no float error.

Independent of compute_U8.py: own d_mono, own WL-class brute canon8, own MaxCut.
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
    best = 0
    for mask in range(1 << (n - 1)):
        full = mask << 1
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
    return F(2 * (edges_count(n, A) - maxcut_int(n, A)), n * n)


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
            kk = []
            for a in range(n):
                oa = cur[a]
                for b in range(a + 1, n):
                    ob = cur[b]
                    kk.append(1 if (adj[oa] >> ob) & 1 else 0)
            kt = tuple(kk)
            if best is None or kt < best:
                best = kt
                p = [0] * n
                for pos, old in enumerate(cur):
                    p[old] = pos
                bestperm = p
            return
        for pr in itertools.permutations(groups[idx]):
            gen(idx + 1, cur + list(pr))

    gen(0, [])
    return best, bestperm


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


def maxcut_profile_int(nodes, edges):
    """integer-weighted MaxCut, brute over 2-colorings of nodes."""
    nn = len(nodes)
    if nn == 0:
        return 0
    idx = {v: i for i, v in enumerate(nodes)}
    el = [(idx[a], idx[b], w) for (a, b), w in edges.items()]
    best = 0
    for mask in range(1 << (nn - 1)):
        c = 0
        for a, b, w in el:
            if ((mask >> a) & 1) != ((mask >> b) & 1):
                c += w
        if c > best:
            best = c
    return best


def U8_exact(n_parts, Tadj):
    """Return U_8 as exact Fraction. Internal weights scaled to integers by SCALE = n^10 * 90."""
    SCALE = (n_parts ** 10) * 90  # multinomial * 90/n^10 -> integer after * SCALE
    # weight of a count-vector contributing to one (R,A,B): multinomial(10;counts) * (1/n)^10 / 90
    # * SCALE = multinomial(10;counts) * 1  (since (1/n)^10 * SCALE / 90 ... wait recompute)
    # raw weight per (J,edge) accumulation = wt/90 where wt = multinomial * (1/n)^10
    # scaled integer = wt/90 * SCALE = multinomial * (1/n)^10 / 90 * n^10 * 90 = multinomial.
    W = {}  # key -> {(A,B): int_weight}
    for counts in comps(10, n_parts):
        mult = factorial(10)
        for c in counts:
            mult //= factorial(c)
        if mult == 0:
            continue
        nn, A = blowup(counts, Tadj)
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
                    key, perm = canon8_memo(Radj)
                    Aset = frozenset(perm[idx[v]] for v in anch if (A[i] >> v) & 1)
                    Bset = frozenset(perm[idx[v]] for v in anch if (A[j] >> v) & 1)
                    d = W.setdefault(key, {})
                    d[(Aset, Bset)] = d.get((Aset, Bset), 0) + mult  # integer (=wt/90*SCALE)
    total_scaled = 0
    for key, ed in W.items():
        offdiag = {}
        sl = 0
        profiles = set()
        for (Aset, Bset), w in ed.items():
            profiles.add(Aset)
            profiles.add(Bset)
            if Aset == Bset:
                sl += w
            else:
                a, b = tuple(sorted([Aset, Bset], key=lambda s: (len(s), sorted(s))))
                offdiag[(a, b)] = offdiag.get((a, b), 0) + w
        mc = maxcut_profile_int(list(profiles), offdiag) if offdiag else 0
        total_scaled += sl + (sum(offdiag.values()) - mc)
    return F(total_scaled, SCALE)


def main():
    print("FRESH EXACT AUDIT: d_mono <= U_8 for ALL triangle-free graphs n=6 and n=7", flush=True)
    import time
    worst_slack = None
    worst_graph = None
    count = 0
    viol = 0
    for n in [6, 7]:
        graphs = fe.enumerate_graphs(n, triangle_free=True)
        print(f"\n--- n={n}: {len(graphs)} triangle-free graphs ---", flush=True)
        t0 = time.time()
        for gi, (nn, A) in enumerate(graphs):
            assert fe.is_triangle_free(nn, A)
            dm = d_mono(nn, A)
            u8 = U8_exact(nn, A)
            slack = u8 - dm
            count += 1
            if slack < 0:
                viol += 1
                print(f"  !!! VIOLATION g#{gi} e={edges_count(nn,A)} d_mono={dm}={float(dm):.6f} U_8={u8}={float(u8):.6f} slack={float(slack):.3e} adj={A}", flush=True)
            if worst_slack is None or slack < worst_slack:
                worst_slack = slack
                worst_graph = (n, list(A), dm, u8)
            if (gi + 1) % 10 == 0:
                print(f"    ...{gi+1}/{len(graphs)} done [{time.time()-t0:.0f}s] worst_slack={float(worst_slack):.3e}", flush=True)
        print(f"  n={n} complete [{time.time()-t0:.0f}s]", flush=True)
    print("\n==================== SUMMARY ====================", flush=True)
    print(f"graphs checked = {count}", flush=True)
    print(f"violations (U_8 < d_mono) = {viol}", flush=True)
    print(f"worst slack (min U_8 - d_mono) exact = {worst_slack} = {float(worst_slack):.6e}", flush=True)
    g = worst_graph
    print(f"worst graph: n={g[0]} d_mono={float(g[2]):.6f} U_8={float(g[3]):.6f} adj={g[1]}", flush=True)
    print(f"\nCLAIM 2 (d_mono <= U_8) on n=6,7: {'CONFIRMED' if viol==0 else 'REFUTED'}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
