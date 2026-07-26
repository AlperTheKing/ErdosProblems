"""ROOT-AGENT (Claude): piece (i) only ever needed the MINIMUM-DEGREE range, which excludes every
subdivision witness for free.

R3-C45 killed the c*W family using twice-subdivided K_n. But those witnesses have degree 2 at every
subdivided vertex, and accepted base (6) already restricts a minimal counterexample to

        delta(G) > (4N - 2)/25   ~   0.16 N,

by  bip(G) <= bip(G-v) + floor(d(v)/2):  if G is a smallest counterexample then
N^2/25 < bip(G) <= (N-1)^2/25 + d(v)/2 for every v, giving d(v) > (4N-2)/25.

So piece (i) never needed to hold for ALL pentagon-free triangle-free graphs -- only for those that
could be minimal counterexamples, i.e. with delta > (4N-2)/25. Every subdivision witness has
delta = 2 and is excluded the moment N > 13.

This checks: (1) that the subdivision witnesses really are excluded; (2) what the pentagon-free
graphs in the surviving degree range actually look like on n <= 11, and what psi they reach.

Also relevant, and worth stating: for odd girth >= 7 the extremal non-bipartite objects are C7
blow-ups with delta = 2n/7 = 0.2857n, so the surviving band for piece (i) is roughly
0.16 N < delta <= 0.2857 N -- narrower than the band for the full conjecture.
"""
import os
from fractions import Fraction as F

import numpy as np
from scipy.optimize import linprog
from itertools import combinations


def bip_Kn(n):
    return n * (n - 1) // 2 - (n * n) // 4


print("=== (1) are the R3-C45 subdivision witnesses excluded by base (6)? ===")
print(f"{'n':>5s} {'N':>8s} {'delta':>6s} {'(4N-2)/25':>11s} {'excluded?':>10s}")
for n in (5, 7, 12, 28, 100):
    m = n * (n - 1) // 2
    N = n + 2 * m
    thr = F(4 * N - 2, 25)
    print(f"{n:5d} {N:8d} {2:6d} {float(thr):11.2f} "
          f"{('YES' if 2 <= thr else 'no'):>10s}")
print("  every twice-subdivided graph has delta = 2 at its subdivision vertices, so all of them")
print("  fall outside the minimal-counterexample range as soon as N > 13.")


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


def psi_max(n, E, starts=12, seed=3):
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
            if len(X0) >= 5:
                break
    X0.append(np.ones(n) / n)
    rng = np.random.default_rng(seed)
    for _ in range(starts):
        X0.append(rng.dirichlet(np.ones(n)))
    best = 0.0
    for x in X0:
        for _ in range(20):
            q = M @ (x[ue] * x[ve])
            b = q.min()
            act = np.where(q <= b + 1e-9)[0][:120]
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
                         b_ub=np.zeros(len(act)), A_eq=Aeq, b_eq=[0.0], bounds=bnd, method='highs')
            if not r2.success or -r2.fun <= 1e-11:
                break
            d = r2.x[:n]
            cand = [(b, x)]
            for t in (0.3, 0.1, 0.03):
                y = np.maximum(x + t * d, 0)
                if y.sum() <= 0:
                    continue
                y /= y.sum()
                cand.append(((M @ (y[ue] * y[ve])).min(), y))
            v2, x2 = max(cand, key=lambda p: p[0])
            if v2 <= b + 1e-13:
                break
            x = x2
        best = max(best, (M @ (x[ue] * x[ve])).min())
    return best


print("\n=== (2) pentagon-free graphs in the surviving degree range, n <= 11 ===")
src = None
for cand in ("../round7/audit_tf11.g6", "../round7/tf11.g6"):
    if os.path.exists(cand):
        src = cand
        break
kept = surv = 0
best_all = (0.0, None)
best_surv = (0.0, None)
for s, n, E in g6iter(src):
    if not E:
        continue
    if has_cycle_len(n, E, 3) or has_cycle_len(n, E, 5) or bipartite(n, E):
        continue
    kept += 1
    deg = [0] * n
    for u, v in E:
        deg[u] += 1
        deg[v] += 1
    delta = min(deg)
    v = psi_max(n, E)
    if v > best_all[0]:
        best_all = (v, s)
    if F(delta) > F(4 * n - 2, 25):
        surv += 1
        if v > best_surv[0]:
            best_surv = (v, s)
print(f"  pentagon-free non-bipartite graphs: {kept}")
print(f"  of those with delta > (4n-2)/25 (minimal-counterexample range): {surv}")
print(f"  max psi over ALL of them:            {best_all[0]:.8f} on {best_all[1]}")
print(f"  max psi over the SURVIVING range:    {best_surv[0]:.8f} on {best_surv[1]}")
print(f"  1/49 = {1/49:.8f},  1/25 = {1/25:.8f}")
print("\nPiece (i) only has to hold in the surviving range, so every subdivision-type witness --")
print("which is what killed the c*W family -- is irrelevant to it.")
