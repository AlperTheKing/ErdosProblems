"""Erdos #23 -- exact counterexample hunt among blow-ups (family F4 side-search).

Lemma A (proved in the write-up):  for any graph H and integer weights a >= 0,
    bip(H[a]) = min_{S subset V(H)} sum_{uv in E(H), uv not cut by S} a_u a_v .
So the conjecture restricted to blow-ups of H reads
    25 * min_S (uncut a-weight) <= (sum_u a_u)^2   for every a.
min_S(...) is monotone under adding edges to H and is invariant under merging
twins, hence it suffices to search REDUCED MAXIMAL TRIANGLE-FREE graphs
(maximal triangle-free + twin-free); files f8_rmtf_*.g6 hold all of them up to
15 vertices (1,1,1,2,4,8,24,91,441 for n=5,8,9,10,11,12,13,14,15).

Search = steepest-ascent unit-move hill climbing with plateau walks on the
integer weight vector a (sum a = T fixed), exact int64 arithmetic throughout.
Seeds: every 5-cycle of H (weight 5 on its vertices) + random restarts.
Any printed ratio > 1 is an exact counterexample to Erdos #23.
"""
import random, glob, os, sys
from fractions import Fraction
from itertools import combinations
import numpy as np
from f1_bip import g6_decode, is_triangle_free

random.seed(23)
HERE = os.path.dirname(os.path.abspath(__file__))
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 13


def uncut_tensor(n, E):
    """T3[k] = symmetric 0/1 adjacency matrix of the edges left uncut by cut k."""
    K = 1 << (n - 1)
    T3 = np.zeros((K, n, n), dtype=np.int64)
    for k in range(K):
        S = (k << 1) | 1
        for (u, v) in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                T3[k, u, v] = 1
                T3[k, v, u] = 1
    return T3


def qvals(T3, a):
    P = T3 @ a                      # (K,n)
    q = (P * a).sum(axis=1) // 2    # (K,)
    return P, q


def climb(T3, n, a, rng, max_iter=400):
    """steepest ascent on val(a) = min_k q_k(a) with plateau walking."""
    a = a.copy()
    P, q = qvals(T3, a)
    cur = int(q.min())
    best = cur; besta = a.copy()
    plateau = 0
    for _ in range(max_iter):
        # newq[k,i,j] = q[k] + P[k,j] - P[k,i] - T3[k,i,j]   (move one unit i->j)
        newq = q[:, None, None] + P[:, None, :] - P[:, :, None] - T3
        vals = newq.min(axis=0)                      # (n,n)
        mask = (a > 0)[:, None] & ~np.eye(n, dtype=bool)
        vals = np.where(mask, vals, -1 << 60)
        m = int(vals.max())
        if m > cur:
            i, j = np.unravel_index(int(vals.argmax()), vals.shape)
            plateau = 0
        elif m == cur and plateau < 12:
            cand = np.argwhere(vals == m)
            i, j = cand[rng.randrange(len(cand))]
            plateau += 1
        else:
            break
        a[i] -= 1; a[j] += 1
        P, q = qvals(T3, a)
        cur = int(q.min())
        if cur > best:
            best = cur; besta = a.copy()
    return best, besta


def five_cycles(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    out = []
    for c in combinations(range(n), 5):
        sub = [(u, v) for u, v in combinations(c, 2) if v in adj[u]]
        if len(sub) == 5 and all(sum(1 for e in sub if x in e) == 2 for x in c):
            out.append(c)
    return out


graphs = []
for f in sorted(glob.glob(os.path.join(HERE, "f8_rmtf_*.g6"))):
    for line in open(f):
        line = line.strip()
        if line:
            graphs.append(line)
graphs = [g for g in graphs if ord(g[0]) - 63 <= NMAX]
print(f"# {len(graphs)} reduced maximal triangle-free graphs with n <= {NMAX}",
      flush=True)

rng = random.Random(2023)
best_overall = Fraction(0); arg_overall = None
for g6 in graphs:
    n, E = g6_decode(g6)
    assert is_triangle_free(n, E)
    T3 = uncut_tensor(n, E)
    best = Fraction(0); besta = None
    seeds = []
    for c in five_cycles(n, E):
        s = np.zeros(n, dtype=np.int64)
        for x in c:
            s[x] = 5
        seeds.append((25, s))
    R = 40 if n <= 12 else (25 if n == 13 else (10 if n == 14 else 4))
    for T in (25, 50, 75):
        for _ in range(R):
            s = np.zeros(n, dtype=np.int64)
            for _ in range(T):
                s[rng.randrange(n)] += 1
            seeds.append((T, s))
    for (T, s) in seeds:
        v, a = climb(T3, n, s, rng)
        r = Fraction(int(v), T * T)
        if r > best:
            best = r; besta = a.tolist()
    flag = "   *** > 1/25 : COUNTEREXAMPLE ***" if best > Fraction(1, 25) else ""
    print(f"{g6:18s} n={n:2d} m={len(E):3d}  max 25*bip(H[a])/N^2 = "
          f"{float(25*best):.6f}  a={besta}{flag}", flush=True)
    if best > best_overall:
        best_overall = best; arg_overall = (g6, besta)
print("MAX over the searched RMTF graphs: 25*bip(H[a])/N^2 =", 25 * best_overall,
      "=", float(25 * best_overall), "at", arg_overall)
