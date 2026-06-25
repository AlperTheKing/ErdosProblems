#!/usr/bin/env python3
"""PROTOTYPE step 2 (decisive): does GPT Pro's interval localizer t((K2-a)(b-K2),W)>=0 drop the order-9 bound
below 2/25? The fooling x* spans d_edge [0,0.556] (Var 9.8e-3); the localizer Sum_H x_H (d_edge_H - a)(b - d_edge_H)
>= 0 penalizes out-of-band components, forcing the edge-density variance <= (mean-a)(b-mean). We add it to the
order-9 LP (hom convention t(2K2)=p^2 ~ d_edge^2 for a first prototype) on the full band and on narrow sub-bands,
and report eta. eta<0 on a sub-band => the band bound there is < 2/25 (GPT's route WORKS for Q=K2).
"""
import numpy as np
from scipy.optimize import linprog
import prove_cert as pc

def build_and_solve(states, ns, dedge, rows, prov, band, loc_band=None):
    """Solve max eta s.t. band, deficit g.x>=eta, moment m.x>=0; optionally + localizer (dedge-a)(b-dedge).x>=0
    with loc_band=(a,b)."""
    lo, hi = band
    nv = ns + 1; c = np.zeros(nv); c[-1] = -1.0
    A_ub = []; b_ub = []
    A_ub.append(np.concatenate([-dedge, [0.0]])); b_ub.append(-lo)
    A_ub.append(np.concatenate([dedge, [0.0]])); b_ub.append(hi)
    for i, row in enumerate(rows):
        r = np.asarray(row, float)
        if prov[i][0] in ("deficit", "deficit_pmap"):
            A_ub.append(np.concatenate([-r, [1.0]])); b_ub.append(0.0)
        else:
            A_ub.append(np.concatenate([-r, [0.0]])); b_ub.append(0.0)
    if loc_band is not None:
        a, b = loc_band
        Lrow = (dedge - a) * (b - dedge)            # per-state interval localizer value
        A_ub.append(np.concatenate([-Lrow, [0.0]])); b_ub.append(0.0)   # -L.x <= 0 => L.x >= 0
    A_eq = [np.concatenate([np.ones(ns), [0.0]])]; b_eq = [1.0]
    bounds = [(0, None)] * ns + [(None, None)]
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=bounds, method="highs-ipm")
    if not res.success:
        res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                      bounds=bounds, method="highs")
    return -res.fun if res.success else None, (res.x[:ns] if res.success else None)

def main():
    C = pc.load(9)
    print("cutting_plane (maxit=12)...", flush=True)
    states, ns, dedge, t, rows, prov, v = pc.cutting_plane(C, maxit=12, target=-1e-6, mom_maxvecs=8, verbose=False)
    print(f"cuts={len(rows)}, baseline eta(full band)={v:+.7e}", flush=True)
    FULL = (0.2486, 0.3197)
    eta0, _ = build_and_solve(states, ns, dedge, rows, prov, FULL)
    print(f"[no localizer]   full band eta = {eta0:+.7e}", flush=True)
    # full-band localizer
    etaL, xL = build_and_solve(states, ns, dedge, rows, prov, FULL, loc_band=FULL)
    print(f"[+ interval-loc] full band eta = {etaL:+.7e}  (drop = {eta0-etaL:+.2e})", flush=True)
    # narrow sub-bands with matching localizer
    print("--- narrow sub-bands [a,b] with localizer (a,b) ---", flush=True)
    subs = [(0.2486,0.27),(0.27,0.29),(0.29,0.31),(0.31,0.3197),(0.28,0.31),(0.26,0.30)]
    for (a,b) in subs:
        e,_ = build_and_solve(states, ns, dedge, rows, prov, (a,b), loc_band=(a,b))
        e0,_ = build_and_solve(states, ns, dedge, rows, prov, (a,b))
        tag = "  <<< eta<0 => bound<2/25 here!" if (e is not None and e<0) else ""
        print(f"  [a,b]=[{a:.4f},{b:.4f}] (w={b-a:.3f}): eta no-loc={e0:+.3e}  +loc={e:+.3e}{tag}", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
