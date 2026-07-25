"""H2_opt.py -- global maximisation of ARCBOUND over measures on the circle.

Everything is done on the grid Gamma_m with FREE nonnegative weights (zeros
allowed), so a measure with k atoms at arbitrary rational positions p/m is just a
weight vector with m-k zeros.  Taking m large therefore covers non-uniform
discretisations too (assignment (c)).

Fast evaluator.  a = floor(m/3)+1 is the smallest index-distance that is adjacent,
b = m-a the largest.  For an interval of length L starting at s let
    F_L[s] = sum of x_i x_j over adjacent pairs inside [s, s+L).
Then  F_L[s] = F_{L-1}[s] + x[j] * ( sum of x over the cyclic range [j+lo_L, j+b] ),
with j = s+L-1 and lo_L = max(a, m-L+1)  (empty when lo_L > b), because
[s,j) meets N(j) = [j+a, j+b] exactly in that single cyclic range.
Finally  mono([s,s+L)) = F_L[s] + F_{m-L}[s+L].

Floating point is used only to SEARCH; every candidate is re-checked exactly by
H2_exact_check.
"""
import numpy as np


def make(m):
    a = m // 3 + 1
    b = m - a
    return a, b


def all_F(x, m, a, b):
    """F[L][s] for L = 0..m."""
    F = np.zeros((m + 1, m))
    xx = np.concatenate([x, x, x])
    P = np.zeros(3 * m + 1)
    P[1:] = np.cumsum(xx)
    idx = np.arange(m)
    for L in range(1, m + 1):
        lo = max(a, m - L + 1)
        F[L] = F[L - 1]
        if lo <= b:
            j = (idx + L - 1) % m
            # sum of x over cyclic [j+lo, j+b]
            s0 = j + lo
            s1 = j + b + 1
            F[L] += x[j] * (P[s1] - P[s0])
    return F


def arcbound_np(x, m, a, b, F=None, want_arcs=False, tol=0.0):
    if F is None:
        F = all_F(x, m, a, b)
    idx = np.arange(m)
    M = np.empty((m + 1, m))
    for L in range(0, m + 1):
        M[L] = F[L] + F[m - L][(idx + L) % m]
    v = M.min()
    if not want_arcs:
        return v
    act = np.argwhere(M <= v + tol)
    return v, M, act


def _nbr_sum(y, m, a, b):
    """r[i] = sum of y over the cyclic interval [i+a, i+b]  (= neighbours of i)."""
    yy = np.concatenate([y, y, y])
    P = np.zeros(3 * m + 1)
    P[1:] = np.cumsum(yy)
    idx = np.arange(m)
    return P[idx + b + 1] - P[idx + a]


def mono_grad(x, m, a, b, L, s):
    """gradient of mono([s,s+L)) wrt x  (vector of length m).  O(m)."""
    inA = np.zeros(m, dtype=bool)
    if L > 0:
        j = (np.arange(L) + s) % m
        inA[j] = True
    u = np.where(inA, x, 0.0)
    v = x - u
    ru = _nbr_sum(u, m, a, b)
    rv = _nbr_sum(v, m, a, b)
    return np.where(inA, ru, rv)


def arc_indicator(m, L, s):
    inA = np.zeros(m, dtype=bool)
    for t in range(L):
        inA[(s + t) % m] = True
    return inA


