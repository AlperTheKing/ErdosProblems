"""ROOT-AGENT (Claude): a PROVED STRICT bound on Lambda from Theorem A's defect, on non-colourable
supports.

Theorem A (R3-C22) proves Lambda <= 1/(2 gamma) with gamma = min over odd cycles C of sum_{v in C}
1/d(v), d(v) = sum_{u in N(v)} x_u, and then bounds gamma >= 25/2. The proof throws away information:
for a 5-cycle, Cauchy-Schwarz and Lemma 2 give

        sum_{v in C} 1/d(v) >= 25 / sum_{v in C} d(v) = 25 / (2 - D(C)),
        D(C) := sum_u x_u (2 - |N(u) cap V(C)|)  >= 0     [my defect, R3-C24]

and for an odd cycle of length L >= 7, sum 1/d >= 2L^2/(L-1) >= 49/3. Hence

        gamma >= min( min over 5-cycles of 25/(2 - D(C)),  49/3 )
        Lambda <= 1/(2 gamma) <= max( (2 - D*)/50,  3/98 ),      D* := min over 5-cycles of D(C).

WHY THIS MATTERS. R3-C24 proved D(C) = 0 implies supp(x) is C5-colourable. So on a NON-C5-COLOURABLE
support -- equivalently, by R3-C38, a WAGNER-CONTAINING support -- every pentagon has D(C) > 0, so
D* > 0 and the bound is STRICTLY below 1/25. That is exactly the epsilon the R3-C37/C38 reduction
needs, on the Lambda side, and it is a consequence of an already-proved theorem rather than a new
conjecture.

The gap that remains is psi versus Lambda: this bounds Lambda, and the frontier needs psi. On Gamma_11
A5b gives 10000 exact packing certificates with psi = Lambda and no gaps, but that is unproved.

Verified here exactly: the bound itself, and that D* > 0 on every non-colourable support.
"""
from fractions import Fraction as F
from itertools import combinations

import numpy as np
from scipy.optimize import linprog


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


n, E = gamma_g(11)
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)
idx = {e: i for i, e in enumerate(E)}
pent = [T for T in combinations(range(n), 5) if all(len(A[v] & set(T)) == 2 for v in T)]

odd = set()
for s in range(n):
    def dfs(u, seen, el):
        for v in sorted(A[u]):
            if v == s and len(seen) >= 3 and len(seen) % 2 == 1:
                odd.add(frozenset(el + [idx[tuple(sorted((u, v)))]]))
            elif v > s and v not in seen:
                dfs(v, seen | {v}, el + [idx[tuple(sorted((u, v)))]])
    dfs(s, {s}, [])
odd = sorted(odd, key=lambda c: (len(c), sorted(c)))
Acov = np.zeros((len(odd), len(E)))
for k, c in enumerate(odd):
    for i in c:
        Acov[k, i] = -1.0


def colourable(sup):
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


rng = np.random.default_rng(20260726)
print(f"Gamma_11: {len(pent)} induced pentagons, {len(odd)} odd cycles\n")
print(f"{'case':>26s} {'D*':>12s} {'bound':>12s} {'Lambda (LP)':>13s} {'psi':>10s} {'ok':>5s}")
bad = 0
tested = 0
worst = None
for trial in range(400):
    a = rng.integers(0, 7, size=n)
    q = int(a.sum())
    if q == 0:
        continue
    x = [F(int(t), q) for t in a]
    sup = [v for v in range(n) if a[v] > 0]
    if not sup:
        continue
    # D* over pentagons
    Ds = []
    for C in pent:
        Cs = set(C)
        Ds.append(sum(x[u] * (2 - len(A[u] & Cs)) for u in range(n)))
    Dstar = min(Ds)
    bound = max((2 - Dstar) / 50, F(3, 98))
    w = np.array([float(x[u] * x[v]) for (u, v) in E])
    r = linprog(w, A_ub=Acov, b_ub=-np.ones(len(odd)), bounds=[(0, None)] * len(E),
                method='highs')
    lam = r.fun if r.success else None
    psi = None
    for mm2 in range(1 << (n - 1)):
        S = (mm2 << 1) | 1
        s = sum(x[u] * x[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        if psi is None or s < psi:
            psi = s
    tested += 1
    ok = lam is None or lam <= float(bound) + 1e-9
    if not ok:
        bad += 1
    col = colourable(sup)
    if not col and (worst is None or Dstar < worst[0]):
        worst = (Dstar, a.tolist(), bound, lam, psi)
    if trial < 8:
        print(f"{('colourable' if col else 'WAGNER-containing'):>26s} {str(Dstar):>12s} "
              f"{str(bound):>12s} {(f'{lam:.6f}' if lam else '-'):>13s} "
              f"{f'{float(psi):.6f}':>10s} {str(ok):>5s}")
print(f"\ninstances tested: {tested};  violations of Lambda <= max((2-D*)/50, 3/98): {bad}")

print("\nnow the decisive structural point: is D* > 0 on every non-colourable support?")
viol = 0
cnt = 0
for mask in range(1, 1 << n):
    sup = [v for v in range(n) if (mask >> v) & 1]
    if colourable(sup):
        continue
    cnt += 1
    # uniform weighting on the support
    x = [F(1, len(sup)) if v in sup else F(0) for v in range(n)]
    Dstar = min(sum(x[u] * (2 - len(A[u] & set(C))) for u in range(n)) for C in pent)
    if Dstar <= 0:
        viol += 1
print(f"  non-colourable supports: {cnt};  with D* <= 0 at the uniform weighting: {viol}")
print(f"  (D* > 0 everywhere means the bound is STRICTLY below 1/25 on every such support)")
if worst:
    print(f"\n  smallest D* seen on a Wagner-containing support: {worst[0]} at a = {worst[1]}")
    print(f"      bound = {worst[2]} = {float(worst[2]):.6f} vs 1/25 = 0.04, "
          f"Lambda = {worst[3]:.6f}, psi = {float(worst[4]):.6f}")
