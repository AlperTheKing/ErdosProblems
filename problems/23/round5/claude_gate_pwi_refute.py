"""ROOT-AGENT GATE (Claude): is product-weight integrality (PWI) merely conjecture-strength, or FALSE?

R3C19_ANDRASFAI4_RESOLVED.md section 6 classified

    PWI:  for every triangle-free H and every x >= 0,  tau_{w(x)}(H) = tau*_{w(x)}(H),  w(x)_uv = x_u x_v

as BLOCKED, on the grounds that PWI + Theorem A implies the conjecture.  But registry entry A5
already records an integrality gap on an N = 14 extremal graph (bip = 7 vs tau* = 32/5), and UNIFORM
weights are a product weight (x = all-ones).  If that is right, PWI is not blocked but REFUTED, and
the classification must say so.

Rather than cite A5 second hand I look for my own witness: exact tau (minimum over all cuts, integer
arithmetic) versus an exact fractional cover for named triangle-free graphs at uniform weight.  A
rational cover y with cost < tau, feasible against EVERY odd cycle, refutes PWI outright.
"""
from fractions import Fraction as F
from itertools import combinations

import numpy as np
from scipy.optimize import linprog


def petersen():
    outer = [(i, (i + 1) % 5) for i in range(5)]
    spokes = [(i, i + 5) for i in range(5)]
    inner = [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return 10, outer + spokes + inner


def grotzsch():
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E += [(5 + i, (i + 1) % 5), (5 + i, (i + 4) % 5), (10, 5 + i)]
    return 11, E


def c5_blowup(a):
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


def gamma(n):
    return n, [(u, v) for u in range(n) for v in range(u + 1, n)
               if 3 * min((u - v) % n, (v - u) % n) > n]


def cube4():
    """the 4-cube Q4: bipartite, so tau = 0 -- a control that must show no gap"""
    E = [(u, u ^ (1 << b)) for u in range(16) for b in range(4) if u < (u ^ (1 << b))]
    return 16, E


def analyse(name, n, E):
    E = sorted({tuple(sorted(e)) for e in E})
    idx = {e: i for i, e in enumerate(E)}
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    tri = any(len(A[u] & A[v]) for u, v in E)
    if tri:
        print(f"{name}: NOT triangle-free, skipped")
        return
    tau = None
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        s = sum(1 for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        if tau is None or s < tau:
            tau = s
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
    if not odd:
        print(f"{name}: n={n} |E|={len(E)} bipartite, tau={tau}, no odd cycles")
        return
    Aub = np.zeros((len(odd), len(E)))
    for k, c in enumerate(odd):
        for i in c:
            Aub[k, i] = -1.0
    res = linprog(np.ones(len(E)), A_ub=Aub, b_ub=-np.ones(len(odd)),
                  bounds=[(0, None)] * len(E), method='highs')
    line = f"{name}: n={n} |E|={len(E)} odd cycles={len(odd)}  tau={tau}  tau*~{res.fun:.6f}"
    if res.success and res.fun < tau - 1e-7:
        for D in (2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 20, 24, 30, 36, 48, 60):
            y = [F(int(round(t * D)), D) for t in res.x]
            if any(t < 0 for t in y):
                continue
            if all(sum(y[i] for i in c) >= 1 for c in odd):
                cost = sum(y)
                if cost < tau:
                    line += f"   EXACT GAP: cover cost {cost} < {tau} (denominator 1/{D})"
                    break
        else:
            line += "   numeric gap, no small-denominator exact cover"
    else:
        line += "   no gap"
    print(line)


if __name__ == '__main__':
    analyse("C5", 5, [(i, (i + 1) % 5) for i in range(5)])
    analyse("C5[2]", *c5_blowup([2, 2, 2, 2, 2]))
    analyse("C5[3,2,2,2,2]", *c5_blowup([3, 2, 2, 2, 2]))
    analyse("Petersen", *petersen())
    analyse("Grotzsch", *grotzsch())
    analyse("Wagner=And(3)", *gamma(8))
    analyse("And(4)=Gamma_11", *gamma(11))
    analyse("Gamma_10", *gamma(10))
    analyse("Q4 (bipartite control)", *cube4())
