"""ROOT-AGENT GATE (Claude): is Codex's R10 bridge really Vega-free at delta > 5N/14?

Codex's Round 10 route claims the unconditional theorem "bip(G) <= N^2/25 for triangle-free G with
delta(G) > 5N/14" reduces, via Theorem R3 at t = 5, to Gamma_1..Gamma_4 with "no Vega statement
needed". By Brandt-Thomasse Corollary 4.1 the twin-free maximal triangle-free weighted graphs with
delta > 1/3 are the Gamma_i AND the 4-chromatic VEGA graphs, so the Vega branch must be discharged,
not ignored. I check that here rather than take it on trust.

The weighted minimum degree of a pattern is  delta*(G) = max over omega on the simplex of
min_v omega(N(v)).  A Vega graph is excluded from the t = 5 list exactly when delta*(G) <= 5/14.

EXACT CERTIFICATE, no LP solver trusted. By LP duality, for ANY probability vector p on V,
        delta*(G) = max_omega min_v omega(N(v)) <= max_u p(N(u)),
because min_v omega(N(v)) <= sum_v p_v omega(N(v)) = sum_u omega_u p(N(u)) <= max_u p(N(u)).
So exhibiting a single rational p with max_u p(N(u)) < 5/14 PROVES delta* < 5/14 exactly. I get p
from a float LP, rationalise it, and then verify the bound in exact arithmetic.

Vega graphs, verbatim from Brandt-Thomasse p.4 (as quoted in round3/G7.md): for i >= 2 take Gamma_i
on {1..3i-1}, add an edge xy and an induced 6-cycle (a,v,c,u,b,w); x is joined to a,b,c and y to
u,v,w; the Gamma_i-neighbours of a and u are {1..i}, of b and v are {i+1..2i}, of c and w are
{2i+1..3i-1}. That graph on 3i+7 vertices is Upsilon_i; the others are Upsilon_i - {y},
Upsilon_i - {2i} (both 3i+6) and Upsilon_i - {y,2i} (3i+5). Upsilon_2 - {y,4} is the Grotzsch graph.
"""
from fractions import Fraction as F

import numpy as np
from scipy.optimize import linprog


def gamma_i(i):
    """Gamma_i on {1..3i-1}: j ~ k iff circular distance in Z_{3i-1} is at least i"""
    m = 3 * i - 1
    V = list(range(1, m + 1))
    E = []
    for a in range(1, m + 1):
        for b in range(a + 1, m + 1):
            d = min((a - b) % m, (b - a) % m)
            if d >= i:
                E.append((a, b))
    return V, E


def upsilon(i):
    V, E = gamma_i(i)
    x, y, a, v, c, u, b, w = ('x', 'y', 'a', 'v', 'c', 'u', 'b', 'w')
    V = V + [x, y, a, v, c, u, b, w]
    E = list(E) + [(x, y)]
    # induced 6-cycle (a,v,c,u,b,w)
    cyc = [a, v, c, u, b, w]
    for t in range(6):
        E.append((cyc[t], cyc[(t + 1) % 6]))
    for t in (a, b, c):
        E.append((x, t))
    for t in (u, v, w):
        E.append((y, t))
    A1 = list(range(1, i + 1))
    A2 = list(range(i + 1, 2 * i + 1))
    A3 = list(range(2 * i + 1, 3 * i))
    for t in A1:
        E += [(a, t), (u, t)]
    for t in A2:
        E += [(b, t), (v, t)]
    for t in A3:
        E += [(c, t), (w, t)]
    return V, [tuple(sorted(e, key=str)) for e in E]


def induced(V, E, drop):
    keep = [z for z in V if z not in drop]
    ks = set(keep)
    return keep, [e for e in E if e[0] in ks and e[1] in ks]


def delta_star(V, E):
    """max_omega min_v omega(N(v)); returns (float value, exact rational dual bound)"""
    idx = {z: k for k, z in enumerate(V)}
    n = len(V)
    N = [[] for _ in range(n)]
    for p, q in E:
        N[idx[p]].append(idx[q])
        N[idx[q]].append(idx[p])
    # primal: max t s.t. sum_{u in N(v)} omega_u >= t for all v, sum omega = 1, omega >= 0
    c = np.zeros(n + 1)
    c[-1] = -1.0
    Aub = np.zeros((n, n + 1))
    for v in range(n):
        for u in N[v]:
            Aub[v, u] = -1.0
        Aub[v, -1] = 1.0
    Aeq = np.zeros((1, n + 1))
    Aeq[0, :n] = 1.0
    r = linprog(c, A_ub=Aub, b_ub=np.zeros(n), A_eq=Aeq, b_eq=[1.0],
                bounds=[(0, None)] * n + [(None, None)], method='highs')
    val = -r.fun if r.success else float('nan')
    # dual certificate: a probability p with max_u p(N(u)) small
    p = None
    if r.success and r.ineqlin is not None:
        d = np.maximum(np.array(r.ineqlin.marginals) * -1.0, 0.0)
        if d.sum() > 0:
            p = d / d.sum()
    best = None
    if p is not None:
        for D in (12, 24, 35, 60, 70, 120, 210, 420, 840, 2520, 27720):
            pr = [F(int(round(t * D)), D) for t in p]
            s = sum(pr)
            if s == 0:
                continue
            pr = [t / s for t in pr]
            m = max(sum(pr[u] for u in N[z]) for z in range(n))
            if best is None or m < best:
                best = m
    return val, best


print(f"{'graph':22s} {'|V|':>4s} {'delta* (LP)':>12s} {'exact dual bound':>18s} "
      f"{'< 5/14 = 0.357143?':>20s}")
allok = True
for i in (2, 3, 4):
    V, E = upsilon(i)
    fams = [(f"Upsilon_{i}", []), (f"Upsilon_{i}-y", ['y']), (f"Upsilon_{i}-{{{2*i}}}", [2 * i]),
            (f"Upsilon_{i}-{{y,{2*i}}}", ['y', 2 * i])]
    for name, drop in fams:
        VV, EE = induced(V, E, drop)
        val, dual = delta_star(VV, EE)
        ok = dual is not None and dual < F(5, 14)
        allok = allok and ok
        print(f"{name:22s} {len(VV):4d} {val:12.6f} "
              f"{(str(dual) + ' = ' + f'{float(dual):.6f}') if dual else '-':>18s} "
              f"{('YES, excluded' if ok else 'NO'):>20s}")
print()
print(f"every Vega graph tested has delta* < 5/14, certified exactly: {allok}")
print("Brandt-Thomasse give delta_reg(Upsilon_i) = (9i-6)/(27i-19), maximal at i = 2:")
print(f"  12/35 = {float(F(12,35)):.6f} < 5/14 = {float(F(5,14)):.6f}, and it DECREASES to 1/3,")
print("so no Vega graph can meet delta > 5/14 and the t = 5 list is Gamma_1..Gamma_4 only.")
print("Petersen is not in that list at all, so the bridge nowhere routes through Guenin/Petersen.")
