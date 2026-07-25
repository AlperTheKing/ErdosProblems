"""audit_G9_density.py -- two remaining G9 claims:

 (i)  G9 section 3d: "W_t's densest induced subgraph is P_2 u P_3, e/s = 3.5t = 0.14N".
      -> exhaustive part-wise maximisation of e(S)/|S| over W_t.
 (ii) G9 section 3b/E: "For all S except S subset of P_0 the crude bound (E(S)-s)/2
      already exceeds the budget".
      -> exhaustive part-wise list of the S where the crude bound does NOT exceed it.
Exact Fractions.
"""
from fractions import Fraction
from itertools import product

E5 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]

for t in (1, 2, 3):
    a = [7 * t, 2 * t, 7 * t, 7 * t, 2 * t]
    N = sum(a)
    m = sum(a[u] * a[v] for u, v in E5)
    best, arg = None, []
    for s in product(*[range(x + 1) for x in a]):
        ssz = sum(s)
        if ssz == 0:
            continue
        eS = sum(s[u] * s[v] for u, v in E5)
        r = Fraction(eS, ssz)
        if best is None or r > best:
            best, arg = r, [s]
        elif r == best:
            arg.append(s)
    print("t=%d  max_S e(S)/|S| = %s = %.4f  ( = %.4f N )  attained at %s%s"
          % (t, best, float(best), float(Fraction(best, N)), arg[:4],
             " ..." if len(arg) > 4 else ""))
    p23 = [0, 0, 7 * t, 7 * t, 0]
    print("       G9's claim  e(P2 u P3)/|P2 u P3| = %s = %.4f = %.4f N"
          % (Fraction(49 * t * t, 14 * t), 49.0 * t / 14, 49.0 * t / 14 / (25 * t)))
    print("       whole graph e(V)/N = %s = %.4f = %.4f N"
          % (Fraction(m, N), float(Fraction(m, N)), float(Fraction(m, N * N))))
    print()

print("=== crude-bound survivors (S where (E(S)-s)/2 <= budget) ===")
for t in (1, 2, 3):
    a = [7 * t, 2 * t, 7 * t, 7 * t, 2 * t]
    N = sum(a)
    m = sum(a[u] * a[v] for u, v in E5)
    surv = []
    for s in product(*[range(x + 1) for x in a]):
        ssz = sum(s)
        if ssz == 0:
            continue
        rest = [a[i] - s[i] for i in range(5)]
        ES = m - sum(rest[u] * rest[v] for u, v in E5)
        if Fraction(ES - ssz, 2) <= Fraction(2 * N * ssz - ssz * ssz, 25):
            surv.append(s)
    onlyP0 = all(s[1] == s[2] == s[3] == s[4] == 0 for s in surv)
    print("t=%d: %d survivors; all contained in P_0? %s ; examples %s"
          % (t, len(surv), onlyP0, surv[:6]))
