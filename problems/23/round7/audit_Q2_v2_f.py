"""audit_Q2_v2_f.py -- AUDIT pass 2, block F:
  F1  the MANDATED round5 ten-witness regression, run against the Q2 mechanism
      (LOC / STAR / ALL ceilings on each witness) + exact tightness on C5[n]
  F2  Fact 2.1 (radius-2 transport on C5[n]) and Fact 2.2 ((*) tight on C5[n])
  F3  Q2.md section 3: is X = A1 u A4 really the UNIQUE locally-maximal
      non-optimal part-cut of W_b?
"""
import sys
from fractions import Fraction as F
from itertools import combinations
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round5")
from audit_Q2_v2_core import (pc, edges, is_trianglefree, mono, maxcut_bip, sigma,
                              delta_recompute, indep_sets)
from claude_witness_regression import WITNESSES, gamma

HR = "=" * 78
print(HR)
print("F1  MANDATED regression: the ten round5 witnesses, exact, through the Q2 mechanism")
print(HR)
print("   For each witness the graph is Gamma_m restricted to the support of the")
print("   weight vector; every part-respecting cut is enumerated exactly.")
print("   bip/N^2 must be <= 1/25 ; LOC/STAR = best 25|M|/N^2 a cut passing that family reaches.")
print()
print(f"   {'witness':28s} {'m':>3s} {'h':>3s} {'N':>4s}  {'25*bip/N^2':>12s}  {'25M/N^2 LOC':>14s}  "
      f"{'25M/N^2 STAR':>14s}  {'ALL':>6s}")


def analyse_pattern(adjmat, w):
    """adjmat: h x h 0/1; w: integer weights (>=0).  Exact ceilings over all
    part-respecting cuts."""
    h = len(w)
    idx = [i for i in range(h) if w[i] > 0]
    hh = len(idx)
    A = [[adjmat[idx[i]][idx[j]] for j in range(hh)] for i in range(hh)]
    a = [w[i] for i in idx]
    N = sum(a)
    nb = [sum(1 << j for j in range(hh) if A[i][j]) for i in range(hh)]
    indep = []
    for m in range(1 << hh):
        ok = True
        for i in range(hh):
            if not (m >> i) & 1:
                continue
            for j in range(i + 1, hh):
                if (m >> j) & 1 and A[i][j]:
                    ok = False
        if ok:
            indep.append(m)
    bestbip = None
    locbest = starbest = allbest = None
    for cm in range(1 << (hh - 1)):
        col = [0] * hh
        for i in range(1, hh):
            col[i] = (cm >> (i - 1)) & 1
        M = sum(a[i] * a[j] for i in range(hh) for j in range(i + 1, hh)
                if A[i][j] and col[i] == col[j])
        if bestbip is None or M < bestbip:
            bestbip = M
        sg = []
        for i in range(hh):
            sg.append(sum((-a[j] if col[i] == col[j] else a[j]) for j in range(hh) if A[i][j]))
        if any(sg[i] < 0 for i in range(hh) if a[i] > 0):
            continue
        ok = True
        for i in range(hh):
            rhs = sum(a[j] * (2 - sg[j]) for j in range(hh)
                      if A[i][j] and col[i] != col[j] and sg[j] <= 1)
            if sg[i] < rhs:
                ok = False
        if not ok:
            continue

        def dl(S):
            v = -sum(a[i] * sg[i] for i in range(hh) if (S >> i) & 1)
            for i in range(hh):
                if not (S >> i) & 1:
                    continue
                for j in range(i + 1, hh):
                    if (S >> j) & 1 and A[i][j]:
                        v += (-2 if col[i] == col[j] else 2) * a[i] * a[j]
            return v
        if locbest is None or M > locbest:
            locbest = M
        st = True
        for i in range(hh):
            for T in indep:
                if T & nb[i]:
                    continue
                S = nb[i] | T
                if S == 0 or S == (1 << hh) - 1:
                    continue
                if dl(S) > 0:
                    st = False
                    break
            if not st:
                break
        if not st:
            continue
        if starbest is None or M > starbest:
            starbest = M
        if all(dl(S) <= 0 for S in range(1, (1 << hh) - 1)):
            if allbest is None or M > allbest:
                allbest = M
    return N, bestbip, locbest, starbest, allbest


for (wname, m, w, why) in WITNESSES:
    g = gamma(m)
    adjmat = [[1 if g[i][j] else 0 for j in range(m)] for i in range(m)]
    N, bip, loc, star, alll = analyse_pattern(adjmat, w)
    f = lambda x: (str(F(25 * x, N * N)) if x is not None else "none")
    print(f"   {wname:28s} {m:3d} {sum(1 for x in w if x>0):3d} {N:4d}  {f(bip):>12s}  {f(loc):>14s}  "
          f"{f(star):>14s}  {f(alll):>6s}")
