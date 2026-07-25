"""audit_Q2_v2_a.py -- AUDIT pass 2, block A:
   A1  Lemma 1 (switching identity + 'max cut iff all Delta(S)<=0')
   A2  Lemma 2 (blow-up multilinearity / corner certificate)
   A3  C5[n] ledger, charge identity, family (*) tightness
   A4  W_b = P4[b+1,b,b,b+1]  minimum improving switch  (R1)
Everything exact integers.
"""
import sys, random
from fractions import Fraction as F
from itertools import combinations, product
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q2_v2_core import (g6, g6_encode, pc, edges, is_trianglefree, mono,
                              maxcut_bip, sigma, delta_recompute, delta_formula,
                              star_sets, family_star_ineq, indep_sets)

random.seed(20260725)
HR = "=" * 78


def blowup(pat, w):
    """pat = list of adjacency masks on h vertices; w = weights.  -> (n, adj, classes)."""
    h = len(pat)
    cls, n = [], 0
    for i in range(h):
        cls.append(list(range(n, n + w[i])))
        n += w[i]
    adj = [0] * n
    for i in range(h):
        for j in range(h):
            if (pat[i] >> j) & 1:
                for x in cls[i]:
                    for y in cls[j]:
                        if x != y:
                            adj[x] |= 1 << y
    return n, adj, cls


def C5pat():
    p = [0] * 5
    for i in range(5):
        p[i] |= 1 << ((i + 1) % 5)
        p[i] |= 1 << ((i + 4) % 5)
    return p


def Pkpat(k):
    p = [0] * k
    for i in range(k - 1):
        p[i] |= 1 << (i + 1)
        p[i + 1] |= 1 << i
    return p


# ------------------------------------------------------------------ A1
print(HR); print("A1  LEMMA 1: Delta(S) recomputed vs formula; maxcut <=> all Delta<=0")
print(HR)
import subprocess
GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
bad_id = bad_mc = tested = 0
for nn in (5, 6, 7, 8):
    out = subprocess.run([GENG, "-t", "-c", str(nn)], capture_output=True, text=True).stdout.split()
    for line in out:
        n, adj = g6(line)
        for Y in range(1 << (n - 1)):
            sg = sigma(n, adj, Y)
            # identity on a random sample of S plus all |S|<=2
            Ss = [0]
            Ss += [1 << i for i in range(n)]
            Ss += [(1 << i) | (1 << j) for i in range(n) for j in range(i + 1, n)]
            Ss += [random.getrandbits(n) for _ in range(6)]
            for S in Ss:
                a = delta_recompute(n, adj, Y, S)
                b = delta_formula(n, adj, Y, S, sg)
                tested += 1
                if a != b:
                    bad_id += 1
                    print("   IDENTITY MISMATCH", line, Y, S, a, b)
        # max-cut characterisation, all cuts, all S (n<=8 -> cheap)
        best = min(mono(n, adj, Y) for Y in range(1 << (n - 1)))
        for Y in range(1 << (n - 1)):
            allle = all(delta_recompute(n, adj, Y, S) <= 0 for S in range(1 << n))
            if allle != (mono(n, adj, Y) == best):
                bad_mc += 1
                print("   MAXCUT CHARACTERISATION MISMATCH", line, Y)
print(f"   identity checks = {tested}, mismatches = {bad_id}")
print(f"   'maxcut <=> all Delta(S)<=0' mismatches = {bad_mc}")
print("   VERDICT L1:", "CONFIRMED" if bad_id == 0 and bad_mc == 0 else "REFUTED")

# ------------------------------------------------------------------ A2
print(); print(HR); print("A2  LEMMA 2: corner check  <=>  maximum cut, for blow-ups")
print(HR)
bad2 = 0
tot2 = 0
pats = {"C5": C5pat(), "P4": Pkpat(4), "C4": [0b0010 | 0b1000, 0b0101, 0b1010, 0b0101 ^ 0b0001]}
# build C4 properly: 0-1-2-3-0
c4 = [0] * 4
for (i, j) in [(0, 1), (1, 2), (2, 3), (3, 0)]:
    c4[i] |= 1 << j; c4[j] |= 1 << i
pats["C4"] = c4
for name, p in pats.items():
    h = len(p)
    for w in product(range(0, 4), repeat=h):
        if sum(w) == 0 or sum(w) > 9:
            continue
        n, adj, cls = blowup(p, list(w))
        if n == 0:
            continue
        best = min(mono(n, adj, Y) for Y in range(1 << (n - 1)))
        for cm in range(1 << h):
            Y = 0
            for i in range(h):
                if (cm >> i) & 1:
                    for x in cls[i]:
                        Y |= 1 << x
            sg = sigma(n, adj, Y)
            corner_ok = True
            for Sm in range(1 << h):
                S = 0
                for i in range(h):
                    if (Sm >> i) & 1:
                        for x in cls[i]:
                            S |= 1 << x
                if delta_recompute(n, adj, Y, S) > 0:
                    corner_ok = False
                    break
            true_max = (mono(n, adj, Y) == best)
            tot2 += 1
            if corner_ok != true_max:
                bad2 += 1
                print("   CORNER MISMATCH", name, w, cm)
print(f"   part-respecting cuts tested = {tot2}, corner-certificate mismatches = {bad2}")
print("   VERDICT L2:", "CONFIRMED" if bad2 == 0 else "REFUTED")

