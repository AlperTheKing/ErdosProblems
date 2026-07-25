"""ROOT-AGENT GATE (Claude): verify the round-8 PROOF of Theorem A. Own implementation.

THEOREM A.  For every triangle-free G and every x >= 0 with sum x = 1,  Lambda(G,x) <= 1/25,
where Lambda is the fractional odd-cycle covering LP with edge weights w_uv = x_u x_v.

This is load-bearing: R3-C17 (Wagner) and the Petersen ceiling both consume it, and it had never
been gated by me. The audit returned a proof; I check the proof, not just the conclusion.

    d(v) = sum_{u in N(v)} x_u.

    LEMMA 1. If g >= 0 has sum_{v in C} g(v) >= gamma for every odd cycle C, then
             Lambda <= (1/(2 gamma)) * sum_v g(v) x_v d(v),
             witnessed by y_e := (g(u)+g(v))/(2 gamma):  each vertex of a cycle meets exactly 2 of
             its edges, so sum_{e in C} y_e = (2/(2 gamma)) sum_{v in C} g(v) >= 1.
             Cost = sum_{uv in E} x_u x_v (g(u)+g(v)) / (2 gamma) = (1/(2 gamma)) sum_v g(v) x_v d(v).

    LEMMA 2 (this is where triangle-freeness is used, and the ONLY place).
             For an odd cycle C of length L in a triangle-free graph, sum_{v in C} d(v) <= (L-1)/2.
             N(u) is independent, so N(u) cap V(C) is an independent set of the cycle C_L, hence has
             size <= floor(L/2) = (L-1)/2; double count sum_{v in C} d(v) = sum_u x_u |N(u) cap V(C)|.

    THEOREM. g = 1/d, gamma = min_C sum_{v in C} 1/d(v).  Cauchy-Schwarz and Lemma 2 give
             sum_{v in C} 1/d(v) >= L^2 / sum_{v in C} d(v) >= 2L^2/(L-1) >= 25/2 for odd L >= 5.
             Lemma 1 then gives cost = (1/(2 gamma)) sum_v x_v = 1/(2 gamma) <= 1/25.

Degenerate weights are handled by restricting to supp(x): edges leaving it have weight 0, so y_e = 1
there is free and covers every odd cycle meeting the complement; isolated vertices of the restriction
lie on no cycle and are dropped, leaving d(v) > 0 everywhere.

Checked here: (1) the arithmetic chain; (2) Lemma 2's combinatorial core, with a K4 control that
MUST violate it; (3) the constructed cover, end to end, exactly: feasible against every odd cycle and
of cost exactly 1/(2 gamma) <= 1/25; (4) the auditor's claim that Theorem A does NOT imply the
conjecture, via twice-subdivided K5.
"""
from fractions import Fraction as F
from itertools import combinations


def gamma_graph(m):
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


