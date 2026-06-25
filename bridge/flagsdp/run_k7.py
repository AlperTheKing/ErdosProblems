#!/usr/bin/env python3
"""GPT Q42: the LAST finite route -- EXHAUSTIVE k=7 scalar cut separation at order 9.
Add deficit rules for all 107 triangle-free 7-vertex root types sigma (A006785(7)=107). For each, the
profile-cut deficit g_{sigma,p} = (mono on the 2 non-root vertices under cut p) - (2/25) S_sigma, with up
to 2^7-DOF profile-cuts -- the richest order-9 cut family, attacking the diagnosed cut-floor directly
(moment cones / Q-T+2D do not). Contradiction LP: max eta s.t. sum x=1, band, eta<=g_r.x for ALL rules
(k<=5 base + k=7) + rank-one moment cuts >=0. eta<0 => CLOSURE (then exact cert). If eta>0 after full k=7
separation => Step 2 is beyond credible SDP routes (GPT's stop criterion) -> redirect to Step-1 Lean.
"""
import sys, time, pickle
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe
import flag_cutgen as fc
import cpp_precompute as cpp

def precompute_k7(states, nthreads=32):
    cpp.compile_cpp()
    types7 = fe.enumerate_graphs(7, triangle_free=True)
    print(f"  {len(types7)} triangle-free 7-vertex root types (expect 107)", flush=True)
    out = []
    t0 = time.time()
    for i, (k, A) in enumerate(types7):
        E, S, cls = cpp.precompute_type_cpp(states, 7, A, nthreads=nthreads)
        out.append((7, A, E, S, cls))
        if (i + 1) % 20 == 0:
            print(f"    precomputed {i+1}/{len(types7)} types [{time.time()-t0:.0f}s]", flush=True)
    print(f"  k=7 precompute done [{time.time()-t0:.0f}s]", flush=True)
    return out

def run(band=(0.2486, 0.3197), maxit=60, tol=1e-7):
    C = pickle.load(open("cache_n9.pkl", "rb"))
    states = C["states"]; ns = len(states); dedge = C["dedge"]; t = C["t"]
    deftypes = C["deftypes"]                     # k<=5
    Pmom = [(lab, tt, Pf.T.reshape(ns, tt, tt)) for (lab, tt, sg, fl, s, Pf, Pi) in C["moments"]]
    print("precomputing k=7 deficit types...", flush=True)
    dt7 = precompute_k7(states)
    alltypes = list(deftypes) + dt7
    print(f"  total deficit types: {len(deftypes)} (k<=5) + {len(dt7)} (k=7) = {len(alltypes)}", flush=True)
    Gdef = [C["Gbase"][i] for i in range(C["Gbase"].shape[0])]
    Mrows = []
    lo, hi = band
    import flag_localizer as floc
    def solve():
        c = np.zeros(ns + 1); c[-1] = -1.0
        Aeq = np.zeros((1, ns + 1)); Aeq[0, :ns] = 1.0
        ub = [np.concatenate([-dedge, [0.0]]), np.concatenate([dedge, [0.0]])]; ubb = [-lo, hi]
        Gd = np.asarray(Gdef)
        A1 = np.concatenate([-Gd, np.ones((Gd.shape[0], 1))], axis=1)
        parts = [np.array(ub), A1]
        if Mrows:
            Mn = floc._norm_rows(Mrows)
            parts.append(np.concatenate([-Mn, np.zeros((Mn.shape[0], 1))], axis=1))
        A_ub = np.vstack(parts); b_ub = np.array(ubb + [0.0] * (A_ub.shape[0] - 2))
        r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=Aeq, b_eq=[1.0], bounds=[(0, None)] * ns + [(None, None)], method="highs-ipm")
        if not r.success or r.x is None:
            r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=Aeq, b_eq=[1.0], bounds=[(0, None)] * ns + [(None, None)], method="highs")
        return (-float(r.fun), np.asarray(r.x[:ns])) if (r.success and r.x is not None) else (0.0, np.ones(ns) / ns)
    v, x = solve(); t0 = time.time()
    print(f"iter0 (with k=7 types available): eta={v:+.7e}", flush=True)
    for it in range(1, maxit + 1):
        added = 0; a7 = 0
        for (k, A, E, S, cls) in alltypes:
            nc = E.shape[1]
            g, p = fc.separate(E, S, x, t, exhaustive_max=16)
            if g < v - tol:
                Gdef.append(fc.cut_from_p(E, S, p, t)); added += 1
                if k == 7:
                    a7 += 1
        madded = 0; mn = 0.0
        for (lab, tt, P) in Pmom:
            mr, lam2, _ = fc.separate_moment(P, x, maxvecs=8); mn = min(mn, lam2)
            for r in mr:
                Mrows.append(r); madded += 1
        if added == 0 and madded == 0:
            print(f"CONVERGED it{it} eta={v:+.7e}", flush=True); break
        v, x = solve()
        print(f"it{it}: +{added}d (k7={a7}) +{madded}m eta={v:+.7e} meig={mn:+.1e} [{time.time()-t0:.0f}s]", flush=True)
        if v < -tol:
            print(f"it{it}: eta={v:+.7e} < 0 -> CLOSED (LP>=SDP rigorous, float)! save for exact cert", flush=True)
            with open("k7_cert_state.pkl", "wb") as f:
                pickle.dump(dict(Gdef=[r.tolist() for r in Gdef], Mrows=[r.tolist() for r in Mrows], eta=v), f, protocol=4)
            break
    print(f"FINAL k=7 eta={v:+.7e}", flush=True)
    if v >= 0:
        print("eta >= 0 after k=7 separation -> per GPT: Step 2 beyond credible SDP routes; pivot to Step-1 Lean.", flush=True)
    return v

if __name__ == "__main__":
    print("=== order-9 EXHAUSTIVE k=7 scalar cut separation (GPT Q42, last finite route) ===", flush=True)
    run()
    print("DONE", flush=True)
