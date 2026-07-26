"""ROOT-AGENT (Claude): does the c*W route REVIVE once base (6)'s degree restriction is applied?

R3-C45 killed psi <= c*W at odd girth >= 7 using twice-subdivided K_n, which forces c >= 1/6 and
hence a useless 1/24 > 1/25. But every one of those witnesses has delta = 2, and accepted base (6)
already confines a minimal counterexample to delta > (4N-2)/25. So they are irrelevant to piece (i),
which only has to hold in that range -- verified in claude_piece_i_mindegree.py, where all
subdivision witnesses are excluded for N > 13 while C7 itself survives.

QUESTION: over pentagon-free graphs with delta > (4n-2)/25, is max_x psi/W <= 4/25?

If yes, the route revives with a restriction that costs NOTHING, since base (6) is accepted:

        psi <= (4/25) W  on the surviving range,  W <= 1/4 (Motzkin-Straus)
        ==>  psi <= 1/25  for every pentagon-free graph that could be a minimal counterexample
        ==>  piece (i) closed.

C7 sits in the surviving range (delta = 2 > (28-2)/25 = 1.04) and gives psi/W = 1/7 = 0.1428 < 0.16,
so the bound is not immediately tight there. Measured below over the whole surviving corpus.
"""
import os
from fractions import Fraction as F
from itertools import combinations

import numpy as np


def g6iter(path):
    for line in open(path):
        s = line.strip()
        if not s:
            continue
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


def max_ratio(n, E, starts=16, seed=5):
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
            if len(X0) >= 6:
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
            r = (M @ p).min() / W
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
print(f"corpus {src};  target 4/25 = {4/25:.8f}")
surv = 0
worst = (0.0, None)
above = 0
for s, n, E in g6iter(src):
    if not E:
        continue
    if has_cycle_len(n, E, 3) or has_cycle_len(n, E, 5) or bipartite(n, E):
        continue
    deg = [0] * n
    for u, v in E:
        deg[u] += 1
        deg[v] += 1
    if not (F(min(deg)) > F(4 * n - 2, 25)):
        continue
    surv += 1
    r, bx = max_ratio(n, E)
    if r > worst[0]:
        worst = (r, s)
    if r > 4 / 25 + 1e-9:
        above += 1
        if above <= 3:
            print(f"*** ABOVE 4/25: {s}  psi/W ~ {r:.8f}", flush=True)
print(f"\npentagon-free, non-bipartite, delta > (4n-2)/25:  {surv} graphs")
print(f"max psi/W over that range: {worst[0]:.8f} on {worst[1]}")
print(f"target 4/25 = {4/25:.8f};  exceeding it: {above}")
if above == 0:
    print(f"headroom {(4/25 - worst[0])/(4/25)*100:.1f}%  -- the c*W route REVIVES under base (6)")
