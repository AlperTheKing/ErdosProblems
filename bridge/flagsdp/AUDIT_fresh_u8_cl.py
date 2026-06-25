#!/usr/bin/env python3
"""Fresh exact audit using compute_U8.canon_label (fast) for R-canonicalization, but OWN d_mono,
OWN maxcut, OWN integer-exact U_8 accumulation. Cross-validated against AUDIT_fresh_u8_fast.canon8.
Enumerates ALL triangle-free graphs on n=6 and n=7; checks d_mono <= U_8 exactly.
"""
import itertools, time
from math import factorial
from fractions import Fraction as F
import flag_engine as fe
from compute_U8 import canon_label


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
            au = A[u]; su = (full >> u) & 1
            w = au >> (u + 1); v = u + 1
            while w:
                if (w & 1) and (((full >> v) & 1) != su):
                    c += 1
                w >>= 1; v += 1
        if c > best:
            best = c
    return best


def d_mono(n, A):
    return F(2 * (edges_count(n, A) - maxcut_int(n, A)), n * n)


def blowup(counts, Tadj):
    parts = []
    for p, c in enumerate(counts):
        parts += [p] * c
    n = len(parts); A = [0] * n
    for u in range(n):
        for w in range(u + 1, n):
            if parts[u] != parts[w] and (Tadj[parts[u]] >> parts[w]) & 1:
                A[u] |= 1 << w; A[w] |= 1 << u
    return n, A


def comps(total, parts):
    if parts == 1:
        yield (total,); return
    for f in range(total + 1):
        for rest in comps(total - f, parts - 1):
            yield (f,) + rest


def maxcut_profile_int(nodes, edges):
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


_cm = {}
def canon_memo(Radj):
    rk = tuple(Radj); v = _cm.get(rk)
    if v is None:
        v = canon_label(8, Radj); _cm[rk] = v
    return v


def U8_exact(n_parts, Tadj):
    SCALE = (n_parts ** 10) * 90
    W = {}
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
                                Radj[p] |= 1 << q; Radj[q] |= 1 << p
                    key, inv = canon_memo(Radj)  # inv[oldpos]=canonpos
                    Aset = frozenset(inv[idx[v]] for v in anch if (A[i] >> v) & 1)
                    Bset = frozenset(inv[idx[v]] for v in anch if (A[j] >> v) & 1)
                    d = W.setdefault(key, {})
                    d[(Aset, Bset)] = d.get((Aset, Bset), 0) + mult
    total = 0
    for key, ed in W.items():
        offdiag = {}; sl = 0; profiles = set()
        for (Aset, Bset), w in ed.items():
            profiles.add(Aset); profiles.add(Bset)
            if Aset == Bset:
                sl += w
            else:
                a, b = tuple(sorted([Aset, Bset], key=lambda s: (len(s), sorted(s))))
                offdiag[(a, b)] = offdiag.get((a, b), 0) + w
        mc = maxcut_profile_int(list(profiles), offdiag) if offdiag else 0
        total += sl + (sum(offdiag.values()) - mc)
    return F(total, SCALE)


def main():
    print("FRESH EXACT AUDIT (canon_label): d_mono <= U_8, all triangle-free n=6,7", flush=True)
    worst = None; wg = None; count = 0; viol = 0
    viol_list = []
    for n in [6, 7]:
        graphs = fe.enumerate_graphs(n, triangle_free=True)
        print(f"\n--- n={n}: {len(graphs)} graphs ---", flush=True)
        t0 = time.time()
        for gi, (nn, A) in enumerate(graphs):
            assert fe.is_triangle_free(nn, A)
            dm = d_mono(nn, A); u8 = U8_exact(nn, A); slack = u8 - dm
            count += 1
            if slack < 0:
                viol += 1; viol_list.append((n, list(A), dm, u8))
                print(f"  !!! VIOLATION g#{gi} e={edges_count(nn,A)} d_mono={dm} U_8={u8} slack={float(slack):.3e} adj={A}", flush=True)
            if worst is None or slack < worst:
                worst = slack; wg = (n, list(A), dm, u8)
            if (gi + 1) % 20 == 0:
                print(f"    ...{gi+1}/{len(graphs)} [{time.time()-t0:.0f}s] worst={float(worst):.3e}", flush=True)
        print(f"  n={n} done [{time.time()-t0:.0f}s]", flush=True)
    print("\n========== SUMMARY ==========", flush=True)
    print(f"graphs checked = {count}", flush=True)
    print(f"violations = {viol}", flush=True)
    print(f"worst slack (min U_8 - d_mono) = {worst} = {float(worst):.6e}", flush=True)
    print(f"worst graph: n={wg[0]} d_mono={float(wg[2]):.6f} U_8={float(wg[3]):.6f} adj={wg[1]}", flush=True)
    print(f"\nCLAIM 2 on n=6,7: {'CONFIRMED' if viol==0 else 'REFUTED'}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
