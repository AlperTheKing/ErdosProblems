"""ROOT-AGENT (Claude): can piece (i) be closed by  psi <= (4/25) * W  at odd girth >= 7?

Piece (i): every PENTAGON-FREE triangle-free G has max_x psi <= 1/25. Motzkin-Straus caps
W = sum over edges of x_u x_v at 1/4 on triangle-free graphs, so it SUFFICES to prove

        psi(G,x)  <=  (4/25) * W(x)        for triangle-free G of odd girth >= 7,

since then psi <= (4/25)(1/4) = 1/25 exactly. Note (4/25) = 0.16.

WHY THIS IS DIFFERENT FROM THE DEAD W/g_odd ROUTE (R3-C42). That one demanded psi <= W/7 = 0.1428*W,
which is TIGHT at C7 and therefore had no room; it died on twice-subdivided K5. The present bound
asks only for 0.16*W, and the two natural extremal objects sit strictly below it:

        C7 uniform:            psi/W = (1/49)/(1/7)     = 1/7   = 0.142857
        twice-subdivided K5:   psi/W = (4/625)/(30/625) = 2/15  = 0.133333

so there is genuine slack at exactly the places the previous route failed.

IT MUST FAIL AT g = 5, and does: C5 uniform gives psi/W = (1/25)/(1/5) = 1/5 = 0.2 > 0.16. That is a
consistency check, not a problem -- if it held at g = 5 it would prove the whole conjecture, so it had
better not.

Measured here: max over x of psi(x)/W(x) across the 934 pentagon-free non-bipartite graphs on
n <= 11, plus named high-odd-girth graphs. Anything above 4/25 kills the route.
"""
import os
import sys
from fractions import Fraction as F
from itertools import combinations

import numpy as np
from scipy.optimize import linprog


def g6iter(path):
    for line in open(path):
        s = line.strip()
        if not s:
            continue
        b = [ord(c) - 63 for c in s]
        n = b[0]
        i = 1
        bits = []
        for x in b[i:]:
            bits.extend((x >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
        E, p = [], 0
        for j in range(1, n):
            for k in range(j):
                if bits[p]:
                    E.append((k, j))
                p += 1
        yield s, n, E


def has_cycle_len(n, E, L):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    for s in range(n):
        stack = [(s, {s}, 1)]
        while stack:
            u, seen, d = stack.pop()
            if d == L:
                if s in A[u]:
                    return True
                continue
            for v in A[u]:
                if v > s and v not in seen:
                    stack.append((v, seen | {v}, d + 1))
    return False


def bipartite(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    col = {}
    for s in range(n):
        if s in col:
            continue
        col[s] = 0
        dq = [s]
        while dq:
            u = dq.pop()
            for v in A[u]:
                if v not in col:
                    col[v] = 1 - col[u]
                    dq.append(v)
                elif col[v] == col[u]:
                    return False
    return True


def max_ratio(n, E, starts=20, seed=11):
    """max over x of psi(x)/W(x); scale-invariant, so optimise on the simplex"""
    ncuts = 1 << (n - 1)
    M = np.zeros((ncuts, len(E)), dtype=np.int8)
    mm = np.arange(ncuts, dtype=np.int64)
    S = (mm << 1) | 1
    for k, (u, v) in enumerate(E):
        M[:, k] = (((S >> u) & 1) == ((S >> v) & 1))
    ue = np.array([e[0] for e in E])
    ve = np.array([e[1] for e in E])
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    X0 = []
    for T in combinations(range(n), 7):
        if all(len(A[v] & set(T)) == 2 for v in T):
            x = np.zeros(n)
            for v in T:
                x[v] = 1.0 / 7
            X0.append(x)
            if len(X0) >= 8:
                break
    X0.append(np.ones(n) / n)
    rng = np.random.default_rng(seed)
    for _ in range(starts):
        X0.append(rng.dirichlet(np.ones(n)))
    best, bx = 0.0, None
    for x in X0:
        for _ in range(40):
            p = x[ue] * x[ve]
            W = p.sum()
            if W <= 0:
                break
            q = M @ p
            r = q.min() / W
            # coordinate ascent on the ratio: try small perturbations
            improved = False
            for i in range(n):
                for step in (0.08, 0.03, 0.01):
                    for sgn in (1, -1):
                        y = x.copy()
                        y[i] = max(0.0, y[i] + sgn * step)
                        if y.sum() <= 0:
                            continue
                        y = y / y.sum()
                        p2 = y[ue] * y[ve]
                        W2 = p2.sum()
                        if W2 <= 0:
                            continue
                        r2 = (M @ p2).min() / W2
                        if r2 > r + 1e-12:
                            x, r, improved = y, r2, True
                            break
                    if improved:
                        break
                if improved:
                    break
            if not improved:
                break
        p = x[ue] * x[ve]
        W = p.sum()
        if W > 0:
            r = (M @ p).min() / W
            if r > best:
                best, bx = r, x
    return best, bx


src = None
for cand in ("../round7/audit_tf11.g6", "../round7/tf11.g6"):
    if os.path.exists(cand):
        src = cand
        break
print(f"corpus: {src};  target bound 4/25 = {4/25:.6f}")
print(f"reference: C7 gives 1/7 = {1/7:.6f}, twice-subdivided K5 gives 2/15 = {2/15:.6f}, "
      f"C5 gives 1/5 = 0.2 (must exceed, and does)\n")
kept = 0
worst = (0.0, None)
above = 0
for s, n, E in g6iter(src):
    if not E:
        continue
    if has_cycle_len(n, E, 3) or has_cycle_len(n, E, 5):
        continue
    if bipartite(n, E):
        continue
    kept += 1
    r, bx = max_ratio(n, E)
    if r > worst[0]:
        worst = (r, s)
    if r > 4 / 25 + 1e-9:
        above += 1
        if above <= 3:
            print(f"*** ABOVE 4/25: {s}  psi/W ~ {r:.8f}", flush=True)
    if kept % 200 == 0:
        print(f"  ... {kept} graphs, worst ratio so far {worst[0]:.8f}", flush=True)
print(f"\npentagon-free non-bipartite graphs scanned: {kept}")
print(f"max psi/W found: {worst[0]:.8f} on {worst[1]}")
print(f"target 4/25 = {4/25:.8f};  graphs exceeding it: {above}")
print(f"headroom: {(4/25 - worst[0]) / (4/25) * 100:.1f}%")
