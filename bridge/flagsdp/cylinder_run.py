#!/usr/bin/env python3
"""GPT Q26-C: order-9 + edge/non-edge-split two-spectator CYLINDER localizers C^eps_{ab}>=0 for the
binding C5 cut. Strictly stronger than the PSD localizer (L=C^0+C^1). Scalar LP rows. Does it close?
Conic = full moment-PSD; deficit cuts; cylinder rows added (every row negative at optimizer), iterate."""
import sys, time, pickle
import numpy as np
import cvxpy as cp
import flag_engine as fe
import flag_cutgen as fc
import flag_localizer as floc

def run(C, band=(0.2486, 0.3197), maxit=40, tol=1e-7, use_conic=True, verbose=True):
    states = C["states"]; ns = len(states); dedge = C["dedge"]; t = C["t"]
    deftypes = C["deftypes"]
    Pflats = [(lab, tt, Pf) for (lab, tt, sigma, flags, s, Pf, Pint) in C["moments"]]
    C5 = C["C5"]; classes5 = fc.profile_classes(*C5); sup5 = list(C["sup"])
    G = C["Gbase"].copy(); Mrows = []
    # find the C5 deftype (for binding-cut separation)
    c5def = None
    for (k, A, E, S, cls) in deftypes:
        if k == 5:
            c5def = (E, S, cls)
    pool = {}  # p-key -> cylinder rows dict
    def add_cyl_for_p(p):
        key = tuple(np.round(p, 6))
        if key in pool:
            return pool[key]
        cyl, _ = floc.cylinder_rows(states, C5, p, t, classes5, sup5)
        pool[key] = cyl
        return cyl
    # seed pool with extremal C5 cuts + all-half + p=0
    for p in floc.c5_extremal_ps(classes5):
        add_cyl_for_p(p)
    add_cyl_for_p(np.full(len(classes5), 0.5))
    add_cyl_for_p(np.zeros(len(classes5)))

    def solve():
        x = cp.Variable(ns, nonneg=True); eta = cp.Variable()
        cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1], G @ x >= eta]
        if use_conic:
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
        # binding C5 cut -> add its cylinder rows to the pool
        if c5def is not None:
            g5, p5 = fc.separate(c5def[0], c5def[1], x, t)
            pv = np.array([float(p5[i]) for i in range(len(classes5))])
            add_cyl_for_p(pv)
        # add every cylinder row negative at x*
        cadded = 0; worst = 0.0
        for key, cyl in pool.items():
            for rk, row in cyl.items():
                val_row = float(row @ x)
                if val_row < -1e-9:
                    Mrows.append(row); cadded += 1; worst = min(worst, val_row)
        if added == 0 and cadded == 0:
            print(f"  CONVERGED it{it} eta={v:+.7f} ({st})", flush=True); break
        if newcuts:
            G = np.vstack([G] + newcuts)
        v, x, st = solve()
        if verbose:
            print(f"  it{it}: +{added}d +{cadded}cyl eta={v:+.7f} ({st}) worstcyl={worst:+.1e} rows={len(Mrows)} [{time.time()-t0:.0f}s]", flush=True)
        if v < -tol:
            print(f"  it{it}: eta={v:+.7f} < 0 -> CLOSED at t={t}!", flush=True); break
    print(f"FINAL cylinder order-9 eta={v:+.7f} ({st})", flush=True)
    return v

if __name__ == "__main__":
    C = pickle.load(open("cache_n9.pkl", "rb"))
    conic = (len(sys.argv) < 2 or sys.argv[1] != "lp")
    print(f"=== order-9 + cylinder localizers (GPT Q26-C), conic={conic} ===", flush=True)
    run(C, use_conic=conic)
    print("DONE", flush=True)