print()
print("   (25*bip/N^2 <= 1 is the conjecture on that witness; LOC/STAR entries > 1 are")
print("    configurations the mechanism cannot exclude; 'none' = family excludes everything.)")

print()
print("   EXACT TIGHTNESS on C5[n] (mandatory):")
c5 = [[1 if (abs(i - j) % 5) in (1, 4) else 0 for j in range(5)] for i in range(5)]
for n in range(1, 9):
    N, bip, loc, star, alll = analyse_pattern(c5, [n] * 5)
    print(f"     C5[{n}]: N={N:3d}  bip={bip:3d}  25*bip/N^2 = {F(25*bip, N*N)}  "
          f"{'TIGHT' if F(25*bip, N*N) == 1 else 'NOT TIGHT <<<'}   "
          f"LOC ceiling {F(25*loc,N*N) if loc else 0}  STAR ceiling {F(25*star,N*N) if star else 0}")

print()
print(HR)
print("F2  Fact 2.1 (radius-2 transport) and Fact 2.2 ((*) tight) on C5[n]")
print(HR)
for n in (1, 2, 3, 4):
    cls, V = [], 0
    for i in range(5):
        cls.append(list(range(V, V + n))); V += n
    adj = [0] * V
    for i in range(5):
        j = (i + 1) % 5
        for x in cls[i]:
            for y in cls[j]:
                adj[x] |= 1 << y; adj[y] |= 1 << x
    Y = 0
    for i in (1, 3, 4):
        for x in cls[i]:
            Y |= 1 << x
    sg = sigma(V, adj, Y)
    dM = [(pc(adj[v]) - sg[v]) // 2 for v in range(V)]
    mu = [F(V) - F(25, 2) * dM[v] for v in range(V)]
    per = [mu[c[0]] for c in cls]
    # which classes are in surplus / deficit, and are all deficit classes at
    # G-distance >= 2 from some surplus class?
    print(f"   C5[{n}] N={V}: mu per class = {per} ; sum = {sum(mu)}")
    # the two specific (*) instances Fact 2.2 names
    for (ci, tname) in ((2, "T = c2"), (4, "T = c4")):
        v = cls[ci][0]
        S = adj[v]
        for x in cls[ci]:
            S |= 1 << x
        print(f"      v in c{ci}, {tname}: Delta(N(v) u T) = {delta_recompute(V, adj, Y, S)} (claim 0)")
    mx = None
    for v in range(V):
        Nv = adj[v]
        for T in indep_sets(V, adj, ((1 << V) - 1) & ~Nv):
            d = delta_recompute(V, adj, Y, Nv | T)
            if mx is None or d > mx:
                mx = d
    print(f"      max Delta over the whole family (*) = {mx}")

print()
print(HR)
print("F3  Q2.md section 3: is X = A1 u A4 the UNIQUE locally-maximal non-optimal part-cut of W_b?")
print(HR)
for b in (3, 4, 5, 6):
    w = [b + 1, b, b, b + 1]
    cls, V = [], 0
    for i in range(4):
        cls.append(list(range(V, V + w[i]))); V += w[i]
    adj = [0] * V
    for i in range(3):
        for x in cls[i]:
            for y in cls[i + 1]:
                adj[x] |= 1 << y; adj[y] |= 1 << x
    res = []
    for cm in range(1 << 3):
        col = [0, (cm >> 0) & 1, (cm >> 1) & 1, (cm >> 2) & 1]
        Y = 0
        for i in range(4):
            if col[i]:
                for x in cls[i]:
                    Y |= 1 << x
        M = mono(V, adj, Y)
        sg = sigma(V, adj, Y)
        if M == 0:
            continue
        # locally maximal = sigma>=0 and all switch-stars
        ok = all(s >= 0 for s in sg)
        for v in range(V):
            yv = (Y >> v) & 1
            NB = adj[v] & (Y if not yv else ~Y) & ((1 << V) - 1)
            rhs = 0
            j = NB
            while j:
                bb = j & -j; k = bb.bit_length() - 1; j ^= bb
                if 2 - sg[k] > 0:
                    rhs += 2 - sg[k]
            if sg[v] < rhs:
                ok = False
        if ok:
            res.append((col, M, [sg[c[0]] for c in cls]))
    print(f"   b={b}: non-optimal part-cuts passing sigma>=0 + switch-star: {len(res)}")
    for (col, M, s) in res:
        print(f"       col={col} |M|={M} sigma={s}")
