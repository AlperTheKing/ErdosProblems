#!/usr/bin/env python3
"""GPT Q25 choice B: order-9, add cut-deficit localizers for k=4 types {C4,2K2,P4,K13} (+ existing C5),
p-separated negative-eigenvector rank-one cuts, full moment-PSD (conic) -> TRUE order-9 value.
If eta<0, hand off to prove_cert (multi-loc) for the exact rational certificate."""
import sys, time, pickle
import numpy as np
import cvxpy as cp
import flag_engine as fe
import flag_cutgen as fc
import flag_localizer as floc

SIGS = {
    "C5": (5, fe.adj_from_edges(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])),
    "C4": (4, fe.adj_from_edges(4, [(0, 1), (1, 2), (2, 3), (3, 0)])),
    "2K2": (4, fe.adj_from_edges(4, [(0, 1), (2, 3)])),
    "P4": (4, fe.adj_from_edges(4, [(0, 1), (1, 2), (2, 3)])),
    "K13": (4, fe.adj_from_edges(4, [(0, 1), (0, 2), (0, 3)])),
}

def build_locs(C, names, t):
    states = C["states"]; t0 = time.time()
    locs = []
    # C5 from cache
    if "C5" in names:
        sup = list(C["sup"]); Csup = C["Csup"]; Gsup = C["Gsup"]
        CONST = {hi: Csup[i] for i, hi in enumerate(sup)}; GRAD = {hi: Gsup[i] for i, hi in enumerate(sup)}
        locs.append(("C5", C["C5"], CONST, GRAD, sup))
    for nm in names:
        if nm == "C5":
            continue
        sig = SIGS[nm]
        CONST, GRAD, classes, sup = floc.precompute_localizer_affine(states, sig, t)
        locs.append((nm, sig, CONST, GRAD, sup))
        print(f"  localizer affine [{nm}] |sup|={len(sup)} nc={len(classes)} [{time.time()-t0:.0f}s]", flush=True)
    return locs

def run_conic(C, names, band=(0.2486, 0.3197), maxit=40, tol=1e-7, verbose=True):
    states = C["states"]; ns = len(states); dedge = C["dedge"]; t = C["t"]
    deftypes = C["deftypes"]
    Pflats = [(lab, tt, Pf) for (lab, tt, sigma, flags, s, Pf, Pint) in C["moments"]]
    G = C["Gbase"].copy(); Mrows = []
    locs = build_locs(C, names, t)
    print(f"  built {len(locs)} localizers [{','.join(n for n,_,_,_,_ in locs)}]", flush=True)
    # cylinder rows (GPT Q26-C) for C5: pool of p -> rows; add violated ones each iter
    C5 = C["C5"]; classes5 = fc.profile_classes(*C5); sup5 = list(C["sup"])
    cyl_pool = {}
    def add_cyl(p):
        key = tuple(np.round(p, 6))
        if key in cyl_pool:
            return
        cyl, _ = floc.cylinder_rows(states, C5, p, t, classes5, sup5)
        cyl_pool[key] = list(cyl.values())
    for p in floc.c5_extremal_ps(classes5):
        add_cyl(p)
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
                if nm == "C5":
                    add_cyl(np.asarray(p))   # cylinder rows at the C5 localizer's worst p
        # binding C5 deficit cut's p -> cylinder rows
        for (k, A, E, S, cls) in deftypes:
            if k == 5:
                _, p5 = fc.separate(E, S, x, t)
                add_cyl(np.array([float(p5[i]) for i in range(len(classes5))]))
        cadded = 0; wc = 0.0
        for rows in cyl_pool.values():
            for row in rows:
                vr = float(row @ x)
                if vr < -1e-9:
                    Mrows.append(row); cadded += 1; wc = min(wc, vr)
        if added == 0 and ladded == 0 and cadded == 0:
            print(f"  conic CONVERGED it{it} eta={v:+.7f} ({st})", flush=True); break
        if newcuts:
            G = np.vstack([G] + newcuts)
        v, x, st = solve()
        if verbose:
            print(f"  conic it{it}: +{added}d +{ladded}L +{cadded}cyl eta={v:+.7f} ({st}) Leig={lmn:+.1e} wcyl={wc:+.1e} [{time.time()-t0:.0f}s]", flush=True)
        if v < -tol:
            print(f"  conic it{it}: eta={v:+.7f} < 0 -> CLOSED (conic) at t={t}!", flush=True); break
    print(f"FINAL conic order-9 multi-loc eta={v:+.7f} ({st})", flush=True)
    return v

if __name__ == "__main__":
    C = pickle.load(open("cache_n9.pkl", "rb"))
    names = sys.argv[1].split(",") if len(sys.argv) > 1 else ["C5", "C4", "2K2", "P4", "K13"]
    print(f"=== order-9 conic + localizers {names} (GPT Q25 choice B) ===", flush=True)
    run_conic(C, names)
    print("DONE", flush=True)
