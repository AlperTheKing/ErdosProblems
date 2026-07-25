"""H2_typeopt.py -- for EVERY realisable k-atom type, maximise
      ARCBOUND(x) = min over cyclic intervals I of  sum_{uv in E, u,v same side} x_u x_v
over the simplex.  Any value > 1/25 refutes the arc-cut conjecture; any x with
ARCBOUND(x) * (sum x)^2 > W(x)^2 refutes W-square.

Search is float (successive LP + many restarts); every reported optimum is then
re-certified exactly in Fractions by H2_exact_check.
"""
import sys, itertools, json
import numpy as np
from scipy.optimize import linprog
from H2_types import enumerate_types, adj_from_type


def build(t):
    k = len(t)
    A = adj_from_type(t)
    E = [(i, j) for i in range(k) for j in A[i] if i < j]
    arcs = []
    for s in range(k):
        for L in range(1, k):
            mask = 0
            for u in range(L):
                mask |= 1 << ((s + u) % k)
            arcs.append(mask)
    arcs = sorted(set(arcs))
    # quadratic form of each arc: pairs that are monochromatic
    Ms = []
    for mask in arcs:
        pr = [(i, j) for (i, j) in E
              if ((mask >> i) & 1) == ((mask >> j) & 1)]
        Ms.append(pr)
    return k, A, E, arcs, Ms


def vals(x, Ms):
    return np.array([sum(x[i] * x[j] for (i, j) in pr) for pr in Ms])


def grads(x, Ms, k):
    G = np.zeros((len(Ms), k))
    for r, pr in enumerate(Ms):
        for (i, j) in pr:
            G[r, i] += x[j]
            G[r, j] += x[i]
    return G


def ascent(x0, Ms, k, iters=250, radius=0.5):
    x = np.maximum(np.array(x0, float), 0)
    if x.sum() <= 0:
        return x, -1
    x /= x.sum()
    v = vals(x, Ms).min()
    r = radius
    for it in range(iters):
        V = vals(x, Ms)
        tau = V.min()
        G = grads(x, Ms, k)
        c = np.zeros(k + 1); c[-1] = -1.0
        A_ub = np.hstack([-G, np.ones((len(Ms), 1))])
        b_ub = V - tau
        A_eq = np.zeros((1, k + 1)); A_eq[0, :k] = 1.0
        bounds = [(max(-r, -xi), r) for xi in x] + [(0, None)]
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=[0.0],
                      bounds=bounds, method="highs")
        if not res.success or res.x is None:
            r *= 0.5
            if r < 1e-13: break
            continue
        d = res.x[:k]
        bt, bv = 0.0, tau
        for s in (1.0, .7, .5, .3, .2, .1, .05, .02, .01, .003):
            y = np.maximum(x + s * d, 0)
            if y.sum() <= 0: continue
            y = y / y.sum()
            vv = vals(y, Ms).min()
            if vv > bv + 1e-16:
                bt, bv = s, vv
        if bt == 0.0:
            r *= 0.5
            if r < 1e-13: break
            continue
        x = np.maximum(x + bt * d, 0); x /= x.sum()
    return x, vals(x, Ms).min()


def induced_c5_seeds(k, A):
    out = []
    for S in itertools.combinations(range(k), 5):
        sub = [[1 if b in A[a] else 0 for b in S] for a in S]
        deg = [sum(row) for row in sub]
        if deg != [2] * 5:
            continue
        # connected? a 2-regular graph on 5 vertices is C5 iff connected
        seen = {0}; st = [0]
        while st:
            u = st.pop()
            for vi in range(5):
                if sub[u][vi] and vi not in seen:
                    seen.add(vi); st.append(vi)
        if len(seen) == 5:
            x = np.zeros(k)
            for a in S: x[a] = 0.2
            out.append(x)
    return out


def run_k(k, nmax, nrand=60, seed=1, report_all=False):
    seen = enumerate_types(k, nmax)
    rng = np.random.default_rng(seed)
    best_overall = (-1, None, None)
    eq_types = 0
    over = []
    for ti, (t, wit) in enumerate(sorted(seen.items())):
        k2, A, E, arcs, Ms = build(t)
        seeds = [np.ones(k) / k]
        seeds += induced_c5_seeds(k, A)
        for _ in range(nrand):
            y = rng.random(k) ** 3
            seeds.append(y / y.sum())
        for _ in range(nrand // 3):
            y = np.zeros(k)
            supp = rng.choice(k, size=int(rng.integers(3, k + 1)), replace=False)
            y[supp] = rng.random(len(supp))
            seeds.append(y / y.sum())
        bv, bx = -1, None
        for s0 in seeds:
            x, v = ascent(s0, Ms, k)
            if v > bv:
                bv, bx = v, x
        if 25 * bv > 1 + 1e-9:
            over.append((t, bv, bx.copy()))
            print(f"  !!! k={k} type={t} 25*max = {25*bv:.12f}  x={np.round(bx,8)}")
        if abs(25 * bv - 1) < 1e-7:
            eq_types += 1
        if bv > best_overall[0]:
            best_overall = (bv, t, bx.copy())
    print(f"k={k}: types={len(seen)}  max 25*ARCBOUND = {25*best_overall[0]:.12f} "
          f"at type {best_overall[1]}   #types attaining 1/25 = {eq_types}  "
          f"#types over = {len(over)}")
    sys.stdout.flush()
    return best_overall, over


if __name__ == "__main__":
    kk = [int(t) for t in sys.argv[1:]] or [5, 6, 7, 8]
    for k in kk:
        nmax = {4: 24, 5: 26, 6: 26, 7: 24, 8: 22, 9: 21, 10: 20, 11: 19, 12: 19}.get(k, 18)
        run_k(k, nmax)
