"""ROOT-AGENT (Claude): sweep the PENTAGON-FREE triangle-free graphs -- an unexplored region.

Two purposes at once.

(1) TEST piece (i) of the R3-C41 reduction: every pentagon-free triangle-free G has
    max_x psi <= 1/25. The W/g_odd route to it died at odd girth 9 (R3-C42), so I want to know how
    much slack actually exists. Conjecturally these graphs top out at 1/49 (C7), leaving ~51% slack,
    which would be a very different target from the sharp ones this campaign keeps losing to.

(2) COUNTEREXAMPLE HUNT in a genuinely unexplored region. Every sweep so far targeted MAXIMAL
    triangle-free patterns, and those almost always contain an induced C5 -- indeed the plateau says
    any graph with a C5 already reaches exactly 1/25. Pentagon-free graphs are the complementary
    region and have never been swept here. If the conjecture fails anywhere, a region nobody has
    looked at deserves a look.

A triangle-free graph with no C5 is either bipartite (psi = 0, trivial) or has odd girth >= 7. Only
the latter are interesting, and they are rare, so the sweep is cheap.

OPTIMISER DISCIPLINE: for odd girth 7 the mandatory explicit candidate is weight 1/7 on an induced
C7, value 1/49; any reported maximum below that on a graph containing a C7 voids the run.
"""
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
        if n == 63:
            n = (b[1] << 12) | (b[2] << 6) | b[3]
            i = 4
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
    found = [False]

    def dfs(start, u, seen, depth):
        if found[0]:
            return
        if depth == L:
            if start in A[u]:
                found[0] = True
            return
        for v in A[u]:
            if v > start and v not in seen:
                dfs(start, v, seen | {v}, depth + 1)

    for s in range(n):
        dfs(s, s, {s}, 1)
        if found[0]:
            return True
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


def psi_max(n, E, starts=14, seed=7):
    """validated ascent: mandatory C7 starts, LP ascent over active cuts"""
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
    best = 0.0
    bx = None
    for x in X0:
        for _ in range(24):
            q = M @ (x[ue] * x[ve])
            b = q.min()
            act = np.where(q <= b + 1e-9)[0][:150]
            G = np.zeros((len(act), n))
            for r, s2 in enumerate(act):
                mono = M[s2].astype(bool)
                np.add.at(G[r], ue[mono], x[ve[mono]])
                np.add.at(G[r], ve[mono], x[ue[mono]])
            c = np.zeros(n + 1)
            c[-1] = -1.0
            Aeq = np.zeros((1, n + 1))
            Aeq[0, :n] = 1.0
            bnd = [(0.0 if x[i] <= 1e-12 else -1.0, 1.0) for i in range(n)] + [(None, 1.0)]
            r2 = linprog(c, A_ub=np.hstack([-G, np.ones((len(act), 1))]),
                         b_ub=np.zeros(len(act)), A_eq=Aeq, b_eq=[0.0], bounds=bnd,
                         method='highs')
            if not r2.success or -r2.fun <= 1e-11:
                break
            d = r2.x[:n]
            cand = [(b, x)]
            for t in (0.3, 0.15, 0.05, 0.02, 0.005):
                y = np.maximum(x + t * d, 0)
                if y.sum() <= 0:
                    continue
                y = y / y.sum()
                cand.append(((M @ (y[ue] * y[ve])).min(), y))
            v2, x2 = max(cand, key=lambda p: p[0])
            if v2 <= b + 1e-13:
                break
            x = x2
        val = (M @ (x[ue] * x[ve])).min()
        if val > best:
            best, bx = val, x
    return best, bx


import os

src = None
for cand in ("../round7/audit_tf11.g6", "../round7/tf11.g6", "../round7/audit_tf10.g6",
             "../round7/tf10.g6"):
    if os.path.exists(cand):
        src = cand
        break
print(f"source corpus: {src}")
tot = kept = 0
best = (0.0, None)
voids = 0
for s, n, E in g6iter(src):
    tot += 1
    if not E:
        continue
    if has_cycle_len(n, E, 3) or has_cycle_len(n, E, 5):
        continue
    if bipartite(n, E):
        continue
    kept += 1
    v, bx = psi_max(n, E)
    hasC7 = has_cycle_len(n, E, 7)
    if hasC7 and v < 1.0 / 49 - 1e-9:
        voids += 1
    if v > best[0]:
        best = (v, s)
    if v > 0.04 + 1e-9:
        print(f"*** ABOVE 1/25: {s}  psi ~ {v:.8f}", flush=True)
print(f"\nscanned {tot} triangle-free graphs; PENTAGON-FREE non-bipartite: {kept}")
print(f"max psi over that region: {best[0]:.8f} on {best[1]}")
print(f"  1/49 = {1/49:.8f}   1/25 = {1/25:.8f}")
print(f"  optimiser voids (below the C7 floor on a graph containing C7): {voids}")
print(f"  slack to the target: {(0.04 - best[0]) / 0.04 * 100:.1f}%")
