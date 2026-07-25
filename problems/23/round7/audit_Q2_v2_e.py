"""audit_Q2_v2_e.py -- AUDIT pass 2, block E: exact VERTEX-LEVEL dissection of the
specific configurations Q2.md reports as ceilings, plus the auditor's new N=45
STAR witness that Q2.md records as '0'.
"""
import sys
from fractions import Fraction as F
from itertools import combinations
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q2_v2_core import (g6, pc, edges, is_trianglefree, mono, maxcut_bip,
                              sigma, delta_recompute, indep_sets)
import random
random.seed(11)
HR = "=" * 78


def blowup_col(pg6, a, col):
    n, pa = g6(pg6)
    assert n == len(a) == len(col)
    cls, V = [], 0
    for i in range(n):
        cls.append(list(range(V, V + a[i]))); V += a[i]
    adj = [0] * V
    for i in range(n):
        for j in range(n):
            if (pa[i] >> j) & 1:
                for x in cls[i]:
                    for y in cls[j]:
                        adj[x] |= 1 << y
    Y = 0
    for i in range(n):
        if col[i]:
            for x in cls[i]:
                Y |= 1 << x
    return V, adj, Y, cls, pa


def report(tag, pg6, a, col):
    V, adj, Y, cls, pa = blowup_col(pg6, a, col)
    M = mono(V, adj, Y)
    sg = sigma(V, adj, Y)
    E = len(edges(V, adj))
    print(f"  {tag}: H={pg6} a={a} col={col}  N={V} |E|={E} |M|={M}  "
          f"25|M|/N^2 = {F(25*M, V*V)} = {float(F(25*M,V*V)):.6f}  tri-free={is_trianglefree(V,adj)}")
    print(f"      sigma per part = {[sg[c[0]] if c else None for c in cls]}   sigma>=0 : {all(s>=0 for s in sg)}")
    # switch-star at vertex level with slack
    slacks = []
    for c in cls:
        if not c:
            slacks.append(None); continue
        v = c[0]
        yv = (Y >> v) & 1
        NB = adj[v] & (Y if not yv else ~Y) & ((1 << V) - 1)
        rhs = 0
        j = NB
        while j:
            b = j & -j; k = b.bit_length() - 1; j ^= b
            if 2 - sg[k] > 0:
                rhs += 2 - sg[k]
        slacks.append(sg[v] - rhs)
    print(f"      switch-star slacks per part = {slacks}   all >= 0 : {all(s is None or s>=0 for s in slacks)}")
    # family (*) at the PART level (corner argument, multilinearity verified in block A)
    h = len(a)
    parts = list(range(h))
    nb = [sum(1 << j for j in range(h) if (pa[i] >> j) & 1) for i in range(h)]
    worst = None
    for i in parts:
        if a[i] == 0:
            continue
        for T in range(1 << h):
            if T & nb[i]:
                continue
            ok = True
            for x in range(h):
                if not (T >> x) & 1:
                    continue
                for y in range(x + 1, h):
                    if (T >> y) & 1 and (pa[x] >> y) & 1:
                        ok = False
            if not ok:
                continue
            S = 0
            for k in range(h):
                if ((nb[i] | T) >> k) & 1:
                    for x in cls[k]:
                        S |= 1 << x
            if S == 0 or S == (1 << V) - 1:
                continue
            d = delta_recompute(V, adj, Y, S)
            if worst is None or d > worst[0]:
                worst = (d, bin(nb[i] | T), i)
    print(f"      family (*) max Delta (part level) = {worst[0]}   "
          f"{'SATISFIED' if worst[0] <= 0 else 'VIOLATED'}")
    # random VERTEX-level independent T cross-check
    bad = 0
    for _ in range(3000):
        v = random.randrange(V)
        Nv = adj[v]
        T = 0
        cand = [x for x in range(V) if not (Nv >> x) & 1]
        random.shuffle(cand)
        for x in cand:
            if adj[x] & T == 0:
                T |= 1 << x
        if delta_recompute(V, adj, Y, Nv | T) > 0:
            bad += 1
    print(f"      3000 random vertex-level (*) instances: violations = {bad}")
    # min improving switch at the part-count level (multilinear -> counts suffice)
    sigp = [sg[c[0]] if c else 0 for c in cls]
    coef = [[0] * h for _ in range(h)]
    for i in range(h):
        for j in range(i + 1, h):
            if (pa[i] >> j) & 1:
                coef[i][j] = -2 if col[i] == col[j] else 2

    def dcount(s):
        d = -sum(s[i] * sigp[i] for i in range(h))
        for i in range(h):
            for j in range(i + 1, h):
                if coef[i][j]:
                    d += coef[i][j] * s[i] * s[j]
        return d
    best = None
    k = 1
    while best is None and k <= V:
        def rec(i, rem, cur):
            nonlocal best
            if best is not None:
                return
            if i == h - 1:
                if rem <= a[i]:
                    s = cur + [rem]
                    if dcount(s) > 0:
                        best = (k, tuple(s), dcount(s))
                return
            lo = max(0, rem - sum(a[i + 1:]))
            for x in range(lo, min(a[i], rem) + 1):
                rec(i + 1, rem - x, cur + [x])
                if best is not None:
                    return
        rec(0, k, [])
        k += 1
    print(f"      min improving switch |S| = {best[0]} = {F(best[0], V)}N = {float(F(best[0],V)):.4f}N "
          f"at counts {best[1]} (Delta={best[2]})")
    return M, V


