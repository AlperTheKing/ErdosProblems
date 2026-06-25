#!/usr/bin/env python3
"""ADVERSARIAL AUDIT of CLAIM 1: re-derive the balanced k7-only cert with the ORBIT-CORRECTED balance.

GPT's validity proof needs Sigma(W) := sum_{sigma,r} lambda_{sigma,r} S_sigma(W) == 1 for ALL W.
Since sum_sigma orbit_sigma * S_sigma(W) == 1 identically (verified), the CORRECT full-coverage balance
is  sum_r lambda_{sigma,r} = orbit_sigma * alpha_7   (NOT equal-per-labeled-type as in balanced_cert_k7only.py).
This script runs BOTH balance variants on the SAME cut pool and reports both delta'.
If the orbit-corrected delta' < 6.17e-5, CLAIM 1 is REFUTED.
"""
import sys, time, pickle, itertools
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe, flag_cutgen as fc, flag_localizer as floc, cpp_precompute as cpp
from run_k7b import sep_multi
from collections import defaultdict

def orbit_size(k, Asig):
    seen = set()
    for perm in itertools.permutations(range(k)):
        key = []
        for i in range(k):
            row = 0
            for j in range(k):
                if i != j and (Asig[perm[i]] >> perm[j]) & 1:
                    row |= (1 << j)
            key.append(row)
        seen.add(tuple(key))
    return len(seen)

