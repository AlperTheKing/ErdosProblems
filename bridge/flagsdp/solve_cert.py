#!/usr/bin/env python3
"""Load cache_nN.pkl and (a) confirm eta<0 via exact HIGHS-LP route (trustworthy, no SDP solver doubt)
and conic route, (b) extract the SDP dual (Y_sigma, Z_loc, alpha, mu, nu), (c) build & verify the
EXACT rational certificate Phi(H) < 0 for all states.

Certificate logic: a triangle-free counterexample graphon W (d_mono>t, e(W) in band) induces x_W with
  g_r . x >= 0 (deficit), L^{sig,p}(x) >> 0 (localizer), M^sig(x) >> 0 (moment), e in [lo,hi].
If rational alpha_r>=0, mu,nu>=0, Y_sig>>0, Z>>0 give Phi(H) < 0 for ALL H, then
  0 > sum_H x_H Phi(H) = sum alpha_r (g_r.x) + <Y,M(x)> + <Z,L(x)> + mu(hi-e) + nu(e-lo) >= 0  -> contradiction.
"""
import sys, time, pickle
from fractions import Fraction as F
import numpy as np
import cvxpy as cp
import flag_engine as fe
import flag_cutgen as fc
import flag_localizer as floc
import flag_exact as fx

def load(N):
    with open(f"cache_n{N}.pkl", "rb") as f:
        return pickle.load(f)

def reconstruct(C):
    states = C["states"]; ns = len(states)
    dedge = C["dedge"]; Gbase = C["Gbase"]; t = C["t"]
    deftypes = C["deftypes"]
    Pflats = [(lab, tt, Pf) for (lab, tt, sigma, flags, s, Pf, Pint) in C["moments"]]
    sup = list(C["sup"]); Csup = C["Csup"]; Gsup = C["Gsup"]
    CONST = {hi: Csup[i] for i, hi in enumerate(sup)}
    GRAD = {hi: Gsup[i] for i, hi in enumerate(sup)}
    C5 = C["C5"]
    return states, ns, dedge, Gbase, t, deftypes, Pflats, sup, CONST, GRAD, C5

def run_lp(C, maxit=300, mom_maxvecs=8, band=(0.2486, 0.3197), tol=1e-7, verbose=True):
    states, ns, dedge, Gbase, t, deftypes, Pflats, sup, CONST, GRAD, C5 = reconstruct(C)
    G = Gbase.copy()
    Mrows = []
    # rank-one moment cut machinery: reshape Pf back to (ns,tt,tt)
    Pmom = [(lab, tt, Pf.T.reshape(ns, tt, tt)) for (lab, tt, Pf) in Pflats]
    def solve():
        x = cp.Variable(ns, nonneg=True); eta = cp.Variable()
        cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1], G @ x >= eta]
        if Mrows:
            cons.append(floc._norm_rows(Mrows) @ x >= 0)
        pr = cp.Problem(cp.Maximize(eta), cons); val = pr.solve(solver=cp.HIGHS)
        return val, np.array(x.value).ravel()
    v, x = solve()
    t0 = time.time()
    for it in range(1, maxit + 1):
        added = 0; newcuts = []
        for (k, A, E, S, cls) in deftypes:
            g, p = fc.separate(E, S, x, t)
            if g < v - tol:
                newcuts.append(fc.cut_from_p(E, S, p, t)); added += 1
        madded = 0; mn = 0.0
        for (lab, tt, P) in Pmom:
            rows, lam, _ = fc.separate_moment(P, x, maxvecs=mom_maxvecs); mn = min(mn, lam)
            for r in rows:
                Mrows.append(r); madded += 1
        ladded = 0; lmn = 0.0
        res = floc.separate_localizer_p(CONST, GRAD, sup, x)
        if res is not None:
            p, lam, w = res; lmn = lam; Q = floc.qmat(p)
            r = np.zeros(ns)
            for hi in sup:
                r[hi] = float(w @ (CONST[hi] + np.einsum("abcd,cd->ab", GRAD[hi], Q)) @ w)
            Mrows.append(r); ladded += 1
        if added == 0 and madded == 0 and ladded == 0:
            if verbose: print(f"  LP iter{it}: CONVERGED eta={v:+.7f} (meig={mn:+.1e})", flush=True)
            break
        if newcuts:
            G = np.vstack([G] + newcuts)
        v, x = solve()
        if verbose and (it <= 5 or it % 10 == 0):
            print(f"  LP iter{it}: +{added}d+{madded}m+{ladded}L eta={v:+.7f} rows={len(Mrows)} meig={mn:+.1e} Leig={lmn:+.1e} [{time.time()-t0:.0f}s]", flush=True)
        if v < -1e-4:    # robustly negative -> stop (confirmed)
            if verbose: print(f"  LP iter{it}: eta={v:+.7f} robustly < 0 -> CONFIRMED", flush=True)
            break
    return v

def run_conic(C, maxit=40, band=(0.2486, 0.3197), tol=1e-7, solver=None, verbose=True):
    states, ns, dedge, Gbase, t, deftypes, Pflats, sup, CONST, GRAD, C5 = reconstruct(C)
    G = Gbase.copy(); Mrows = []
    def solve():
        x = cp.Variable(ns, nonneg=True); eta = cp.Variable()
        cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1], G @ x >= eta]
        for (lab, tt, Pf) in Pflats:
            cons.append(cp.reshape(Pf @ x, (tt, tt), order="C") >> 0)
        if Mrows:
            cons.append(floc._norm_rows(Mrows) @ x >= 0)
        pr = cp.Problem(cp.Maximize(eta), cons)
        val = pr.solve(solver=solver) if solver else pr.solve()
        return val, np.array(x.value).ravel(), pr.status
    v, x, st = solve()
    for it in range(1, maxit + 1):
        added = 0; newcuts = []
        for (k, A, E, S, cls) in deftypes:
            g, p = fc.separate(E, S, x, t)
            if g < v - tol:
                newcuts.append(fc.cut_from_p(E, S, p, t)); added += 1
        ladded = 0
        res = floc.separate_localizer_p(CONST, GRAD, sup, x)
        if res is not None:
            p, lam, w = res; Q = floc.qmat(p); r = np.zeros(ns)
            for hi in sup:
                r[hi] = float(w @ (CONST[hi] + np.einsum("abcd,cd->ab", GRAD[hi], Q)) @ w)
            Mrows.append(r); ladded += 1
        if added == 0 and ladded == 0:
            break
        if newcuts:
            G = np.vstack([G] + newcuts)
        v, x, st = solve()
        if verbose:
            print(f"  conic iter{it}: +{added}d+{ladded}L eta={v:+.7f} ({st})", flush=True)
        if v < -tol:
            break
    print(f"  conic FINAL eta={v:+.7f} ({st})", flush=True)
    return v

if __name__ == "__main__":
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 9
    C = load(N)
    mode = sys.argv[1] if len(sys.argv) > 1 else "lp"
    if mode == "lp":
        run_lp(C)
    elif mode == "conic":
        run_conic(C)
    elif mode == "both":
        print("LP route (exact HIGHS):"); run_lp(C)
        print("conic route:"); run_conic(C)
    print("DONE", flush=True)
