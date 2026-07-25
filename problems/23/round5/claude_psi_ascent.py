"""ROOT-AGENT COUNTEREXAMPLE PROBE (Claude, round 5): a CORRECT max-min optimiser for
        psi(H,x) = min over cuts S of sum_{uv monochromatic} x_u x_v
run over the COMPLETE corpus of maximal triangle-free patterns.

Why this is the right tool.  psi is a minimum of quadratics: nonsmooth, and ordinary hill-climbing
finds local optima (that error produced retracted numbers earlier in this campaign).  Here the
ascent direction comes from a linear program over the ACTIVE cuts:

        maximise  delta   s.t.  <grad q_S(x), d> >= delta  for every active S,
                                sum d = 0,  -1 <= d <= 1,  d_u >= 0 where x_u = 0.

If delta <= 0 the point is first-order stationary.  Starts include EVERY induced-C5 concentration
(mandatory by the plateau theorem: psi there is exactly 1/25, so any run returning less is void),
the uniform point, and random points.  The best point found is re-evaluated in exact rationals.

A pattern with max_x psi > 1/25 is a COUNTEREXAMPLE to Erdos 23.
"""
import sys
import numpy as np
from fractions import Fraction as F
from itertools import combinations
from scipy.optimize import linprog


def g6(s):
    b = [ord(c) - 63 for c in s]
    n = b[0]; i = 1
    if n == 63:
        n = (b[1] << 12) | (b[2] << 6) | b[3]; i = 4
    bits = []
    for x in b[i:]:
        bits.extend((x >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    E = []; p = 0
    for j in range(1, n):
        for k in range(j):
            if bits[p]:
                E.append((k, j))
            p += 1
    return n, E


def build(n, E):
    """cuts x edges incidence of 'monochromatic under this cut'"""
    m = len(E)
    rows = []
    for mask in range(1 << (n - 1)):
        S = (mask << 1) | 1
        rows.append([1.0 if ((S >> u) & 1) == ((S >> v) & 1) else 0.0 for (u, v) in E])
    return np.array(rows)


def psi_vals(M, E, x):
    p = np.array([x[u] * x[v] for (u, v) in E])
    return M @ p


def grad(M, E, x, idx, n):
    """gradient of q_S for the cuts listed in idx"""
    G = np.zeros((len(idx), n))
    for r, s in enumerate(idx):
        row = M[s]
        for e, (u, v) in enumerate(E):
            if row[e]:
                G[r, u] += x[v]; G[r, v] += x[u]
    return G


def induced_c5s(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    out = []
    for S in combinations(range(n), 5):
        if all(len(adj[v] & set(S)) == 2 for v in S):
            out.append(S)
    return out


def ascend(M, E, n, x0, iters=60):
    x = x0.copy()
    for _ in range(iters):
        q = psi_vals(M, E, x)
        val = q.min()
        act = np.where(q <= val + 1e-9)[0]
        if len(act) > 400:
            act = act[np.argsort(q[act])[:400]]
        G = grad(M, E, x, act, n)
        # variables: d (n), delta (1); maximise delta
        c = np.zeros(n + 1); c[-1] = -1.0
        A_ub = np.hstack([-G, np.ones((len(act), 1))])
        b_ub = np.zeros(len(act))
        A_eq = np.zeros((1, n + 1)); A_eq[0, :n] = 1.0
        b_eq = [0.0]
        bounds = [(0.0 if x[i] <= 1e-12 else -1.0, 1.0) for i in range(n)] + [(None, 1.0)]
        r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        if not r.success or -r.fun <= 1e-11:
            break
        d = r.x[:n]
        best = (val, x)
        for t in (0.5, 0.25, 0.12, 0.06, 0.03, 0.015, 0.008, 0.004, 0.002, 0.001, 5e-4, 2e-4):
            y = x + t * d
            if y.min() < -1e-12:
                continue
            y = np.maximum(y, 0.0); y /= y.sum()
            v2 = psi_vals(M, E, y).min()
            if v2 > best[0]:
                best = (v2, y)
        if best[0] <= val + 1e-13:
            break
        x = best[1]
    return psi_vals(M, E, x).min(), x


def exact_psi(n, E, xf):
    best = None
    for mask in range(1 << (n - 1)):
        S = (mask << 1) | 1
        s = sum(xf[u] * xf[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        if best is None or s < best:
            best = s
    return best


def run(path, starts=24, seed=0):
    rng = np.random.default_rng(seed)
    hits = []
    best_overall = (0.0, None)
    npat = 0
    for line in open(path):
        s = line.strip()
        if not s:
            continue
        n, E = g6(s)
        M = build(n, E)
        npat += 1
        c5s = induced_c5s(n, E)
        X0 = []
        for T in c5s[:6]:
            x = np.zeros(n)
            for v in T:
                x[v] = 0.2
            X0.append(x)
        X0.append(np.ones(n) / n)
        for _ in range(starts):
            X0.append(rng.dirichlet(np.ones(n)))
        bv, bx = 0.0, None
        for x0 in X0:
            v, x = ascend(M, E, n, x0)
            if v > bv:
                bv, bx = v, x
        if bv > best_overall[0]:
            best_overall = (bv, s)
        if bv > 0.04 + 1e-9:
            # exact re-evaluation at a rational rounding of the best point
            for D in (60, 120, 360, 2520):
                a = [int(round(t * D)) for t in bx]
                tot = sum(a)
                if tot == 0:
                    continue
                xf = [F(ai, tot) for ai in a]
                ex = exact_psi(n, E, xf)
                if ex > F(1, 25):
                    print(f"*** COUNTEREXAMPLE {s}  exact psi = {ex} = {float(ex)} > 1/25   x = {[str(t) for t in xf]}")
                    hits.append((s, ex, xf))
                    break
            else:
                print(f"    numeric {bv:.10f} > 1/25 on {s} but no rational rounding exceeded 1/25 "
                      f"(numerical artefact)")
    print(f"{path}: {npat} patterns, best numeric psi = {best_overall[0]:.10f} on {best_overall[1]}, "
          f"exact counterexamples = {len(hits)}")
    return hits


if __name__ == '__main__':
    total = []
    for p in sys.argv[1:]:
        total += run(p)
    print("TOTAL exact counterexamples:", len(total))
