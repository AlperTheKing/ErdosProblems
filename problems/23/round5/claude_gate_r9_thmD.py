"""ROOT-AGENT GATE (Claude): the round-9 Theorem D audit. Own implementation.

Three claims decide this round, so I check exactly those.

(1) NECESSITY OF TRIANGLE-FREENESS. Theorem D reads psi <= (1-rho)^2/25 + rho*eta for an induced C5
    C, eta = x(V\\C), rho = x(R), R = non-twin vertices off C. The audit claims it FAILS the moment a
    triangle is allowed: graph6 `Ehf?` = C5 (0-1-2-3-4-0) plus a vertex 5 adjacent to c_0 and c_1,
    with x = (2/5, 2/5, 0, 0, 0, 1/5), giving psi = 2/25 against the bound 41/625.
    Vertex 5's C-neighbourhood {c_0,c_1} is an ADJACENT pair, not a twin pair, so 5 lies in R.

(2) THEOREM F, the improved constant. `psi <= 1/25 whenever eta <= 4/25`, against Theorem D's
    eta <= 1/13. The sharp test is the NEW band eta in (1/13, 4/25]: Theorem D says nothing there and
    Theorem F claims it, so any violation inside that band refutes Theorem F while leaving D intact.

(3) THE AUDIT'S OWN RETRACTION. It first claimed "BAD_i = 0 for SOME i implies psi <= 1/25" and
    withdrew it, on y = (1/6, 1/4, 1/6, 1/4, 1/6): the five cyclic products are
    (1/24, 1/24, 1/24, 1/24, 1/36), so the minimum over any FOUR of them is 1/24 > 1/25.
    A retraction is only worth as much as its witness, so I verify the witness.
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


def has_triangle(n, E):
    A = adjacency(n, E)
    return any(A[u] & A[v] for u, v in E)


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


def eta_rho(n, E, A, C, x):
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
    eta = sum(x[v] for v in range(n) if v not in Cs)
    rho = sum(x[v] for v in range(n) if v not in Cs and v not in twin)
    return eta, rho


print("=== (1) triangle-freeness is NECESSARY for Theorem D ===")
n, E = 6, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4), (0, 5), (1, 5)]
A = adjacency(n, E)
print(f"  graph: C5 + vertex 5 adjacent to c_0 and c_1;  has a triangle: {has_triangle(n, E)}")
x = [F(2, 5), F(2, 5), F(0), F(0), F(0), F(1, 5)]
C = (0, 1, 2, 3, 4)
eta, rho = eta_rho(n, E, A, C, x)
ps = psi_exact(n, E, x)
bound = (1 - rho) ** 2 / 25 + rho * eta
print(f"  x = {[str(t) for t in x]},  eta = {eta}, rho = {rho}")
print(f"  psi = {ps} = {float(ps):.4f}   Theorem D bound = {bound} = {float(bound):.4f}")
print(f"  -> Theorem D {'VIOLATED (so triangle-freeness is load-bearing)' if ps > bound else 'holds'}"
      f";  psi > 1/25 as well: {ps > F(1,25)} (no counterexample: the graph has a triangle)")

print("\n=== (2) THEOREM F: psi <= 1/25 whenever eta <= 4/25, tested in the NEW band (1/13, 4/25] ===")
suite = [("C5", (5, [(i, (i + 1) % 5) for i in range(5)])), ("Petersen", petersen()),
         ("Grotzsch", grotzsch()), ("Wagner", gamma_g(8)), ("Gamma_11", gamma_g(11)),
         ("Gamma_14", gamma_g(14)), ("N=14 extremal", g6("M?AE@bH{AYN_LgBs?")),
         ("C5[2]", blowup([2, 2, 2, 2, 2])), ("C5[3,1,2,2,1]", blowup([3, 1, 2, 2, 1]))]
rng = np.random.default_rng(20260726)
tot_band = viol_F = viol_D_in_band = 0
worst = None
for name, (n, E) in suite:
    A = adjacency(n, E)
    C5s = induced_c5s(n, E)
    for C in C5s[:8]:
        for trial in range(400):
            q = int(rng.integers(12, 40))
            a = [0] * n
            for v in C:
                a[v] = int(rng.integers(1, q))
            off = [v for v in range(n) if v not in set(C)]
            for v in off:
                if rng.random() < 0.5:
                    a[v] = int(rng.integers(0, max(2, q // 4)))
            tot = sum(a)
            if tot == 0:
                continue
            x = [F(v, tot) for v in a]
            eta, rho = eta_rho(n, E, A, C, x)
            if not (F(1, 13) < eta <= F(4, 25)):
                continue
            tot_band += 1
            ps = psi_exact(n, E, x)
            if ps > F(1, 25):
                viol_F += 1
                if worst is None or ps > worst[0]:
                    worst = (ps, name, [str(t) for t in x], eta, rho)
            if ps > (1 - rho) ** 2 / 25 + rho * eta:
                viol_D_in_band += 1
print(f"  exact instances with eta strictly inside (1/13, 4/25]: {tot_band}")
print(f"  violations of Theorem F (psi > 1/25): {viol_F}")
print(f"  violations of Theorem D's inequality in the same band: {viol_D_in_band}")
if worst:
    print(f"  worst: {worst}")

print("\n=== (3) the audit's own retraction witness ===")
y = [F(1, 6), F(1, 4), F(1, 6), F(1, 4), F(1, 6)]
print(f"  y = {[str(t) for t in y]},  sum = {sum(y)}")
prods = [y[i] * y[(i + 1) % 5] for i in range(5)]
print(f"  cyclic products y_i y_(i+1) = {[str(p) for p in prods]}")
print(f"  min over all five = {min(prods)} = {float(min(prods)):.5f}  (<= 1/25: {min(prods) <= F(1,25)})")
for drop in range(5):
    four = [prods[i] for i in range(5) if i != drop]
    if min(four) > F(1, 25):
        print(f"  dropping index {drop}: min over the other four = {min(four)} = "
              f"{float(min(four)):.5f} > 1/25  -> 'BAD_i = 0 for SOME i' is INSUFFICIENT")
        break

print("\n=== the Andrasfai profile correction, C(k-1,2) not C(k-2,2) ===")
for k in (3, 4, 5, 6):
    m = 3 * k - 1
    nn, EE = gamma_g(m)
    print(f"  And({k}) = Gamma_{m}: C(k-1,2) = {(k-1)*(k-2)//2}, C(k-2,2) = {(k-2)*(k-3)//2}")
