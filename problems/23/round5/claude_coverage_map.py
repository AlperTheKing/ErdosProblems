"""ROOT-AGENT (Claude): a COVERAGE MAP of the proved toolkit, and a rigidity proposition of my own.

Two proved theorems now exist:
  THEOREM A  Lambda(G,x) <= 1/25 for every triangle-free G  (round 8, gated R3-C22), giving
             psi <= 1/25 whenever the signed graph has no odd-K5 minor (Guenin);
  THEOREM D  psi <= (1-rho)^2/25 + rho*eta for an induced C5 C, eta = x(V\\C), rho = x(R),
             R = the non-twin vertices off C; hence psi <= 1/25 when 25*eta + rho <= 2.

PROPOSITION (mine). Define the DEFECT of an induced 5-cycle C at x:
        D(C) = sum_u x_u * (2 - |N(u) cap V(C)|)   >= 0
(nonnegative because Lemma 2's core gives |N(u) cap V(C)| <= (5-1)/2 = 2).
Then:
  (i)  rho(C) <= D(C) <= 2*rho(C);
  (ii) D(C) = 0  ==>  supp(x) is C5-COLOURABLE, hence psi(H,x) <= 1/25 unconditionally.

Proof of (ii): D(C) = 0 forces |N(u) cap C| = 2 for every u in supp(x). Triangle-freeness forbids
the two neighbours from being adjacent, so they lie at distance 2 on C, i.e. u is a full twin of
some class i. Two twins of the same class are non-adjacent (a triangle through c_{i+1} otherwise),
and twins of classes i and i+2 are non-adjacent (a triangle through c_{i+1}). So every edge of the
support runs between consecutive classes, and class(.) is a homomorphism onto C5. QED

This is exactly the equality case of THEOREM A handing THEOREM D its hypothesis: the two theorems
the campaign proved independently meet at D = 0. Verified below on exact instances.

Then the coverage map: over many exact (graph, weighting) instances, which are already settled by
the proved toolkit, and what do the UNSETTLED ones look like? That is the territory a proof still
has to cross, measured rather than guessed.
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


def c5_colourable(n, E, sup):
    """is the subgraph induced on `sup` homomorphic to C5?"""
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


def cycle_order(C, A):
    C = list(C)
    order = [C[0]]
    prev = None
    for _ in range(4):
        nxt = [w for w in A[order[-1]] if w in C and w != prev]
        prev = order[-1]
        order.append(nxt[0] if nxt[0] not in order else nxt[1])
    return order


def induced_c5s(n, E):
    A = adjacency(n, E)
    return [S for S in combinations(range(n), 5)
            if all(len(A[v] & set(S)) == 2 for v in S)]


def analyse(n, E, x):
    """returns (psi, best-D, closed_by_thmD, closed_by_D0, best eta/rho at the argmin C)"""
    A = adjacency(n, E)
    sup = {v for v in range(n) if x[v] > 0}
    out = {'psi': psi_exact(n, E, x), 'D': None, 'thmD': False, 'D0': False,
           'eta': None, 'rho': None, 'ncyc': 0}
    best = None
    for C in induced_c5s(n, E):
        out['ncyc'] += 1
        Cs = set(C)
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
        R = [v for v in range(n) if v not in Cs and v not in twin]
        eta = sum(x[v] for v in range(n) if v not in Cs)
        rho = sum(x[v] for v in R)
        D = sum(x[u] * (2 - len(A[u] & Cs)) for u in range(n))
        if best is None or D < best[0]:
            best = (D, eta, rho)
        if 25 * eta + rho <= 2:
            out['thmD'] = True
        if D == 0:
            out['D0'] = True
    if best:
        out['D'], out['eta'], out['rho'] = best
    return out


print("=== Proposition (i): rho(C) <= D(C) <= 2 rho(C), and (ii) D = 0 => support C5-colourable ===")
rng = np.random.default_rng(20260726)
suite = [("C5", (5, [(i, (i + 1) % 5) for i in range(5)])),
         ("C5[2]", blowup([2, 2, 2, 2, 2])), ("C5[3,1,2,2,1]", blowup([3, 1, 2, 2, 1])),
         ("C5[2,0,2,2,2]", blowup([2, 0, 2, 2, 2])),
         ("Petersen", petersen()), ("Grotzsch", grotzsch()), ("Wagner", gamma_g(8)),
         ("Gamma_11", gamma_g(11)), ("N=14 extremal", g6("M?AE@bH{AYN_LgBs?"))]
bad_i = bad_ii = tested = 0
d0_cases = 0
for name, (n, E) in suite:
    A = adjacency(n, E)
    for t in range(14):
        a = rng.integers(0, 6, size=n)
        if a.sum() == 0:
            continue
        x = [F(int(v), int(a.sum())) for v in a]
        sup = {v for v in range(n) if x[v] > 0}
        for C in induced_c5s(n, E):
            Cs = set(C)
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
            rho = sum(x[v] for v in range(n) if v not in Cs and v not in twin)
            D = sum(x[u] * (2 - len(A[u] & Cs)) for u in range(n))
            tested += 1
            if not (rho <= D <= 2 * rho):
                bad_i += 1
            if D == 0:
                d0_cases += 1
                if not c5_colourable(n, E, sup):
                    bad_ii += 1
                    print(f"    (ii) FAILS on {name}, x = {[str(t) for t in x]}, C = {C}")
print(f"  instances (graph, x, induced C5): {tested}")
print(f"  (i)  rho <= D <= 2 rho  violations: {bad_i}")
print(f"  (ii) D = 0 cases: {d0_cases}, of which support NOT C5-colourable: {bad_ii}")

print("\n=== coverage map: what the proved toolkit already settles, and what it does not ===")
rows = []
for name, (n, E) in suite:
    tot = closed = viol = 0
    resid = []
    for t in range(40):
        a = rng.integers(0, 7, size=n)
        if a.sum() == 0:
            continue
        x = [F(int(v), int(a.sum())) for v in a]
        r = analyse(n, E, x)
        tot += 1
        sup = {v for v in range(n) if x[v] > 0}
        cov = r['thmD'] or r['D0'] or c5_colourable(n, E, sup)
        if cov:
            closed += 1
        else:
            resid.append((r['psi'], r['eta'], r['rho'], r['D']))
        if r['psi'] > F(1, 25):
            viol += 1
    worst = max((p for p, _, _, _ in resid), default=None)
    rows.append((name, tot, closed, len(resid), worst, viol))
print(f"  {'graph':16s} {'inst':>5s} {'settled':>8s} {'residual':>9s} {'max psi in residual':>21s}"
      f" {'psi>1/25':>9s}")
for name, tot, closed, nres, worst, viol in rows:
    print(f"  {name:16s} {tot:5d} {closed:8d} {nres:9d} "
          f"{(str(worst) + ' = ' + f'{float(worst):.5f}') if worst is not None else '-':>21s} {viol:9d}")
print("\n  'settled' = C5-colourable support, or D = 0, or Theorem D's 25*eta + rho <= 2.")
print("  The residual column is the territory a proof still has to cross.")