# ------------------------------------------------------------------ A3
print(); print(HR); print("A3  C5[n] ledger, charge identity, family (*) tightness")
print(HR)
p5 = C5pat()
for nn in range(1, 9):
    w = [nn] * 5
    n, adj, cls = blowup(p5, w)
    Y = 0
    for i in (1, 3, 4):
        for x in cls[i]:
            Y |= 1 << x
    M = mono(n, adj, Y)
    E = len(edges(n, adj))
    sg = sigma(n, adj, Y)
    mu = [F(n) - F(25, 2) * (len(bin(adj[v] & ((Y if (Y >> v) & 1 else ~Y)) & ((1 << n) - 1)).replace("0b", "").replace("0", "")) if False else 0) for v in range(n)]
    dM = [(pc(adj[v]) - sg[v]) // 2 for v in range(n)]
    mu = [F(n) - F(25, 2) * dM[v] for v in range(n)]
    summu = sum(mu)
    ismax = (M == maxcut_bip(n, adj)) if n <= 22 else None
    # family (*) : max Delta over S = N(v) u T
    if n <= 20:
        mx = max(delta_recompute(n, adj, Y, S) for S in family_star_ineq(n, adj, Y))
    else:
        mx = None
    print(f"   C5[{nn}] N={n:3d} |E|={E:4d} |M|={M:3d}  25|M|-N^2={25*M-n*n:3d}  sum mu={summu} "
          f"(target N^2-25|M| = {n*n-25*M})  maxcut? {ismax}  max Delta over (*) = {mx}")
print("   [dM per class]", "c0,c1,c2 -> 0 ; c3,c4 -> n   mu = +N and -(3/2)N as claimed" )

# ------------------------------------------------------------------ A4
print(); print(HR); print("A4  W_b = P4[b+1,b,b,b+1], X = A1 u A4 : minimum improving switch (R1)")
print(HR)
p4 = Pkpat(4)


def wb_min_switch_counts(b):
    """own count-level enumeration over the 4 parts (twins => counts suffice)."""
    w = [b + 1, b, b, b + 1]
    col = [0, 1, 1, 0]        # X = A1 u A4
    sg = []
    for i in range(4):
        s = 0
        for j in range(4):
            if (p4[i] >> j) & 1:
                s += -w[j] if col[i] == col[j] else w[j]
        sg.append(s)
    best = None
    for s0 in range(w[0] + 1):
        for s1 in range(w[1] + 1):
            for s2 in range(w[2] + 1):
                for s3 in range(w[3] + 1):
                    sv = (s0, s1, s2, s3)
                    d = -sum(sv[i] * sg[i] for i in range(4))
                    for i in range(4):
                        for j in range(i + 1, 4):
                            if (p4[i] >> j) & 1:
                                d += (-2 if col[i] == col[j] else 2) * sv[i] * sv[j]
                    if d > 0:
                        t = sum(sv)
                        if best is None or t < best[0]:
                            best = (t, sv, d)
    return best, sg, w


print("    b | N  | sigma        | |M| | 25|M|-N^2 | min|S| | |S|/N        | witness (s1,s2,s3,s4) | Q2.md")
q2tab = {3: 5, 4: 5, 5: 6, 6: 7, 8: 8, 10: 10, 12: 11}
for b in list(range(2, 21)) + [30, 50]:
    best, sg, w = wb_min_switch_counts(b)
    N = 4 * b + 2
    M = b * b
    claim = q2tab.get(b, "")
    flag = ""
    if b in q2tab:
        flag = "ok" if q2tab[b] == best[0] else f"<<< MISMATCH Q2.md says {q2tab[b]}"
    print(f"   {b:3d} | {N:3d} | {str(sg):12s} | {M:3d} | {25*M-N*N:6d} | {best[0]:5d}  | "
          f"{str(F(best[0],N)):10s} = {float(F(best[0],N)):.4f} | {best[1]} d={best[2]} | {flag}")

# vertex-level cross-check for small b over ALL 2^N subsets
for b in (2, 3, 4):
    w = [b + 1, b, b, b + 1]
    n, adj, cls = blowup(p4, w)
    Y = 0
    for i in (1, 2):
        for x in cls[i]:
            Y |= 1 << x
    M = mono(n, adj, Y)
    bestS = None
    for S in range(1 << n):
        if delta_recompute(n, adj, Y, S) > 0:
            k = pc(S)
            if bestS is None or k < bestS:
                bestS = k
    cnt = wb_min_switch_counts(b)[0][0]
    print(f"   [vertex level] b={b} N={n} |M|={M} 25|M|-N^2={25*M-n*n} "
          f"min|S| over ALL 2^{n} subsets = {bestS}  (count-enum: {cnt})  "
          f"{'AGREE' if bestS == cnt else 'DISAGREE'}")

# the (*) refutation of W_b claimed in Q2.md section 3
print("   (*) applied to W_b (claim: Delta(N(v) u A1) = b^2 > 0):")
for b in (2, 3, 4, 5):
    w = [b + 1, b, b, b + 1]
    n, adj, cls = blowup(p4, w)
    Y = 0
    for i in (1, 2):
        for x in cls[i]:
            Y |= 1 << x
    v = cls[0][0]
    S = adj[v]
    for x in cls[0]:
        S |= 1 << x
    print(f"     b={b}: v in A1, T = A1: Delta = {delta_recompute(n, adj, Y, S)}  (b^2 = {b*b})  |S| = {pc(S)}")
