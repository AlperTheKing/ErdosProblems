#!/usr/bin/env python3
"""Option-A probe: strengthen order-9 moment-PSD with k=3 (and optionally k=4) blocks (bigger flags,
the higher diagonal level) on top of the existing k<=2 blocks + deficit + 5 PSD localizers + cylinder.
Standard flag-SDP strengthening WITHIN order 9. Does it close the +3.0e-5 wall?"""
import sys, time, pickle
from math import comb
import numpy as np
import cvxpy as cp
import flag_engine as fe
import flag_sdp as fs
import flag_cutgen as fc
import flag_localizer as floc

def k3_blocks(states, ns):
    """Compute k=3 moment blocks (3K1, K2+K1, P3), flags on 6 (s=3). Returns [(lab,tt,Pf)]."""
    specs = [("3K1", (3, [0, 0, 0])), ("K2K1", (3, fe.adj_from_edges(3, [(0, 1)]))),
             ("P3", (3, fe.adj_from_edges(3, [(0, 1), (1, 2)])))]
    out = []; t0 = time.time()
    for lab, sigma in specs:
        flags = fs.enumerate_flags(sigma, 6); tt = len(flags)
        mats = fs.P_sigma(9, states, sigma, flags)
        Pf = np.zeros((tt * tt, ns))
        for hi, (n, _A) in enumerate(states):
            nk = 1
            for i in range(3):
                nk *= (n - i)
            denom = nk * (comb(n - 3, 3) ** 2) if (nk > 0 and n - 3 >= 3) else 1.0
            Pf[:, hi] = (mats[hi] / (denom if denom > 0 else 1.0)).flatten()
        out.append((lab, tt, Pf))
        print(f"  k3 block {lab}: {tt}x{tt} [{time.time()-t0:.0f}s]", flush=True)
    return out

def run(C, names, k3, band=(0.2486, 0.3197), maxit=30, tol=1e-7):
    states = C["states"]; ns = len(states); dedge = C["dedge"]; t = C["t"]
    deftypes = C["deftypes"]
    Pflats = [(lab, tt, Pf) for (lab, tt, sigma, flags, s, Pf, Pint) in C["moments"]]
    Pflats = Pflats + k3
    G = C["Gbase"].copy(); Mrows = []
    # PSD localizers
    import multi_loc as ml
    locs = ml.build_locs(C, names, t)
    C5 = C["C5"]; classes5 = fc.profile_classes(*C5); sup5 = list(C["sup"])
    cyl_pool = {}
    def add_cyl(p):
        key = tuple(np.round(p, 6))
        if key in cyl_pool: return
        cyl, _ = floc.cylinder_rows(states, C5, p, t, classes5, sup5); cyl_pool[key] = list(cyl.values())
    for p in floc.c5_extremal_ps(classes5): add_cyl(p)
    print(f"  moment blocks: {[ (l,tt) for (l,tt,_) in Pflats]}", flush=True)
    def solve():
        x = cp.Variable(ns, nonneg=True); eta = cp.Variable()
        cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1], G @ x >= eta]
        for (lab, tt, Pf) in Pflats:
            cons.append(cp.reshape(Pf @ x, (tt, tt), order="C") >> 0)
        if Mrows:
            cons.append(floc._norm_rows(Mrows) @ x >= 0)
        pr = cp.Problem(cp.Maximize(eta), cons); val = pr.solve()
        return val, np.array(x.value).ravel(), pr.status
    v, x, st = solve(); t0 = time.time()
    print(f"  iter0 (full moment hierarchy, no loc): eta={v:+.7f} ({st})", flush=True)
    for it in range(1, maxit + 1):
        added = 0; newcuts = []
        for (k, A, E, S, cls) in deftypes:
            g, p = fc.separate(E, S, x, t, exhaustive_max=13)
            if g < v - tol:
                newcuts.append(fc.cut_from_p(E, S, p, t)); added += 1
        ladded = 0; lmn = 0.0
        for (nm, sig, CONST, GRAD, sup) in locs:
            res = floc.separate_localizer_p(CONST, GRAD, sup, x)
            if res is not None:
                p, lam, w = res; lmn = min(lmn, lam); Q = floc.qmat(p); r = np.zeros(ns)
                for hi in sup:
                    r[hi] = float(w @ (CONST[hi] + np.einsum("abcd,cd->ab", GRAD[hi], Q)) @ w)
                Mrows.append(r); ladded += 1
                if nm == "C5": add_cyl(np.asarray(p))
        cadded = 0
        for rows in cyl_pool.values():
            for row in rows:
                if float(row @ x) < -1e-9:
                    Mrows.append(row); cadded += 1
        if added == 0 and ladded == 0 and cadded == 0:
            print(f"  CONVERGED it{it} eta={v:+.7f} ({st})", flush=True); break
        if newcuts: G = np.vstack([G] + newcuts)
        v, x, st = solve()
        print(f"  it{it}: +{added}d +{ladded}L +{cadded}cyl eta={v:+.7f} ({st}) Leig={lmn:+.1e} [{time.time()-t0:.0f}s]", flush=True)
        if v < -tol:
            print(f"  it{it}: eta={v:+.7f} < 0 -> CLOSED at t={t}!", flush=True); break
    print(f"FINAL order-9 + k3-moments eta={v:+.7f} ({st})", flush=True)
    return v

if __name__ == "__main__":
    C = pickle.load(open("cache_n9.pkl", "rb"))
    print("=== order-9 + k=3 moment blocks + localizers + cylinder (option A) ===", flush=True)
    k3 = k3_blocks(C["states"], len(C["states"]))
    names = ["C5", "C4", "2K2", "P4", "K13"]
    run(C, names, k3)
    print("DONE", flush=True)
