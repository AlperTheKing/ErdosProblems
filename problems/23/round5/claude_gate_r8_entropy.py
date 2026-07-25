"""ROOT-AGENT GATE (Claude): re-verify the round-8 "entropy/counting" family. Own implementation.

LEMMA R8-3, the claim I most want to check, because it replaces an exhaustive search by a counting
argument. Call F "rainbow-1" if F meets EVERY induced pentagon in exactly one edge (this is the
admissibility condition I already gated from the transport family: at a C5-concentration the
multiplier value is |mono(S) cap E(K)|/25, and any strictly-above-the-minimum aggregator forces that
count to be 1 for every induced pentagon K simultaneously).

Double counting the pairs (e, K) with e in F, K an induced pentagon through e:
        sum_{e in F} p(e)  =  sum_K |F cap E(K)|  =  P,
where p(e) = number of induced pentagons through e and P = total number of induced pentagons.
So if every p(e) is divisible by 5 while P is NOT, no rainbow-1 set can exist.

Claim: in And(4) = Gamma_11 every edge lies in 5 or 10 induced pentagons and P = 33, and 5 does not
divide 33. That would prove R(And(4)) = empty by pure counting -- and it must agree with my earlier
exhaustive finding of 0 admissible cuts among all 1024, and with my count of 33 induced C5s.

Also gated here: the x-adapted Z5-rotation geometric-mean certificate (PRGM), claimed dead on the
Wagner graph at uniform weights via min over all 5^7 maps of prod_r m_r = 162, against
5^10 * 162 > 8^10.
"""
from fractions import Fraction as F
from itertools import combinations, product


def gamma(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


def petersen():
    return 10, ([(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)]
                + [(5 + i, 5 + (i + 2) % 5) for i in range(5)])


def grotzsch():
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E += [(5 + i, (i + 1) % 5), (5 + i, (i + 4) % 5), (10, 5 + i)]
    return 11, E


def g6(s):
    b = [ord(c) - 63 for c in s]
    n = b[0]
    bits = []
    for x in b[1:]:
        bits.extend((x >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    E, p = [], 0
    for j in range(1, n):
        for k in range(j):
            if bits[p]:
                E.append((k, j))
            p += 1
    return n, E


def adjacency(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    return A


def pentagons(n, E):
    """every induced 5-cycle, returned as its edge set"""
    A = adjacency(n, E)
    out = []
    for S in combinations(range(n), 5):
        Ss = set(S)
        if all(len(A[v] & Ss) == 2 for v in S):
            out.append(frozenset((min(u, v), max(u, v))
                                 for u, v in combinations(S, 2) if v in A[u]))
    return out


print("=== LEMMA R8-3: divisibility obstruction to rainbow-1 edge sets ===")
print(f"{'graph':22s} {'P':>5s} {'P mod 5':>8s}  {'p(e) values':22s} {'all p(e)=0 mod 5':>17s}  verdict")
cases = [("C5", (5, [(i, (i + 1) % 5) for i in range(5)])),
         ("Wagner = And(3)", gamma(8)),
         ("Petersen", petersen()),
         ("Grotzsch", grotzsch()),
         ("And(4) = Gamma_11", gamma(11)),
         ("And(5) = Gamma_14", gamma(14)),
         ("N=14 extremal", g6("M?AE@bH{AYN_LgBs?"))]
for name, (n, E) in cases:
    K = pentagons(n, E)
    P = len(K)
    p = {}
    for e in E:
        e = (min(e), max(e))
        p[e] = sum(1 for k in K if e in k)
    vals = sorted(set(p.values()))
    alldiv = all(v % 5 == 0 for v in p.values())
    kill = alldiv and P % 5 != 0
    print(f"{name:22s} {P:5d} {P % 5:8d}  {str(vals):22s} {str(alldiv):>17s}  "
          f"{'NO rainbow-1 set exists' if kill else 'no obstruction from divisibility'}")

print("\n=== cross-check against my earlier exhaustive gate ===")
n11, E11 = gamma(11)
K11 = pentagons(n11, E11)
print(f"  Gamma_11 induced pentagons = {len(K11)} (my transport gate found 33 induced C5s: "
      f"{len(K11) == 33})")
A11 = adjacency(n11, E11)
found = 0
for m in range(1 << (n11 - 1)):
    S = (m << 1) | 1
    Fset = frozenset((u, v) for (u, v) in E11 if ((S >> u) & 1) == ((S >> v) & 1))
    if all(len(Fset & k) == 1 for k in K11):
        found += 1
print(f"  exhaustive rainbow-1 cuts among all 1024: {found}  "
      f"(divisibility predicts 0: {found == 0})")

print("\n=== PRGM: the x-adapted Z5-rotation geometric-mean certificate, at uniform weights ===")
for name, (n, E) in [("Wagner = And(3)", gamma(8)), ("Petersen", petersen()),
                     ("C5", (5, [(i, (i + 1) % 5) for i in range(5)]))]:
    best = None
    for tail in product(range(5), repeat=n - 1):
        phi = (0,) + tail
        prod = 1
        for r in range(5):
            side = {(r + t) % 5 for t in (0, 2, 4)}
            mono = sum(1 for (u, v) in E if ((phi[u] in side) == (phi[v] in side)))
            prod *= mono
            if prod == 0 or (best is not None and prod > best):
                break
        if prod > 0 and (best is None or prod < best):
            best = prod
    lhs = 5 ** 10 * best
    rhs = n ** 10
    print(f"  {name:18s} min over all 5^{n-1} maps of prod_r m_r = {best};  "
          f"5^10*{best} = {lhs}  vs  {n}^10 = {rhs}  -> "
          f"{'FAILS (certificate invalid)' if lhs > rhs else 'holds'}")

print("\n=== the recurring 1/20 barrier, stated exactly ===")
print("  Motzkin-Straus caps the edge weight of a triangle-free graph at 1/4;")
print("  a balanced 5-fold split of that mass gives (1/4)/5 = 1/20, which is exactly the")
print(f"  value A6 attains on every C5[n] and the value the Grotzsch star witness attains: "
      f"{F(1,4)/5} = {float(F(1,20)):.4f} > {float(F(1,25)):.4f} = 1/25")
