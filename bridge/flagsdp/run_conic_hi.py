#!/usr/bin/env python3
"""Conic moment-PSD with k=4 blocks (GPT decision A: moment-consistency hierarchy, exact PSD).
k<=2 (cache) + selected k=4 blocks (moments_hi) + deficit + PSD localizers. Does eta cross <0?"""
import sys, time, pickle
import numpy as np
import cvxpy as cp
import flag_engine as fe
import flag_cutgen as fc
import flag_localizer as floc
import multi_loc as ml

def run(C, H, k4_only=True, band=(0.2486, 0.3197), maxit=30, tol=1e-7):
    states = C["states"]; ns = len(states); dedge = C["dedge"]; t = C["t"]
    deftypes = C["deftypes"]
    Pflats = [(lab, tt, Pf) for (lab, tt, sg, fl, s, Pf, Pi) in C["moments"]]   # k<=2 flat (tt*tt, ns)
    hi_blocks = []
    for b in H["blocks"]:
        if k4_only and b["k"] != 4:
            continue
        Pf = b["Pf"]  # (ns, tt, tt)
        hi_blocks.append((b["name"], b["tt"], Pf.reshape(ns, -1).T.copy()))  # -> (tt*tt, ns)
    print(f"  conic blocks: k<=2 {[l for l,_,_ in Pflats]} + {[l for l,_,_ in hi_blocks]}", flush=True)
    G = C["Gbase"].copy(); Mrows = []
    locs = ml.build_locs(C, ["C5", "C4", "2K2", "P4", "K13"], t)
    def solve():
        x = cp.Variable(ns, nonneg=True); eta = cp.Variable()
        cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1], G @ x >= eta]
        for (lab, tt, Pf) in Pflats:
            cons.append(cp.reshape(Pf @ x, (tt, tt), order="C") >> 0)
        for (lab, tt, Pf) in hi_blocks:
            cons.append(cp.reshape(Pf @ x, (tt, tt), order="C") >> 0)
        if Mrows:
            cons.append(floc._norm_rows(Mrows) @ x >= 0)
        pr = cp.Problem(cp.Maximize(eta), cons)
        import os
        sv = os.environ.get("SOLVER", "")
        val = pr.solve(solver=cp.SDPA) if sv == "SDPA" else pr.solve()
        return val, np.array(x.value).ravel(), pr.status
    v, x, st = solve(); t0 = time.time()
    print(f"  iter0: eta={v:+.7f} ({st})", flush=True)
    for it in range(1, maxit + 1):
        added = 0; newcuts = []
        for (k, A, E, S, cls) in deftypes:
            g, p = fc.separate(E, S, x, t, exhaustive_max=13)
            if g < v - tol:
                newcuts.append(fc.cut_from_p(E, S, p, t)); added += 1
        ladded = 0; lmn = 0.0
        for (nm, sig, CON, GRA, sup) in locs:
            res = floc.separate_localizer_p(CON, GRA, sup, x)
            if res is not None:
                p, lam, w = res; lmn = min(lmn, lam); Q = floc.qmat(p); r = np.zeros(ns)
                for hh in sup:
                    r[hh] = float(w @ (CON[hh] + np.einsum("abcd,cd->ab", GRA[hh], Q)) @ w)
                Mrows.append(r); ladded += 1
        if added == 0 and ladded == 0:
            print(f"  CONVERGED it{it} eta={v:+.7f} ({st})", flush=True); break
        if newcuts:
            G = np.vstack([G] + newcuts)
        v, x, st = solve()
        print(f"  it{it}: +{added}d +{ladded}L eta={v:+.7f} ({st}) Leig={lmn:+.1e} [{time.time()-t0:.0f}s]", flush=True)
        if v < -tol:
            print(f"  it{it}: eta={v:+.7f} < 0 -> CLOSED at t={t}!", flush=True); break
    print(f"FINAL conic-k4 eta={v:+.7f} ({st})", flush=True)
    return v

if __name__ == "__main__":
    C = pickle.load(open("cache_n9.pkl", "rb")); H = pickle.load(open("moments_hi_n9.pkl", "rb"))
    k4only = (len(sys.argv) < 2 or sys.argv[1] != "all")
    print(f"=== order-9 conic moment-PSD k<=2 + k4 (GPT A), k4_only={k4only} ===", flush=True)
    run(C, H, k4_only=k4only)
    print("DONE", flush=True)