def adjacency(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    return A


def odd_cycles(n, E):
    idx = {(min(u, v), max(u, v)): i for i, (u, v) in enumerate(E)}
    A = adjacency(n, E)
    out = set()
    for s in range(n):
        def dfs(u, seen, el, path):
            for v in sorted(A[u]):
                if v == s and len(path) >= 3 and len(path) % 2 == 1:
                    out.add((frozenset(el + [idx[(min(u, v), max(u, v))]]), frozenset(path)))
                elif v > s and v not in seen:
                    dfs(v, seen | {v}, el + [idx[(min(u, v), max(u, v))]], path + [v])
        dfs(s, {s}, [], [s])
    return [(sorted(e), sorted(p)) for e, p in out]


print("=== (1) the arithmetic chain: 2L^2/(L-1) >= 25/2 for odd L >= 5, and increasing ===")
prev = None
ok = True
for L in range(5, 32, 2):
    val = F(2 * L * L, L - 1)
    if val < F(25, 2):
        ok = False
    if prev is not None and val <= prev:
        ok = False
    prev = val
    if L <= 11:
        print(f"    L = {L:2d}:  2L^2/(L-1) = {val} = {float(val):.4f}")
print(f"    all odd 5 <= L <= 31 satisfy >= 25/2 and strictly increase: {ok}   (equality at L=5)")

print("\n=== (2) Lemma 2's core: |N(u) cap V(C)| <= (L-1)/2, with a K4 control ===")
suite = [("C5", (5, [(i, (i + 1) % 5) for i in range(5)])), ("C7", (7, [(i, (i + 1) % 7) for i in range(7)])),
         ("Wagner", gamma_graph(8)), ("Petersen", petersen()), ("Grotzsch", grotzsch()),
         ("Gamma_11", gamma_graph(11))]
tot = viol = tight = 0
for name, (n, E) in suite:
    A = adjacency(n, E)
    for _, P in odd_cycles(n, E):
        L = len(P)
        for u in range(n):
            k = len(A[u] & set(P))
            tot += 1
            if k > (L - 1) // 2:
                viol += 1
            if k == (L - 1) // 2:
                tight += 1
print(f"    triangle-free suite: {tot} (u,C) pairs, violations = {viol}, tight = {tight}")
n4, E4 = 4, [(u, v) for u in range(4) for v in range(u + 1, 4)]
A4 = adjacency(n4, E4)
v4 = sum(1 for _, P in odd_cycles(n4, E4) for u in range(4)
         if len(A4[u] & set(P)) > (len(P) - 1) // 2)
print(f"    K4 control (has triangles): violations = {v4}  -> triangle-freeness is what is used: "
      f"{v4 > 0}")

print("\n=== (3) the constructed cover, end to end, exact rationals ===")
import numpy as np
rng = np.random.default_rng(20260726)
worst = F(0)
bad_feas = bad_cost = 0
for name, (n, E) in suite:
    A = adjacency(n, E)
    OC = odd_cycles(n, E)
    for trial in range(6):
        a = rng.integers(0, 9, size=n)
        if a.sum() == 0:
            continue
        x = [F(int(t), int(a.sum())) for t in a]
        T = [v for v in range(n) if x[v] > 0]
        d = {v: sum(x[u] for u in A[v]) for v in T}
        if any(d[v] == 0 for v in T):
            continue                                   # isolated in the restriction; dropped
        # gamma over odd cycles living inside supp(x)
        inside = [(el, P) for (el, P) in OC if all(v in T for v in P)]
        if not inside:
            continue
        g = {v: 1 / d[v] for v in T}
        gam = min(sum(g[v] for v in P) for (_, P) in inside)
        y = {}
        for i, (u, v) in enumerate(E):
            y[i] = (g[u] + g[v]) / (2 * gam) if (u in T and v in T) else F(1)
        if any(sum(y[i] for i in el) < 1 for (el, _) in OC):
            bad_feas += 1
        cost = sum(F(x[u] * x[v]) * y[i] for i, (u, v) in enumerate(E))
        pred = 1 / (2 * gam)
        if cost != pred:
            bad_cost += 1
        worst = max(worst, cost)
        if gam < F(25, 2):
            print(f"    !! gamma = {gam} < 25/2 on {name}")
print(f"    infeasible covers: {bad_feas}   cost != 1/(2 gamma): {bad_cost}   "
      f"max cost over all instances: {worst} = {float(worst):.6f}  (<= 1/25: {worst <= F(1,25)})")

print("\n=== (4) Theorem A does NOT imply the conjecture: twice-subdivided K5 ===")
print("    K5 with every edge subdivided twice: n = 5 + 2*10 = 25, m = 3*10 = 30, triangle-free,")
print("    odd girth 9.  Odd cycles correspond exactly to odd cycles of K5 (a k-cycle becomes 3k).")
print("    psi at uniform x = bip/625, and bip = min edges to delete from K5 to make it bipartite,")
print("    since deleting any one edge of a subdivision path kills that K5 edge.")
K5 = [(u, v) for u in range(5) for v in range(u + 1, 5)]
best = None
for m in range(1 << 4):
    S = (m << 1) | 1
    mono = sum(1 for (u, v) in K5 if ((S >> u) & 1) == ((S >> v) & 1))
    best = mono if best is None else min(best, mono)
psi = F(best, 625)
lam = F(30, 9 * 625)
print(f"    bip(K5) = {best}  ->  psi = {best}/625 = {psi}")
print(f"    uniform y = 1/9 on all 30 edges covers every 9-cycle: Lambda <= 30/(9*625) = {lam}")
print(f"    psi/Lambda = {psi / lam}   -> integrality gap, so Lambda <= 1/25 does NOT give psi <= 1/25")
print(f"    (and psi = {float(psi):.6f} <= 1/25 = 0.04, so this is no counterexample)")
