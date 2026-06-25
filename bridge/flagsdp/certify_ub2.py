#!/usr/bin/env python3
"""GPT Q40 (Pick a, fixed): EXACT rational certificate of  d_mono < 2/25 + delta  via SHIFTED THRESHOLD.
Run the prove_cert closure pipeline with t := t0 = 2/25 + 5e-5 (a SAFE rational target). Since the true
order-9 bound is ~+4.3e-5 < 5e-5, the contradiction CLOSES at t0 (eta<0), so certificate_lp gives c>0 and
the exact Fraction verification certifies  max_H Phi(H) < 0  =>  d_mono(H) < t0 = 2/25 + 1/20000  on band.
delta = 1/20000 = 5e-5 (exact rational). Regenerator-backed rows only (deficit + localizer + rank-one
moment), all exactly regenerable via flag_exact with the SAME t0.
"""
import sys, pickle, time
from math import comb
from fractions import Fraction as F
import numpy as np
import prove_cert as pc
import flag_exact as fx

LO = F(1243, 5000); HI = F(3197, 10000)
T0 = F(1601, 20000)        # 2/25 + 1/20000 = 0.08005

def verify_t0(C, states, prov, coeff, a, b, c, t0, maxden=10**7, keep_tol=1e-9):
    moments = {m[0]: (m[6], m[4], m[2]) for m in C["moments"]}   # lab -> (Pint, s, sigma)
    sup = list(C["sup"])
    edens = fx.edge_density_exact(states)
    keep = [i for i in range(len(coeff)) if coeff[i] > keep_tol]
    print(f"  kept {len(keep)}/{len(coeff)} cuts (coeff>{keep_tol})", flush=True)
    Phi = [F(0)] * len(states)
    a_f = fx.rationalize(a, maxden); b_f = fx.rationalize(b, maxden); c_f = fx.rationalize(c, maxden)
    for hi_i in range(len(states)):
        Phi[hi_i] += a_f * (edens[hi_i] - LO) + b_f * (HI - edens[hi_i]) + c_f
    for idx in keep:
        cf = fx.rationalize(coeff[idx], maxden); pr = prov[idx]
        if pr[0] == "deficit":
            _, k, A, cls, p = pr
            pmap = {cls[i]: F(int(p[i])) for i in range(len(cls))}
            vals = fx.gr_exact(states, k, A, pmap, t0)
        elif pr[0] == "deficit_pmap":
            _, k, A, pmap = pr
            vals = fx.gr_exact(states, k, A, pmap, t0)
        elif pr[0] == "moment":
            _, lab, sigma, s, vv = pr
            Pint, ss, sg = moments[lab]
            denom = []
            for (n, _A) in states:
                nk = 1
                for i in range(sigma[0]):
                    nk *= (n - i)
                d = nk * (comb(n - sigma[0], s) ** 2) if (nk > 0 and n - sigma[0] >= s) else 1
                denom.append(F(int(d)) if d else F(1))
            vals = fx.moment_cut_exact(Pint, fx.rat_vec(vv, maxden), denom)
        else:  # localizer
            _, sg, w, pL = pr
            vals = fx.localizer_cut_exact(states, sup, sg, fx.rat_vec(w, maxden), fx.rat_vec(pL, maxden), t0)
        for hi_i in range(len(states)):
            if vals[hi_i] != 0:
                Phi[hi_i] += cf * vals[hi_i]
    mx = max(Phi); arg = int(np.argmax([float(p) for p in Phi]))
    return (mx < 0 and c_f > 0), mx, c_f, arg

def main(N=9):
    C = pc.load(N)
    C["t"] = float(T0)                 # shift threshold for cutting_plane + separation
    print(f"=== order-{N} EXACT cert  d_mono < 2/25 + 1/20000 = {float(T0)}  (shifted-threshold closure) ===", flush=True)
    t0 = time.time()
    states, ns, dedge, t, rows, prov, v = pc.cutting_plane(C, maxit=60, target=-1e-6, mom_maxvecs=12, verbose=True)
    print(f"cutting-plane @ t0: eta*={v:+.7e}, {len(rows)} cuts [{time.time()-t0:.0f}s]", flush=True)
    if v >= 0:
        print(f"eta >= 0 at t0: not closed -> need more cuts / larger t0. STOP.", flush=True); return
    cval, coeff, a, b, c = pc.certificate_lp(rows, dedge, ns)
    print(f"certificate LP: max c = {cval:+.6e}", flush=True)
    if cval <= 0:
        print("c <= 0: cuts insufficient at t0.", flush=True); return
    ok, mx, c_f, arg = verify_t0(C, states, prov, coeff, a, b, c, T0)
    print(f"EXACT: max_H Phi = {float(mx):+.6e} (c_f={float(c_f):.3e}); argmax state {arg}", flush=True)
    if ok:
        print(f"*** EXACT CERTIFICATE VERIFIED: d_mono(G) < 2/25 + 1/20000 = {T0} for ALL triangle-free G in band [0.2486,0.3197] ***", flush=True)
        with open(f"upperbound_cert2_n{N}.pkl", "wb") as f:
            pickle.dump(dict(prov=prov, coeff=coeff, a=a, b=b, c=c, t0_num=T0.numerator, t0_den=T0.denominator,
                             maxPhi_num=mx.numerator, maxPhi_den=mx.denominator), f, protocol=4)
        print(f"saved upperbound_cert2_n{N}.pkl", flush=True)
    else:
        print(f"NOT verified: max_H Phi = {float(mx):+.3e} (rationalization too coarse?)", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
