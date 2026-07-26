"""ROOT-AGENT (Claude): adversarially test MY OWN R3-C39 reduction before it is allowed to stand.

R3-C39 claimed the conjecture follows from

        (GAP)  psi(G,x) - Lambda(G,x) <= D*(x)/50   for non-C5-colourable supports,

since the proved refinement Lambda <= max((2-D*)/50, 3/98) then gives psi <= 2/50 = 1/25.

TWO THINGS TO CHECK, and I expect one of them to hurt.

(1) AN ERROR IN MY OWN ENTRY. R3-C39 says "graphs with NO induced C5 are handled by the other
    branch: Lambda <= 3/98 < 1/25". That is FALSE. Registry A28 established that sup psi/Lambda over
    triangle-free graphs equals the general weighted MinUnCut LP gap and is UNBOUNDED, so bounding
    Lambda says nothing about psi. Pentagon-free triangle-free graphs are NOT closed by that branch
    and remain a genuinely open piece of the reduction. Recorded as a correction.

(2) IS (GAP) EVEN TRUE? Test it exactly wherever both sides are computable, including the graphs with
    the largest known integrality gaps, since those are where it should break if it breaks.
"""
from fractions import Fraction as F
from itertools import combinations

import numpy as np
from scipy.optimize import linprog


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


def build(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    idx = {tuple(sorted(e)): i for i, e in enumerate(E)}
    odd = set()
    for s in range(n):
        def dfs(u, seen, el):
            for v in sorted(A[u]):
                if v == s and len(seen) >= 3 and len(seen) % 2 == 1:
                    odd.add(frozenset(el + [idx[tuple(sorted((u, v)))]]))
                elif v > s and v not in seen:
                    dfs(v, seen | {v}, el + [idx[tuple(sorted((u, v)))]])
        dfs(s, {s}, [])
    pent = [T for T in combinations(range(n), 5) if all(len(A[v] & set(T)) == 2 for v in T)]
    return A, sorted(odd, key=lambda c: (len(c), sorted(c))), pent


def colourable(n, A, sup):
    sup = sorted(sup)
    c = {}

    def rec(i):
        if i == len(sup):
            return True
        v = sup[i]
        for t in range(5 if i else 1):
            if all((c[w] - t) % 5 in (1, 4) for w in A[v] if w in c):
                c[v] = t
                if rec(i + 1):
                    return True
                c.pop(v)
        return False

    return rec(0)


suite = [("C5", (5, [(i, (i + 1) % 5) for i in range(5)])), ("Wagner", gamma_g(8)),
         ("Petersen", petersen()), ("Grotzsch", grotzsch()), ("Gamma_11", gamma_g(11)),
         ("N=14 extremal", g6("M?AE@bH{AYN_LgBs?"))]
rng = np.random.default_rng(20260726)
print(f"{'graph':16s} {'instances':>10s} {'GAP violations':>15s} {'worst psi-Lambda vs D*/50':>28s}")
for name, (n, E) in suite:
    A, odd, pent = build(n, E)
    if not odd:
        continue
    Acov = np.zeros((len(odd), len(E)))
    for k, c in enumerate(odd):
        for i in c:
            Acov[k, i] = -1.0
    viol = 0
    tested = 0
    worst = None
    for trial in range(150):
        a = rng.integers(0, 7, size=n)
        q = int(a.sum())
        if q == 0:
            continue
        x = [F(int(t), q) for t in a]
        sup = [v for v in range(n) if a[v] > 0]
        if colourable(n, A, sup) or not pent:
            continue
        psi = None
        for mm in range(1 << (n - 1)):
            S = (mm << 1) | 1
            s = sum(x[u] * x[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
            if psi is None or s < psi:
                psi = s
        w = np.array([float(x[u] * x[v]) for (u, v) in E])
        r = linprog(w, A_ub=Acov, b_ub=-np.ones(len(odd)), bounds=[(0, None)] * len(E),
                    method='highs')
        if not r.success:
            continue
        lam = r.fun
        Dstar = min(sum(x[u] * (2 - len(A[u] & set(C))) for u in range(n)) for C in pent)
        gap = float(psi) - lam
        rhs = float(Dstar) / 50
        tested += 1
        if gap > rhs + 1e-9:
            viol += 1
            if worst is None or gap - rhs > worst[0]:
                worst = (gap - rhs, a.tolist(), gap, rhs)
    ws = (f"gap {worst[2]:.6f} vs {worst[3]:.6f}" if worst else "none")
    print(f"{name:16s} {tested:10d} {viol:15d} {ws:>28s}")
    if worst:
        print(f"    witness a = {worst[1]}")

print("\n(GAP) is the sole remaining content of the R3-C39 reduction on pentagon-containing graphs.")
print("Pentagon-FREE triangle-free graphs are a separate open piece: R3-C39 wrongly said the")
print("Lambda <= 3/98 branch closes them, but A28's unbounded psi/Lambda ratio means it does not.")
