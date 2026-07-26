"""ROOT-AGENT (Claude): test the restricted c*W route on the odd-girth-7 ANDRASFAI ANALOGUES.

R3-C46 left the route unrefuted but untested where it matters: pentagon-free graphs with
delta > 0.16 N at LARGE N. The n <= 11 corpus does not exercise the restriction at all.

The natural family is the circular cliques K_{p/q} -- vertices Z_p, i ~ j iff circdist(i,j) >= q.
And(k) = K_{(3k-1)/k} has odd girth 5 and is the level-5 family; the level-7 family is the
p/q in [7/3, 5/2) range, whose members have odd girth 7. These are exactly the graphs that are
pentagon-free AND dense enough to sit inside the minimal-counterexample range, so they are where the
restricted route lives or dies.

C7 = K_{7/3} is the smallest. Larger members have MORE vertices and HIGHER degree ratio, so they test
the restriction properly rather than vacuously.

Reported per graph: odd girth (must be 7), delta/N (must exceed 0.16 to be in range), max psi/W over
weightings, and max psi. Anything with psi/W > 4/25 kills the restricted route; anything with
psi > 1/25 is a COUNTEREXAMPLE to the conjecture itself and outranks everything.
"""
import sys
from fractions import Fraction as F
from itertools import combinations

import numpy as np


def circ_clique(p, q):
    E = [(u, v) for u in range(p) for v in range(u + 1, p)
         if min((u - v) % p, (v - u) % p) >= q]
    return p, E


def odd_girth(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    best = None
    for L in range(3, n + 1, 2):
        for s in range(n):
            stack = [(s, {s}, 1)]
            while stack:
                u, seen, d = stack.pop()
                if d == L:
                    if s in A[u]:
                        return L
                    continue
                for v in A[u]:
                    if v > s and v not in seen:
                        stack.append((v, seen | {v}, d + 1))
    return best


def analyse(p, q, starts=18, seed=13):
    n, E = circ_clique(p, q)
    if not E:
        return None
    deg = [0] * n
    for u, v in E:
        deg[u] += 1
        deg[v] += 1
    delta = min(deg)
    og = odd_girth(n, E)
    ncuts = 1 << (n - 1)
    if ncuts > (1 << 22):
        return (n, len(E), og, delta, None, None, "too large for exact cut enumeration")
    ue = np.array([e[0] for e in E])
    ve = np.array([e[1] for e in E])
    M = np.zeros((ncuts, len(E)), dtype=np.int8)
    mm = np.arange(ncuts, dtype=np.int64)
    S = (mm << 1) | 1
    for k, (u, v) in enumerate(E):
        M[:, k] = (((S >> u) & 1) == ((S >> v) & 1))
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
    bestr, bestpsi = 0.0, 0.0
    for x in X0:
        for _ in range(45):
            pr = x[ue] * x[ve]
            W = pr.sum()
            if W <= 0:
                break
            r = (M @ pr).min() / W
            improved = False
            for i in range(n):
                for step in (0.06, 0.02, 0.008):
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
        pr = x[ue] * x[ve]
        W = pr.sum()
        if W > 0:
            bestr = max(bestr, (M @ pr).min() / W)
        bestpsi = max(bestpsi, (M @ pr).min())
    return (n, len(E), og, delta, bestr, bestpsi, "")


print("odd-girth-7 circular cliques K_{p/q}, p/q in [7/3, 5/2)")
print(f"{'p/q':>8s} {'N':>4s} {'|E|':>5s} {'odd g':>6s} {'delta':>6s} {'delta/N':>8s} "
      f"{'in range?':>10s} {'max psi/W':>11s} {'max psi':>10s}")
cands = []
for q in range(3, 12):
    for p in range(2 * q, 3 * q):
        r = F(p, q)
        if F(7, 3) <= r < F(5, 2):
            cands.append((p, q))
seen = set()
for p, q in cands:
    key = F(p, q)
    if key in seen:
        continue
    seen.add(key)
    out = analyse(p, q)
    if out is None:
        continue
    n, m, og, delta, r, psi, note = out
    inr = F(delta) > F(4 * n - 2, 25)
    if note:
        print(f"{str(F(p,q)):>8s} {n:4d} {m:5d} {str(og):>6s} {delta:6d} "
              f"{delta/n:8.4f} {str(inr):>10s} {note}")
        continue
    flag = ""
    if r > 4 / 25 + 1e-9:
        flag = "  *** psi/W ABOVE 4/25 -- restricted route DIES"
    if psi > 0.04 + 1e-9:
        flag += "  *** psi ABOVE 1/25 -- COUNTEREXAMPLE"
    print(f"{str(F(p,q)):>8s} {n:4d} {m:5d} {str(og):>6s} {delta:6d} {delta/n:8.4f} "
          f"{str(inr):>10s} {r:11.8f} {psi:10.8f}{flag}")
    sys.stdout.flush()
print(f"\n4/25 = {4/25:.8f};  1/7 = {1/7:.8f};  1/25 = {1/25:.8f};  1/49 = {1/49:.8f}")