print(HR)
print("E1  the NEW N=45 STAR configuration found by the auditor (Q2.md records STAR=0 at N=45)")
print(HR)
report("N=45 STAR", "ECxo", [7, 2, 5, 7, 12, 12], [0, 1, 0, 1, 1, 0])

print()
print(HR)
print("E2  Q2.md's own STAR ceiling witnesses at N=24 and N=36 (claimed 25/24)")
print(HR)
report("N=24 STAR", "ECxo", [4, 1, 3, 4, 6, 6], [0, 1, 0, 1, 1, 0])
report("N=36 STAR", "ECxo", [6, 1, 5, 6, 9, 9], [0, 1, 0, 1, 1, 0])

print()
print(HR)
print("E3  Q2.md R4: the 6-part LOC champion EEj_ at a=(14,4,12,4,12,14), N=60")
print(HR)
n6, adj6 = g6("EEj_")
print("   EEj_ decoded: edges =", [(i, j) for i in range(n6) for j in range(i + 1, n6) if (adj6[i] >> j) & 1])
print("   Q2.md says: parts {0,1,2}|{3,4,5}, edges 03,04,05,13,15,24,25 (bipartite)")
bip6 = maxcut_bip(n6, adj6)
print(f"   bip(EEj_) = {bip6}  (bipartite iff 0)")
for (a, col) in [([14, 4, 12, 4, 12, 14], [0, 1, 1, 1, 1, 0]),
                 ([11, 4, 9, 4, 9, 11], [0, 1, 1, 1, 1, 0]),
                 ([8, 4, 6, 4, 6, 8], [0, 1, 1, 1, 1, 0])]:
    M, V = report(f"EEj_ N={sum(a)}", "EEj_", a, col)
    print(f"      |M|/N^2 = {F(M, V*V)} ~ 1/{float(V*V)/M:.3f}   (Q2.md: 89/900 ~ 1/10.11 at N=60)")

print()
print(HR)
print("E4  is the ECxo family a C5 blow-up? (Q2.md says the witness 'is' C5[2u,2u,3u,2u,3u])")
print(HR)
n5, adj5 = g6("ECxo")
print("   ECxo edges =", [(i, j) for i in range(n5) for j in range(i + 1, n5) if (adj5[i] >> j) & 1])
tw = {}
for v in range(n5):
    tw.setdefault(adj5[v], []).append(v)
print("   twin classes =", list(tw.values()))
print("   #edges =", len(edges(n5, adj5)), " (C5-with-one-class-doubled would have 7)")
print("   bip(ECxo) =", maxcut_bip(n5, adj5), "(0 => bipartite => NOT a C5 blow-up)")
