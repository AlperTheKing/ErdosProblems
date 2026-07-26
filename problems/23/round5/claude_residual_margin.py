"""ROOT-AGENT (Claude): does the proved toolkit already cover everything NEAR the extremal value?

The coverage map showed something worth chasing: over random weightings the instances the toolkit
does NOT settle had psi at most 0.0298, well under 1/25 = 0.04. If that holds in general -- if every
instance with psi close to 1/25 is settled -- then the conjecture reduces to proving

        psi <= 1/25 - epsilon   OFF the settled region,

a statement WITH ROOM TO SPARE rather than the sharp one. Sharpness is what has killed every
mechanism in this campaign (the 1/20 barrier, the plateau, the tightness of Theorem A), so a
non-sharp residual target would be a genuine change of character.

"Settled" means one of the three proved facts applies:
    * the support is C5-colourable                      (Theorem B / accepted base)
    * D(C) = 0 for some induced C5                      (my Proposition; implies the above)
    * 25*eta(C) + rho(C) <= 2 for some induced C5       (Theorem D)

The dangerous region is sampled deliberately, not uniformly: weightings are built by perturbing
C5-concentrations at many scales, since that is where psi is large. Uniform random weightings would
miss it entirely.

Reported: MAX psi over UNSETTLED instances, per graph and overall. Exact rationals throughout.
"""
from fractions import Fraction as F
from itertools import combinations

import numpy as np


def gamma_g(m):
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


def blowup(a):
    n = sum(a)
    part, k = [], 0
    for s in a:
        part.append(list(range(k, k + s)))
        k += s
    E = []
    for i in range(5):
        for u in part[i]:
            for v in part[(i + 1) % 5]:
                E.append((min(u, v), max(u, v)))
    return n, E


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


def psi_exact(n, E, x):
    best = None
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        s = sum(x[u] * x[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        if best is None or s < best:
            best = s
    return best


def induced_c5s(n, E):
    A = adjacency(n, E)
    return [S for S in combinations(range(n), 5)
            if all(len(A[v] & set(S)) == 2 for v in S)]


def cycle_order(C, A):
    C = list(C)
    order = [C[0]]
    prev = None
    for _ in range(4):
        nxt = [w for w in A[order[-1]] if w in C and w != prev]
        prev = order[-1]
        order.append(nxt[0] if nxt[0] not in order else nxt[1])
    return order


def c5_colourable(n, E, sup):
    sup = sorted(sup)
    A = adjacency(n, E)
    col = {}

    def rec(i):
        if i == len(sup):
            return True
        v = sup[i]
        for c in range(5 if i else 1):
            if all(not (w in col and (col[w] - c) % 5 not in (1, 4)) for w in A[v] if w in col):
                col[v] = c
                if rec(i + 1):
                    return True
                del col[v]
        return False

    return rec(0)


def settled(n, E, C5s, A, x):
    sup = {v for v in range(n) if x[v] > 0}
    if c5_colourable(n, E, sup):
        return True
    for C in C5s:
        Cs = set(C)
        if sum(x[u] * (2 - len(A[u] & Cs)) for u in range(n)) == 0:
            return True
        order = cycle_order(C, A)
        twin = set()
        for v in range(n):
            if v in Cs:
                continue
            nb = A[v] & Cs
            for i in range(5):
                if nb == {order[(i - 1) % 5], order[(i + 1) % 5]}:
                    twin.add(v)
                    break
        eta = sum(x[v] for v in range(n) if v not in Cs)
        rho = sum(x[v] for v in range(n) if v not in Cs and v not in twin)
        if 25 * eta + rho <= 2:
            return True
    return False


suite = [("Petersen", petersen()), ("Grotzsch", grotzsch()), ("Wagner", gamma_g(8)),
         ("Gamma_11", gamma_g(11)), ("Gamma_14", gamma_g(14)),
         ("N=14 extremal", g6("M?AE@bH{AYN_LgBs?")),
         ("C5[2]", blowup([2, 2, 2, 2, 2])), ("C5[3,1,2,2,1]", blowup([3, 1, 2, 2, 1]))]

rng = np.random.default_rng(20260726)
print(f"  {'graph':16s} {'instances':>10s} {'unsettled':>10s} {'max psi UNSETTLED':>20s} "
      f"{'max psi settled':>17s}")
glob_unsettled = None
for name, (n, E) in suite:
    A = adjacency(n, E)
    C5s = induced_c5s(n, E)
    if not C5s:
        continue
    inst = 0
    best_un = None
    best_set = None
    # deliberately sample the dangerous region: perturb C5-concentrations at many scales
    for C in C5s[:12]:
        for q in (5, 10, 15, 20, 25, 40, 60):
            for trial in range(10):
                a = [0] * n
                for v in C:
                    a[v] = q
                k = rng.integers(1, max(2, n - 4))
                for _ in range(int(k)):
                    w = int(rng.integers(0, n))
                    a[w] += int(rng.integers(1, max(2, q // 2 + 1)))
                tot = sum(a)
                if tot == 0:
                    continue
                x = [F(v, tot) for v in a]
                ps = psi_exact(n, E, x)
                inst += 1
                if settled(n, E, C5s, A, x):
                    if best_set is None or ps > best_set:
                        best_set = ps
                else:
                    if best_un is None or ps > best_un:
                        best_un = ps
    if best_un is not None and (glob_unsettled is None or best_un > glob_unsettled[0]):
        glob_unsettled = (best_un, name)
    su = f"{str(best_un)} = {float(best_un):.5f}" if best_un is not None else "-"
    ss = f"{float(best_set):.5f}" if best_set is not None else "-"
    print(f"  {name:16s} {inst:10d} {'yes' if best_un is not None else 'no':>10s} {su:>20s} {ss:>17s}")

print(f"\n  worst UNSETTLED instance anywhere: psi = {glob_unsettled[0]} = "
      f"{float(glob_unsettled[0]):.6f} on {glob_unsettled[1]}")
print(f"  target 1/25 = 0.040000;  margin = {float(F(1,25) - glob_unsettled[0]):.6f} "
      f"= {glob_unsettled[0] / F(1,25) * 100:.2f}% of the target")
print("\n  If this margin is real, the conjecture reduces OFF the settled region to a NON-SHARP")
print("  bound, which is a different kind of statement from the sharp one that has killed every")
print("  mechanism so far. If instead some unsettled instance approaches 1/25, this route is dead.")
