#!/usr/bin/env python3
"""
2-colored flag-algebra SDP (primal) for beta = monochromatic edge density (Phase C).
Target: max d_mono over 2-colored triangle-free graphons in the band [+ max-cut switching, added next].
Conjecture: d_mono <= 2/25 = 0.08  (since beta/N^2 -> d_mono/2, and beta<=N^2/25).

PRIMAL flag SDP:
  maximize  sum_H d_mono(H) x_H
  s.t.      x_H >= 0,  sum_H x_H = 1,
            M^sigma(x) := sum_H x_H P^sigma(H)  PSD   (each colored type sigma),
            d_edge band:  0.2486 <= sum_H d_edge(H) x_H <= 0.32,
            [switching constraints added in flag_switch.py]
The optimum is a certified UPPER bound on d_mono for actual graphons (flag relaxation).
"""
import itertools
import numpy as np
import cvxpy as cp
import flag_engine as fe
import flag_engine_col as fc


# ---------- colored flags ----------
def enumerate_flags_col(sigma, m, triangle_free=True):
    """All triangle-free colored sigma-flags on m vertices up to root-fixing colored iso.
    sigma=(k,Asig,colsig): first k vertices induce sigma (edges+colors) exactly."""
    k, Asig, colsig = sigma
    slots = [(i, j) for i in range(k) for j in range(k, m)] + \
            [(i, j) for i in range(k, m) for j in range(i+1, m)]
    seen = {}
    for cfree in itertools.product((0, 1), repeat=(m-k)):
        col = list(colsig) + list(cfree)
        for bits in itertools.product((0, 1), repeat=len(slots)):
            A = [0]*m
            for i in range(k):
                for j in range(i+1, k):
                    if (Asig[i] >> j) & 1:
                        A[i] |= 1 << j; A[j] |= 1 << i
            for (slot, b) in zip(slots, bits):
                if b:
                    i, j = slot; A[i] |= 1 << j; A[j] |= 1 << i
            if triangle_free and not fe.is_triangle_free(m, A):
                continue
            ck = fc.canonical_col(m, A, col, roots=k)
            if ck not in seen:
                seen[ck] = (m, fe.graph_from_key(m, ck[1]), list(ck[0]))
    return list(seen.values())


def _induces_sigma_col(Ah, colh, R, sigma):
    k, Asig, colsig = sigma
    for a in range(k):
        if colh[R[a]] != colsig[a]:
            return False
    for a in range(k):
        for b in range(a+1, k):
            e = 1 if (Ah[R[a]] >> R[b]) & 1 else 0
            s = 1 if (Asig[a] >> b) & 1 else 0
            if e != s:
                return False
    return True


def _flagkey_col(Ah, colh, R, S, k):
    verts = list(R) + list(S)
    m = len(verts)
    _, B = fe.induced(Ah, verts)
    cc = tuple(colh[v] for v in verts)
    return fc.canonical_col(m, B, cc, roots=k)


def P_sigma_col(states, sigma, flags):
    k = sigma[0]
    s = flags[0][0] - k
    t = len(flags)
    flagidx = {fc.canonical_col(fm, fA, fcol, roots=k): i for i, (fm, fA, fcol) in enumerate(flags)}
    mats = []
    for (n, Ah, colh) in states:
        M = np.zeros((t, t))
        allv = list(range(n))
        for R in itertools.permutations(range(n), k):
            if not _induces_sigma_col(Ah, colh, R, sigma):
                continue
            rest = [v for v in allv if v not in R]
            subs = list(itertools.combinations(rest, s))
            idxs = [flagidx.get(_flagkey_col(Ah, colh, R, S, k), -1) for S in subs]
            for a in range(len(subs)):
                ia = idxs[a]
                if ia < 0: continue
                Sa = set(subs[a])
                for b in range(len(subs)):
                    ib = idxs[b]
                    if ib < 0: continue
                    if Sa & set(subs[b]): continue
                    M[ia, ib] += 1.0
        mats.append(M)
    return mats


# ---------- objective / densities ----------
def d_mono_vec(states):
    m00 = fc.mono_edge(); m11 = fc.mono_edge_11()
    return np.array([fc.induced_density_col(m00, H) + fc.induced_density_col(m11, H) for H in states])

def d_edge_vec(states):
    m00 = fc.mono_edge(); m11 = fc.mono_edge_11(); ce = fc.cut_edge()
    return np.array([fc.induced_density_col(m00, H) + fc.induced_density_col(m11, H)
                     + fc.induced_density_col(ce, H) for H in states])


# ---------- colored types ----------
def colored_types(N, kmax=2):
    """All colored triangle-free types on k=1..kmax vertices, with their order-m flag lists
    (m chosen so k+2(m-k) <= N)."""
    out = []
    for k in range(1, kmax+1):
        for (kk, A, col) in fc.enumerate_colored(k, triangle_free=True):
            sigma = (k, A, tuple(col))
            smax = (N - k) // 2
            for s in range(1, smax+1):
                m = k + s
                flags = enumerate_flags_col(sigma, m)
                if len(flags) >= 1:
                    out.append((sigma, flags))
    return out


# ---------- primal SDP ----------
def solve_primal(N, types_and_flags, band=(0.2486, 0.32), extra_lin=None, verbose=True):
    """maximize d_mono(x) over x>=0, sum=1, M^sigma(x) PSD, band on d_edge, extra linear <=0 constraints.
       extra_lin: list of (vector over states) g with constraint sum_H g(H) x_H <= 0 (switching)."""
    states = fc.enumerate_colored(N, triangle_free=True)
    ns = len(states)
    dmono = d_mono_vec(states); dedge = d_edge_vec(states)
    x = cp.Variable(ns, nonneg=True)
    cons = [cp.sum(x) == 1]
    if band:
        cons += [dedge @ x >= band[0], dedge @ x <= band[1]]
    npsd = 0
    for (sigma, flags) in types_and_flags:
        mats = P_sigma_col(states, sigma, flags)
        t = len(flags)
        if t == 1:
            continue
        # vectorized: M[i,j] = sum_h x_h mats[h][i,j]  ->  reshape((t*t, ns) @ x)
        Pflat = np.stack([m.ravel() for m in mats], axis=1)   # (t*t, ns)
        M = cp.reshape(Pflat @ x, (t, t), order='C')
        cons.append(0.5*(M + M.T) >> 0); npsd += 1
    if extra_lin:
        for g in extra_lin:
            cons.append(g @ x <= 0)
    prob = cp.Problem(cp.Maximize(dmono @ x), cons)
    val = prob.solve(solver=cp.SCS, max_iters=20000)
    if verbose:
        print(f"  N={N}: states={ns} types={len(types_and_flags)} PSD-blocks={npsd}  "
              f"max d_mono = {val:.6f}  (target <= 0.08)  status={prob.status}")
    return val, prob.status, states, x


if __name__ == "__main__":
    print("=== Phase C baseline: 2-colored flag SDP for d_mono (band only, NO switching yet) ===")
    for N in (5, 6):
        tf = colored_types(N, kmax=2)
        solve_primal(N, tf, band=(0.2486, 0.32))
    print("(switching constraints next — baseline shows how far band+flags alone get)")
    print("DONE")