def main(band=(0.2486, 0.3197), sep_iters=4, tol=1e-7, seed=0):
    np.random.seed(seed)
    C = pickle.load(open("cache_n9.pkl", "rb"))
    states = C["states"]; ns = len(states); dedge = C["dedge"]; t = C["t"]
    Pmom = [(lab, tt, Pf.T.reshape(ns, tt, tt)) for (lab, tt, sg, fl, s, Pf, Pi) in C["moments"]]
    lo, hi = band
    cpp.compile_cpp()
    types7 = fe.enumerate_graphs(7, triangle_free=True)
    print(f"k=7: {len(types7)} types; precomputing...", flush=True); t0 = time.time()
    dt7 = [(7, A, *cpp.precompute_type_cpp(states, 7, A, nthreads=32)) for (k, A) in types7]
    orb = {('k7', ti): orbit_size(7, A) for ti, (k, A) in enumerate(types7)}
    print(f"  [{time.time()-t0:.0f}s] orbit sizes computed (sum={sum(orb.values())})", flush=True)
    alltypes = [(7, ('k7', ti), E, S, cls) for ti, (k, A, E, S, cls) in enumerate(dt7)]

    Gdef = []; Gtype = []; Mrows = []
    def solve_primal():
        c = np.zeros(ns + 1); c[-1] = -1.0; Aeq = np.zeros((1, ns + 1)); Aeq[0, :ns] = 1.0
        ub = [np.concatenate([-dedge, [0.0]]), np.concatenate([dedge, [0.0]])]; ubb = [-lo, hi]
        parts = [np.array(ub)]
        if Gdef:
            Gd = np.asarray(Gdef); parts.append(np.concatenate([-Gd, np.ones((Gd.shape[0], 1))], axis=1))
        if Mrows:
            Mn = floc._norm_rows(Mrows); parts.append(np.concatenate([-Mn, np.zeros((Mn.shape[0], 1))], axis=1))
        A_ub = np.vstack(parts); b_ub = np.array(ubb + [0.0] * (A_ub.shape[0] - 2))
        r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=Aeq, b_eq=[1.0], bounds=[(0, None)] * ns + [(None, None)], method="highs-ipm")
        if not r.success: r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=Aeq, b_eq=[1.0], bounds=[(0, None)] * ns + [(None, None)], method="highs")
        return (-float(r.fun), np.asarray(r.x[:ns])) if r.success else (0.0, np.ones(ns) / ns)
    v, x = solve_primal()
    seen = set()
    for it in range(1, sep_iters + 1):
        added = 0
        for (k, tid, E, S, cls) in alltypes:
            ps, gs = sep_multi(E, S, x, t, 1e9, tol, keep=1)
            for p in ps:
                key = (tid, tuple(p))
                if key in seen: continue
                seen.add(key); Gdef.append(fc.cut_from_p(E, S, p, t)); Gtype.append((k, tid)); added += 1
        for (lab, tt, P) in Pmom:
            mr, _, _ = fc.separate_moment(P, x, maxvecs=4)
            for r in mr: Mrows.append(r)
        v, x = solve_primal()
        print(f"sep it{it}: pool={len(Gdef)} cuts eta={v:+.7e}", flush=True)
        if added == 0: break
    print(f"unbalanced eta={v:+.7e}, pool {len(Gdef)} cuts over {len(set(Gtype))} types", flush=True)

    nC = len(Gdef); nM = len(Mrows)
    by_type = defaultdict(list)
    for i, (k, tid) in enumerate(Gtype): by_type[(k, tid)].append(i)
    G = np.asarray(Gdef); Mn = floc._norm_rows(Mrows) if Mrows else np.zeros((0, ns))

    def run_dual(mode):
        # mode 'equal': sum_r lam = alpha (same per labeled type); 'orbit': sum_r lam = orbit_sigma*alpha
        # single alpha for k=7 only; constraint sum over types of (rhs) ... we fix Sigma==1:
        #  equal:  sum_r lam_sigma = a for all sigma; normalization sum_sigma a*S_sigma is NOT 1 -> just use the
        #          original script's normalization: alpha_7=1 means a is a free var with the "sum_k alpha=1" => a appears as alpha.
        #          Reproduce original: sum_r lam = alpha7 ; alpha7 = 1 (since only k=7). => a=1.
        #  orbit:  sum_r lam_sigma = orbit_sigma * alpha7 ; choose alpha7 so that Sigma(W)=sum_sigma orbit_sigma*alpha7*S_sigma
        #          = alpha7 * 1 = alpha7. Need Sigma==1 => alpha7=1. So sum_r lam_sigma = orbit_sigma.
        nv = nC + nM + 2 + 1  # [lam | gam | mu | nu | delta]   (alpha folded: fixed)
        A_ub = np.zeros((ns, nv))
        A_ub[:, :nC] = G.T
        if nM: A_ub[:, nC:nC + nM] = Mn.T
        A_ub[:, nC + nM] = dedge - lo; A_ub[:, nC + nM + 1] = hi - dedge; A_ub[:, -1] = -1.0
        b_ub = np.zeros(ns)
        Aeq = []; beq = []
        for (k, tid), idxs in by_type.items():
            row = np.zeros(nv)
            for i in idxs: row[i] = 1.0
            Aeq.append(row)
            beq.append(1.0 if mode == 'equal' else float(orb[tid]))
        c = np.zeros(nv); c[-1] = 1.0
        bounds = [(0, None)] * (nC + nM + 2) + [(None, None)]
        r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=np.array(Aeq), b_eq=np.array(beq), bounds=bounds, method="highs-ipm")
        if not r.success: r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=np.array(Aeq), b_eq=np.array(beq), bounds=bounds, method="highs")
        return (r.x[-1] if r.success else None, r.status, r.message)

    thr = 2.0 / (25 * 36 * 36)
    de, st, ms = run_dual('equal')
    do, st2, ms2 = run_dual('orbit')
    print(f"\n>>> EQUAL-per-labeled-type delta' = {de if de is None else f'{de:+.7e}'} (status {st})", flush=True)
    print(f">>> ORBIT-corrected (Sigma==1) delta' = {do if do is None else f'{do:+.7e}'} (status {st2})", flush=True)
    print(f"    threshold 2/(25*36^2) = {thr:.6e}", flush=True)
    if do is not None:
        print(f"    ORBIT delta' < threshold ? {do < thr}  => N<=180 {'RECOVERED => CLAIM REFUTED' if do < thr else 'NOT recovered => CLAIM holds'}", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
