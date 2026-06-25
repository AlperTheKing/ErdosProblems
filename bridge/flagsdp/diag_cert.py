#!/usr/bin/env python3
"""Diagnose the certificate failure: for each kept cut, compare the FLOAT row (used by the cert LP)
against the EXACT regenerated row. The mismatched cut type reveals the bug."""
import sys, pickle
from math import comb
from fractions import Fraction as F
import numpy as np
import flag_exact as fx

N = int(sys.argv[1]) if len(sys.argv) > 1 else 9
C = pickle.load(open(f"cache_n{N}.pkl", "rb"))
D = pickle.load(open(f"certdata_n{N}.pkl", "rb"))
states = C["states"]; sup = list(C["sup"]); t = F(2, 25)
moments = {m[0]: (m[6], m[4], m[2]) for m in C["moments"]}   # lab -> (Pint, s, sigma)
prov = D["prov"]; coeff = D["coeff"]; rows = D["rows"]
keep = [i for i in range(len(coeff)) if coeff[i] > 1e-9]
print(f"kept {len(keep)} cuts; checking float-vs-exact per cut", flush=True)
maxden = 10**6
worst = []
for idx in keep:
    pr = prov[idx]; fl = np.array(rows[idx])
    if pr[0] == "deficit":
        _, k, A, cls, p = pr
        pmap = {cls[i]: F(int(p[i])) for i in range(len(cls))}
        ex = fx.gr_exact(states, k, A, pmap, t)
    elif pr[0] == "deficit_pmap":
        _, k, A, pmap = pr
        ex = fx.gr_exact(states, k, A, pmap, t)
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
        vrat = fx.rat_vec(vv, maxden)
        ex = fx.moment_cut_exact(Pint, vrat, denom)
    else:
        _, sg, w, pL = pr
        ex = fx.localizer_cut_exact(states, sup, sg, fx.rat_vec(w, maxden), fx.rat_vec(pL, maxden), t)
    exf = np.array([float(z) for z in ex])
    err = np.abs(exf - fl).max()
    worst.append((err, idx, pr[0], coeff[idx]))
worst.sort(reverse=True)
print("top mismatches (err, idx, type, coeff):")
for (err, idx, typ, cf) in worst[:12]:
    print(f"  err={err:.3e}  idx={idx}  {typ}  coeff={cf:.3e}  contrib~{err*cf:.2e}")
print(f"total max float row vs exact mismatch contribution sum ~ {sum(e*c for e,_,_,c in worst):.2e}")
