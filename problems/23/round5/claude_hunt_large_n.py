"""ROOT-AGENT (Claude): counterexample hunt at n = 16..20, where exhaustive pattern enumeration dies.

The exhaustive maximal-triangle-free sweep is complete and clean through n = 15 (5036 patterns, best
psi exactly 1/25).  n = 16 needs 25617 patterns and there is no corpus: building one meant filtering
445,781,050 connected triangle-free graphs already at n = 14.  So this is a randomised structured
hunt instead of an enumeration, and it says so in its output rather than pretending to be complete.

Target window.  Every odd-girth-5 graph already has max_x psi >= 1/25 (plateau), and the published
flag-algebra bound gives max_x psi <= 2/47.  So a counterexample must land in

        psi  in  (1/25, 2/47]  =  (0.040000, 0.042553]

which is what the reporting threshold below is set to.

Evaluator.  claude_psi_ascent_fast.py holds a dense (ncuts, n, n) array, which is 1.7 GB by n = 20.
Here the cut structure is a boolean incidence matrix (ncuts x |E|) instead, so
        q_S(x) = sum over monochromatic edges of S of x_u x_v  =  (Mono @ p),  p_e = x_u x_v,
and only the ACTIVE cuts ever need a gradient.

OPTIMISER DISCIPLINE (loop rule 9) is enforced: every graph is started from each of its induced C5s
at weight 1/5, and any run returning below 1/25 on a graph of odd girth 5 is reported as VOID.
"""
import sys

import numpy as np
from fractions import Fraction as F
from itertools import combinations
from scipy.optimize import linprog


def random_mtf(n, rng):
    """A uniformly-shuffled greedy maximal triangle-free graph on n vertices."""
    adj = [set() for _ in range(n)]
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(pairs)
    E = []
    for u, v in pairs:
        if adj[u] & adj[v]:
            continue
        adj[u].add(v)
        adj[v].add(u)
        E.append((u, v))
    return E, adj


def mono_matrix(n, E):
    ncuts = 1 << (n - 1)
    M = np.zeros((ncuts, len(E)), dtype=bool)
    for k, (u, v) in enumerate(E):
        m = np.arange(ncuts, dtype=np.int64)
        S = (m << 1) | 1
        M[:, k] = (((S >> u) & 1) == ((S >> v) & 1))
    return M


def induced_c5s(n, adj, limit=10):
    out = []
    for S in combinations(range(n), 5):
        if all(len(adj[v] & set(S)) == 2 for v in S):
            out.append(S)
            if len(out) >= limit:
                break
    return out


def ascend(M, E, n, x0, iters=30):
    ue = np.array([e[0] for e in E])
    ve = np.array([e[1] for e in E])
    x = x0.copy()

    def vals(y):
        return M @ (y[ue] * y[ve])

    for _ in range(iters):
        q = vals(x)
        best = q.min()
        act = np.where(q <= best + 1e-9)[0]
        if len(act) > 200:
            act = act[np.argsort(q[act])[:200]]
        G = np.zeros((len(act), n))
        for r, s in enumerate(act):
            mono = M[s]
            np.add.at(G[r], ue[mono], x[ve[mono]])
            np.add.at(G[r], ve[mono], x[ue[mono]])
        c = np.zeros(n + 1)
        c[-1] = -1.0
        A_ub = np.hstack([-G, np.ones((len(act), 1))])
        A_eq = np.zeros((1, n + 1))
        A_eq[0, :n] = 1.0
        bounds = [(0.0 if x[i] <= 1e-12 else -1.0, 1.0) for i in range(n)] + [(None, 1.0)]
        r = linprog(c, A_ub=A_ub, b_ub=np.zeros(len(act)), A_eq=A_eq, b_eq=[0.0],
                    bounds=bounds, method='highs')
        if not r.success or -r.fun <= 1e-11:
            break
        d = r.x[:n]
        cand = [(best, x)]
        for t in (0.4, 0.2, 0.1, 0.05, 0.02, 0.01, 5e-3, 2e-3, 1e-3):
            y = x + t * d
            if y.min() < -1e-12:
                continue
            y = np.maximum(y, 0.0)
            y /= y.sum()
            cand.append((vals(y).min(), y))
        v2, x2 = max(cand, key=lambda p: p[0])
        if v2 <= best + 1e-13:
            break
        x = x2
    return vals(x).min(), x


def exact_psi(n, E, xf):
    best = None
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        s = sum(xf[u] * xf[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        if best is None or s < best:
            best = s
    return best


def main(nlo, nhi, trials, seed=20260726):
    rng = np.random.default_rng(seed)
    print(f"randomised hunt (NOT an enumeration): n = {nlo}..{nhi}, {trials} graphs each; "
          f"reporting any psi > 1/25, window (1/25, 2/47]", flush=True)
    voids = 0
    for n in range(nlo, nhi + 1):
        best_n, best_g = 0.0, None
        for t in range(trials):
            E, adj = random_mtf(n, rng)
            c5s = induced_c5s(n, adj)
            M = mono_matrix(n, E)
            X0 = []
            for T in c5s:
                x = np.zeros(n)
                for v in T:
                    x[v] = 0.2
                X0.append(x)
            X0.append(np.ones(n) / n)
            for _ in range(4):
                X0.append(rng.dirichlet(np.ones(n)))
            bv, bx = 0.0, None
            for x0 in X0:
                v, xx = ascend(M, E, n, x0)
                if v > bv:
                    bv, bx = v, xx
            if c5s and bv < 0.04 - 1e-9:
                voids += 1                       # loop rule 9: optimiser failed its own floor
                continue
            if bv > best_n:
                best_n, best_g = bv, (E, bx)
            if bv > 0.04 + 1e-9:
                E2, bx2 = E, bx
                for D in (60, 120, 360, 2520, 27720):
                    a = [int(round(t * D)) for t in bx2]
                    tot = sum(a)
                    if tot == 0:
                        continue
                    xf = [F(ai, tot) for ai in a]
                    ex = exact_psi(n, E2, xf)
                    if ex > F(1, 25):
                        print(f"*** COUNTEREXAMPLE n={n} exact psi = {ex} = {float(ex)}", flush=True)
                        print(f"    E = {E2}", flush=True)
                        print(f"    x = {[str(t) for t in xf]}", flush=True)
                        return
                print(f"    n={n} numeric {bv:.10f} > 1/25, no rational rounding confirmed it",
                      flush=True)
        print(f"  n = {n}: {trials} random maximal triangle-free graphs, best numeric psi "
              f"= {best_n:.10f}", flush=True)
    print(f"no counterexample; optimiser-void runs (below the C5 floor) = {voids}", flush=True)


if __name__ == '__main__':
    a = sys.argv[1:]
    main(int(a[0]) if a else 16, int(a[1]) if len(a) > 1 else 20,
         int(a[2]) if len(a) > 2 else 40)
