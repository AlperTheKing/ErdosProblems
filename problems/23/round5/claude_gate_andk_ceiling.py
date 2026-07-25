"""ROOT-AGENT GATE (Claude): is max_x psi(And(k)) exactly 1/25 for k = 4..7, or does some And(k) break it?

This is the single cheapest decisive question left on the Andrasfai side.  The delta > N/3 reduction
needs max_x psi = 1/25 on EVERY And(k); R3-C17 proved it for k = 2, 3 only, and round 7 refuted the
degree-2 certificate scheme for k = 4 with an exact dual ray, so no certificate covers k >= 4.

Either outcome is worth having:
  * any And(k) with max_x psi > 1/25 is a COUNTEREXAMPLE to the conjecture (highest-value outcome);
  * all equal to 1/25 sharpens the target to "no weighting beats the C5-concentration on And(k)".

And(k) = Gamma_{3k-1}, the circle graph on m points with u ~ v iff 3*circdist(u,v) > m.

OPTIMISER DISCIPLINE (loop rule 9): every run starts from every induced C5 at weight 1/5, so the
returned value can never sit below 1/25 by accident; a value below the floor voids the run.
"""
import sys

import numpy as np
from fractions import Fraction as F
from itertools import combinations
from scipy.optimize import linprog


def gamma(m):
    return [(u, v) for u in range(m) for v in range(u + 1, m)
            if 3 * min((u - v) % m, (v - u) % m) > m]


def mono_matrix(n, E):
    ncuts = 1 << (n - 1)
    M = np.zeros((ncuts, len(E)), dtype=bool)
    m = np.arange(ncuts, dtype=np.int64)
    S = (m << 1) | 1
    for k, (u, v) in enumerate(E):
        M[:, k] = (((S >> u) & 1) == ((S >> v) & 1))
    return M


def induced_c5s(n, E, limit=12):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v)
        adj[v].add(u)
    out = []
    for S in combinations(range(n), 5):
        if all(len(adj[v] & set(S)) == 2 for v in S):
            out.append(S)
            if len(out) >= limit:
                break
    return out


def ascend(M, E, n, x0, iters=40):
    ue = np.array([e[0] for e in E])
    ve = np.array([e[1] for e in E])
    x = x0.copy()

    def vals(y):
        return M @ (y[ue] * y[ve])

    for _ in range(iters):
        q = vals(x)
        best = q.min()
        act = np.where(q <= best + 1e-9)[0]
        if len(act) > 250:
            act = act[np.argsort(q[act])[:250]]
        G = np.zeros((len(act), n))
        for r, s in enumerate(act):
            mono = M[s]
            np.add.at(G[r], ue[mono], x[ve[mono]])
            np.add.at(G[r], ve[mono], x[ue[mono]])
        c = np.zeros(n + 1)
        c[-1] = -1.0
        A_eq = np.zeros((1, n + 1))
        A_eq[0, :n] = 1.0
        bounds = [(0.0 if x[i] <= 1e-12 else -1.0, 1.0) for i in range(n)] + [(None, 1.0)]
        r = linprog(c, A_ub=np.hstack([-G, np.ones((len(act), 1))]), b_ub=np.zeros(len(act)),
                    A_eq=A_eq, b_eq=[0.0], bounds=bounds, method='highs')
        if not r.success or -r.fun <= 1e-11:
            break
        d = r.x[:n]
        cand = [(best, x)]
        for t in (0.4, 0.2, 0.1, 0.05, 0.02, 0.01, 5e-3, 2e-3, 1e-3, 3e-4):
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


def run(m, rand_starts=25, seed=20260726):
    E = gamma(m)
    n = m
    M = mono_matrix(n, E)
    c5s = induced_c5s(n, E)
    rng = np.random.default_rng(seed + m)
    X0 = []
    for T in c5s:
        x = np.zeros(n)
        for v in T:
            x[v] = 0.2
        X0.append(x)
    X0.append(np.ones(n) / n)
    for _ in range(rand_starts):
        X0.append(rng.dirichlet(np.ones(n)))
    best, bx = 0.0, None
    for x0 in X0:
        v, xx = ascend(M, E, n, x0)
        if v > best:
            best, bx = v, xx
    k = (m + 1) // 3
    tag = ""
    if best < 0.04 - 1e-9 and c5s:
        tag = "  VOID (below the C5 floor)"
    elif best > 0.04 + 1e-9:
        tag = "  ABOVE 1/25 - checking exactly"
    print(f"And({k}) = Gamma_{m}: |E| = {len(E)}, cuts = {1 << (n-1)}, induced C5s found = "
          f"{len(c5s)},  max_x psi ~ {best:.10f}{tag}", flush=True)
    if best > 0.04 + 1e-9:
        for D in (60, 120, 360, 2520, 27720, 360360):
            a = [int(round(t * D)) for t in bx]
            tot = sum(a)
            if tot == 0:
                continue
            xf = [F(ai, tot) for ai in a]
            ex = exact_psi(n, E, xf)
            if ex > F(1, 25):
                print(f"  *** COUNTEREXAMPLE And({k}): exact psi = {ex} = {float(ex)}", flush=True)
                print(f"      x = {[str(t) for t in xf]}", flush=True)
                return True
        print("  numeric excess did not survive exact rational rounding", flush=True)
    return False


if __name__ == '__main__':
    ms = [int(t) for t in sys.argv[1:]] or [11, 14, 17, 20]
    for m in ms:
        run(m)
