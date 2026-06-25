#!/usr/bin/env python3
"""GPT Q40 (Pick a, CORRECT formulation): EXACT rational certificate  d_mono <= 2/25 + delta  on the band,
via the DUAL MARGIN LP (not a closure-c optimization, not a threshold shift).

Soundness: for the best profile-cut rule, min_r g_r(H) = (best profile-cut mono) - 2/25 >= d_mono(H) - 2/25
(profile-cuts are a SUBSET of all cuts, so leave >= mono than the true max-cut). Hence for any convex combo
lambda (lambda_r>=0, sum=1):   d_mono(H) - 2/25 <= min_r g_r(H) <= sum_r lambda_r g_r(H).
We certify  sum_r lambda_r g_r(H) <= delta  on the band by adding nonneg multiples of the >=0 moment/loc
rows m_j and the band slacks:  for ALL states H,
   sum_r lambda_r g_r(H) + sum_j gamma_j m_j(H) + mu(e_H - lo) + nu(hi - e_H)  <=  delta,
with lambda,gamma,mu,nu >= 0 and sum lambda = 1. On a band graphon the added terms are >=0, so
sum lambda g_r <= delta, giving  d_mono <= 2/25 + delta.  LP optimum delta = eta (contradiction-LP value).
Then rationalize all multipliers and EXACTLY verify max_H LHS <= delta_rational via flag_exact regenerators.
"""
import sys, pickle, time
from math import comb
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import prove_cert as pc
import flag_exact as fx

LO = F(1243, 5000); HI = F(3197, 10000); T = F(2, 25)

def dual_margin_lp(rows, prov, dedge, ns, band=(0.2486, 0.3197), use_loc=False):
    lo, hi = band
    nd_idx = [i for i in range(len(prov)) if prov[i][0] in ("deficit", "deficit_pmap")]
    # exclude localizer cuts by default: their EXACT regeneration (permutations(n,5) x Fraction) is too slow.
    nm_idx = [i for i in range(len(prov)) if prov[i][0] == "moment" or (use_loc and prov[i][0] == "localizer")]
    R = np.array(rows)                          # (nr, ns)
    nd, nm = len(nd_idx), len(nm_idx); nv = nd + nm + 3   # [lambda, gamma, mu, nu, delta]
    cobj = np.zeros(nv); cobj[-1] = 1.0         # minimize delta
    # per-state: sum lambda*g + sum gamma*m + mu(e-lo)+nu(hi-e) - delta <= 0
    A_ub = np.zeros((ns, nv))
    for c, i in enumerate(nd_idx):
        A_ub[:, c] = R[i]
    for c, i in enumerate(nm_idx):
        A_ub[:, nd + c] = R[i]
    A_ub[:, nd + nm] = dedge - lo
    A_ub[:, nd + nm + 1] = hi - dedge
    A_ub[:, nd + nm + 2] = -1.0
    b_ub = np.zeros(ns)
    A_eq = np.zeros((1, nv)); A_eq[0, :nd] = 1.0; b_eq = [1.0]      # sum lambda = 1
    bounds = [(0, None)] * (nd + nm + 2) + [(None, None)]
    r = linprog(cobj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs-ipm")
    if not r.success:
        r = linprog(cobj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    delta = float(r.x[-1]); lam = r.x[:nd]; gam = r.x[nd:nd + nm]; mu = float(r.x[nd + nm]); nu = float(r.x[nd + nm + 1])
    return delta, nd_idx, lam, nm_idx, gam, mu, nu, r.success

def regen(C, states, prov, idx):
    """Exact Fraction values of cut `idx` over all states."""
    pr = prov[idx]
    if pr[0] in ("deficit", "deficit_pmap"):
        if pr[0] == "deficit":
            _, k, A, cls, p = pr; pmap = {cls[i]: F(int(p[i])) for i in range(len(cls))}
        else:
            _, k, A, pmap = pr
        return fx.gr_exact(states, k, A, pmap, T)
    if pr[0] == "moment":
        _, lab, sigma, s, vv = pr
        moments = {m[0]: (m[6], m[4], m[2]) for m in C["moments"]}
        Pint, ss, sg = moments[lab]
        denom = []
        for (n, _A) in states:
            nk = 1
            for i in range(sigma[0]):
                nk *= (n - i)
            d = nk * (comb(n - sigma[0], s) ** 2) if (nk > 0 and n - sigma[0] >= s) else 1
            denom.append(F(int(d)) if d else F(1))
        return fx.moment_cut_exact(Pint, fx.rat_vec(vv, 10**7), denom)
    _, sg, w, pL = pr
    return fx.localizer_cut_exact(states, list(C["sup"]), sg, fx.rat_vec(w, 10**7), fx.rat_vec(pL, 10**7), T)

def main(N=9):
    C = pc.load(N)
    print(f"=== order-{N} EXACT dual-margin cert  d_mono <= 2/25 + delta  (GPT Q40 Pick a) ===", flush=True)
    t0 = time.time()
    states, ns, dedge, t, rows, prov, v = pc.cutting_plane(C, maxit=15, target=-1e-6, mom_maxvecs=8, verbose=False)
    print(f"cutting-plane: eta*={v:+.7e}, {len(rows)} cuts [{time.time()-t0:.0f}s]", flush=True)
    delta, ndix, lam, nmix, gam, mu, nu, ok = dual_margin_lp(rows, prov, dedge, ns)
    print(f"dual-margin LP: delta = {delta:+.7e}  (success={ok}); kept lambda>{1e-9}: {(lam>1e-9).sum()}/{len(lam)}, gamma>{1e-9}: {(gam>1e-9).sum()}/{len(gam)}", flush=True)
    # EXACT verification
    edens = fx.edge_density_exact(states)
    lam_f = [fx.rationalize(x, 10**7) for x in lam]; gam_f = [fx.rationalize(x, 10**7) for x in gam]
    mu_f = fx.rationalize(mu, 10**7); nu_f = fx.rationalize(nu, 10**7)
    slam = sum(lam_f)
    if slam != 1:
        lam_f = [x / slam for x in lam_f]        # renormalize to exact sum 1
    Phi = [mu_f * (edens[i] - LO) + nu_f * (HI - edens[i]) for i in range(ns)]
    for c, i in enumerate(ndix):
        if lam_f[c] != 0:
            vals = regen(C, states, prov, i)
            for j in range(ns):
                if vals[j] != 0:
                    Phi[j] += lam_f[c] * vals[j]
    for c, i in enumerate(nmix):
        if gam_f[c] != 0:
            vals = regen(C, states, prov, i)
            for j in range(ns):
                if vals[j] != 0:
                    Phi[j] += gam_f[c] * vals[j]
    mx = max(Phi); arg = int(np.argmax([float(p) for p in Phi]))
    print(f"EXACT: max_H [ sum lam*g + sum gam*m + band ] = {float(mx):+.7e} = {mx}", flush=True)
    print(f"   => d_mono(G) <= 2/25 + {float(mx):.3e} for ALL triangle-free G in band [0.2486,0.3197]  (EXACT, Fraction)", flush=True)
    print(f"   argmax state {arg}", flush=True)
    with open(f"dual_cert_n{N}.pkl", "wb") as f:
        pickle.dump(dict(prov=prov, ndix=ndix, lam=[str(x) for x in lam_f], nmix=nmix, gam=[str(x) for x in gam_f],
                         mu=str(mu_f), nu=str(nu_f), maxPhi_num=mx.numerator, maxPhi_den=mx.denominator), f, protocol=4)
    print(f"saved dual_cert_n{N}.pkl  (delta_exact = {mx} = {float(mx):.6e})", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
