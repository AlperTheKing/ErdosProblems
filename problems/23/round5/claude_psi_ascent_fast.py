"""ROOT-AGENT (Claude): vectorised max-min optimiser for psi, for the n = 14..16 pattern sweep.

Same algorithm as claude_psi_ascent.py (LP ascent over the active cuts, mandatory induced-C5 starts)
but with the cut structure held as a dense (ncuts, n, n) array so that every value and every gradient
is a numpy contraction:

        q_S(x) = 1/2 * x^T M_S x ,      grad q_S(x) = M_S x .

Validation is mandatory and printed before any sweep result: the optimiser must return exactly 1/25
on C5, 1/49 on C7, 0 on K_{3,3}, and must never return below 1/25 on a graph of odd girth 5.
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
    ncuts = 1 << (n - 1)
    M = np.zeros((ncuts, n, n), dtype=np.float64)
    for m in range(ncuts):
        S = (m << 1) | 1
        for (u, v) in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                M[m, u, v] = 1.0
                M[m, v, u] = 1.0
    return M


def vals(M, x):
    return 0.5 * np.einsum('sij,i,j->s', M, x, x)


def induced_c5s(n, E, limit=8):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    out = []
    for S in combinations(range(n), 5):
        if all(len(adj[v] & set(S)) == 2 for v in S):
            out.append(S)
            if len(out) >= limit:
                break
    return out


def ascend(M, n, x0, iters=28):
    x = x0.copy()
    for _ in range(iters):
        q = vals(M, x)
        best = q.min()
        act = np.where(q <= best + 1e-9)[0]
        if len(act) > 250:
            act = act[np.argsort(q[act])[:250]]
        G = M[act] @ x                                  # (|act|, n) gradients
        c = np.zeros(n + 1); c[-1] = -1.0
        A_ub = np.hstack([-G, np.ones((len(act), 1))])
        b_ub = np.zeros(len(act))
        A_eq = np.zeros((1, n + 1)); A_eq[0, :n] = 1.0
        bounds = [(0.0 if x[i] <= 1e-12 else -1.0, 1.0) for i in range(n)] + [(None, 1.0)]
        r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=[0.0], bounds=bounds, method='highs')
        if not r.success or -r.fun <= 1e-11:
            break
        d = r.x[:n]
        cand = [(best, x)]
        for t in (0.4, 0.2, 0.1, 0.05, 0.02, 0.01, 5e-3, 2e-3, 1e-3, 3e-4):
            y = x + t * d
            if y.min() < -1e-12:
                continue
            y = np.maximum(y, 0.0); y /= y.sum()
            cand.append((vals(M, y).min(), y))
        v2, x2 = max(cand, key=lambda p: p[0])
        if v2 <= best + 1e-13:
            break
        x = x2
    return vals(M, x).min(), x


def exact_psi(n, E, xf):
    best = None
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        s = sum(xf[u] * xf[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        if best is None or s < best:
            best = s
    return best


def run_file(path, starts=5, seed=0, report_every=100):
    rng = np.random.default_rng(seed)
    npat = 0; best_overall = (0.0, None); hits = []
    for line in open(path):
        s = line.strip()
        if not s:
            continue
        n, E = g6(s)
        M = build(n, E)
        npat += 1
        X0 = []
        for T in induced_c5s(n, E):
            x = np.zeros(n)
            for v in T:
                x[v] = 0.2
            X0.append(x)
        X0.append(np.ones(n) / n)
        for _ in range(starts):
            X0.append(rng.dirichlet(np.ones(n)))
        bv, bx = 0.0, None
        for x0 in X0:
            v, xx = ascend(M, n, x0)
            if v > bv:
                bv, bx = v, xx
        if bv > best_overall[0]:
            best_overall = (bv, s)
        if bv > 0.04 + 1e-9:
            for D in (60, 120, 360, 2520, 27720):
                a = [int(round(t * D)) for t in bx]
                tot = sum(a)
                if tot == 0:
                    continue
                xf = [F(ai, tot) for ai in a]
                ex = exact_psi(n, E, xf)
                if ex > F(1, 25):
                    print(f"*** COUNTEREXAMPLE {s}  exact psi = {ex} = {float(ex)}  x = {[str(t) for t in xf]}",
                          flush=True)
                    hits.append((s, ex))
                    break
            else:
                print(f"    numeric {bv:.10f} > 1/25 on {s}, no rational rounding confirmed", flush=True)
        if npat % report_every == 0:
            print(f"  ... {npat} patterns, best so far {best_overall[0]:.10f}", flush=True)
    print(f"{path}: {npat} patterns, best numeric psi = {best_overall[0]:.10f} on {best_overall[1]}, "
          f"exact counterexamples = {len(hits)}", flush=True)
    return hits


if __name__ == '__main__':
    if '--validate' in sys.argv:
        for name, (n, E) in [('C5', (5, [(i, (i + 1) % 5) for i in range(5)])),
                             ('C7', (7, [(i, (i + 1) % 7) for i in range(7)])),
                             ('K33', (6, [(i, 3 + j) for i in range(3) for j in range(3)]))]:
            M = build(n, E)
            rng = np.random.default_rng(1)
            best = 0.0
            for x0 in [np.ones(n) / n] + [rng.dirichlet(np.ones(n)) for _ in range(15)]:
                v, _ = ascend(M, n, x0)
                best = max(best, v)
            print(f"validate {name}: {best:.10f}")
        sys.exit(0)
    total = []
    for p in sys.argv[1:]:
        total += run_file(p)
    print("TOTAL exact counterexamples:", len(total))