def lp_ascent(x, m, a, b, iters=200, nact=60, radius=0.25, seed=0, verbose=False):
    """Successive-LP ascent on max_x min_arcs mono."""
    from scipy.optimize import linprog
    x = np.array(x, dtype=float)
    x = np.maximum(x, 0)
    x /= x.sum()
    best = arcbound_np(x, m, a, b)
    for it in range(iters):
        v, M, _ = arcbound_np(x, m, a, b, want_arcs=True)
        flat = M.ravel()
        order = np.argsort(flat)[:nact]
        arcs = [(int(o // m), int(o % m)) for o in order]
        G = np.array([mono_grad(x, m, a, b, L, s) for (L, s) in arcs])
        vals = np.array([M[L, s] for (L, s) in arcs])
        # max delta  s.t. vals + G d >= v + delta ; sum d = 0 ; -r<=d<=r ; x+d>=0
        n = m
        c = np.zeros(n + 1); c[-1] = -1.0
        A_ub = np.hstack([-G, np.ones((len(arcs), 1))])
        b_ub = vals - v
        A_eq = np.zeros((1, n + 1)); A_eq[0, :n] = 1.0
        b_eq = [0.0]
        r = radius / m
        bounds = [(max(-r, -xi), r) for xi in x] + [(0, None)]
        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method="highs")
        except Exception:
            break
        if not res.success:
            radius *= 0.5
            if radius < 1e-9:
                break
            continue
        d = res.x[:n]
        if np.abs(d).max() < 1e-14:
            radius *= 0.5
            if radius < 1e-12:
                break
            continue
        # exact-ish line search
        bestt, bestv = 0.0, v
        for t in [1.0, 0.7, 0.5, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01]:
            y = x + t * d
            if y.min() < -1e-15:
                continue
            y = np.maximum(y, 0)
            s = y.sum()
            if s <= 0:
                continue
            y /= s
            vv = arcbound_np(y, m, a, b)
            if vv > bestv:
                bestt, bestv = t, vv
        if bestt == 0.0:
            radius *= 0.5
            if radius < 1e-12:
                break
            continue
        x = np.maximum(x + bestt * d, 0); x /= x.sum()
        best = bestv
        if verbose and it % 20 == 0:
            print(f"    it={it} 25*AB={25*best:.9f} radius={radius:.2e}")
    return x, best


def block_ascent(x, m, a, b, rounds=40):
    """Exact-in-block LP ascent: within any set of pairwise NON-adjacent indices the
    objective is a min of affine functions, hence concave -> a single LP is exact.
    The arcs [c, c+a-1] of index-length a are such sets."""
    from scipy.optimize import linprog
    x = np.array(x, float); x = np.maximum(x, 0); x /= x.sum()
    for rd in range(rounds):
        improved = False
        for c0 in range(m):
            S = [(c0 + t) % m for t in range(a)]          # pairwise non-adjacent
            mass = sum(x[i] for i in S)
            if mass <= 0:
                continue
            # affine model: mono(A) = const + sum_{i in S} x_i * (sum of x_j, j~i, j same side, j notin S)
            # build exactly by evaluating with x_S replaced by unit vectors
            base = np.array(x); base[S] = 0.0
            Fb = all_F(base, m, a, b)
            idxs = np.arange(m)
            const = np.empty((m + 1, m))
            for L in range(m + 1):
                const[L] = Fb[L] + Fb[m - L][(idxs + L) % m]
            coef = np.zeros((len(S), m + 1, m))
            for k, i in enumerate(S):
                e = np.zeros(m); e[i] = 1.0
                y = base + e
                Fy = all_F(y, m, a, b)
                for L in range(m + 1):
                    coef[k, L] = (Fy[L] + Fy[m - L][(idxs + L) % m]) - const[L]
            nA = (m + 1) * m
            A_ub = np.zeros((nA, len(S) + 1))
            b_ub = np.zeros(nA)
            r = 0
            for L in range(m + 1):
                for s in range(m):
                    for k in range(len(S)):
                        A_ub[r, k] = -coef[k, L, s]
                    A_ub[r, -1] = 1.0
                    b_ub[r] = const[L, s]
                    r += 1
            cvec = np.zeros(len(S) + 1); cvec[-1] = -1.0
            A_eq = np.zeros((1, len(S) + 1)); A_eq[0, :len(S)] = 1.0
            res = linprog(cvec, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=[mass],
                          bounds=[(0, None)] * len(S) + [(None, None)], method="highs")
            if res.success:
                newx = np.array(x); newx[S] = res.x[:len(S)]
                if arcbound_np(newx, m, a, b) > arcbound_np(x, m, a, b) + 1e-14:
                    x = newx
                    improved = True
        if not improved:
            break
    return x, arcbound_np(x, m, a, b)
