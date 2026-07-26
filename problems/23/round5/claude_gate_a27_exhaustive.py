"""ROOT-AGENT GATE (Claude): does my own residual-margin claim survive exhaustive enumeration?

I measured, by HEURISTIC SAMPLING, that weightings the proved toolkit cannot settle top out around
30/841 = 0.035672 on Gamma_11, an 11% margin below 1/25, and suggested that would make the residual
target NON-SHARP. I recorded it as a measurement with its limits stated. Codex now reports the
opposite: the unsettled maximum RISES with grid refinement and no epsilon is bounded away from 1/25.

That is a claim against my own work, so I check it myself rather than accept it.

METHOD. On Gamma_11, enumerate ALL integer weightings a >= 0 with sum a = q -- zero entries allowed,
which is mandatory here -- for increasing q. For each, psi * q^2 is the exact integer minimum over
all 1024 bipartitions of sum over monochromatic edges of a_u a_v. Sort by psi descending, then walk
down checking SETTLED (support C5-colourable, or D(C) = 0, or 25*eta(C) + rho(C) <= 2 for some
induced C5) until the first unsettled weighting appears: that is the EXACT max of psi over the
unsettled region at that grid. If it climbs toward 1/25 as q grows, my suggestion is dead.
"""
import sys
from fractions import Fraction as F
from itertools import combinations

import numpy as np


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


n, E = gamma_g(11)
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)
ue = np.array([e[0] for e in E])
ve = np.array([e[1] for e in E])

ncuts = 1 << (n - 1)
M = np.zeros((ncuts, len(E)), dtype=np.int32)
mm = np.arange(ncuts, dtype=np.int64)
S = (mm << 1) | 1
for k, (u, v) in enumerate(E):
    M[:, k] = (((S >> u) & 1) == ((S >> v) & 1)).astype(np.int32)
MT = np.ascontiguousarray(M.T)

C5s = [T for T in combinations(range(n), 5) if all(len(A[v] & set(T)) == 2 for v in T)]


def cycle_order(C):
    C = list(C)
    order = [C[0]]
    prev = None
    for _ in range(4):
        nxt = [w for w in A[order[-1]] if w in C and w != prev]
        prev = order[-1]
        order.append(nxt[0] if nxt[0] not in order else nxt[1])
    return order


ORD = {C: cycle_order(C) for C in C5s}


def c5_colourable(sup):
    sup = sorted(sup)
    col = {}

    def rec(i):
        if i == len(sup):
            return True
        v = sup[i]
        for c in range(5 if i else 1):
            if all((col[w] - c) % 5 in (1, 4) for w in A[v] if w in col):
                col[v] = c
                if rec(i + 1):
                    return True
                del col[v]
        return False

    return rec(0)


def settled(a, q):
    sup = {v for v in range(n) if a[v] > 0}
    if c5_colourable(sup):
        return True
    for C in C5s:
        Cs = set(C)
        D = sum(a[u] * (2 - len(A[u] & Cs)) for u in range(n))
        if D == 0:
            return True
        order = ORD[C]
        twin = set()
        for v in range(n):
            if v in Cs:
                continue
            nb = A[v] & Cs
            for i in range(5):
                if nb == {order[(i - 1) % 5], order[(i + 1) % 5]}:
                    twin.add(v)
                    break
        eta = sum(a[v] for v in range(n) if v not in Cs)
        rho = sum(a[v] for v in range(n) if v not in Cs and v not in twin)
        if 25 * eta + rho <= 2 * q:
            return True
    return False


def compositions(total, parts):
    a = [0] * parts
    a[0] = total
    while True:
        yield a
        if a[parts - 1] == total:
            return
        if a[0] > 0:
            a[0] -= 1
            a[1] += 1
        else:
            j = next(i for i in range(1, parts) if a[i] > 0)
            a[0] = a[j] - 1
            a[j] = 0
            a[j + 1] += 1


print(f"Gamma_11: |E| = {len(E)}, cuts = {ncuts}, induced pentagons = {len(C5s)}")
print(f"{'q':>4s} {'weightings':>12s} {'max psi ALL':>22s} {'max psi UNSETTLED':>24s} {'% of 1/25':>10s}")
for q in (8, 10, 12, 14):
    rows = np.fromiter((v for a in compositions(q, n) for v in a), dtype=np.int32)
    P = rows.reshape(-1, n)
    K = P.shape[0]
    best = np.empty(K, dtype=np.int32)
    CH = 100000
    for s in range(0, K, CH):
        blk = P[s:s + CH]
        prod = (blk[:, ue] * blk[:, ve]).astype(np.int32)
        best[s:s + CH] = (prod @ MT).min(axis=1)
    order = np.argsort(-best)
    top_all = F(int(best[order[0]]), q * q)
    unsettled = None
    for idx in order:
        val = F(int(best[idx]), q * q)
        if unsettled is not None and val <= unsettled:
            break
        if not settled(P[idx].tolist(), q):
            unsettled = val
            break
    pct = float(unsettled / F(1, 25) * 100) if unsettled is not None else 0.0
    print(f"{q:4d} {K:12d} {str(top_all) + ' = ' + f'{float(top_all):.6f}':>22s} "
          f"{(str(unsettled) + ' = ' + f'{float(unsettled):.6f}') if unsettled else '-':>24s} "
          f"{pct:9.2f}%")
    sys.stdout.flush()
print("\nIf the UNSETTLED column climbs toward 1/25 = 0.040000 as q grows, there is no epsilon")
print("bounded away from the target off the settled region, and my residual-margin suggestion dies.")
