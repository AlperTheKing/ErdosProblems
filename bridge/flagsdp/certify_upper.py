#!/usr/bin/env python3
"""GPT Q34 step 1: FREEZE + EXACT-CERTIFY the rational upper bound  d_mono <= 2/25 + delta  on the band.
Reuses prove_cert's cutting_plane (regenerator-backed rows: deficit + rank-one moment + localizer; NO
conic cones) + certificate_lp, but interprets the optimum c<0 as an UPPER bound: if exact arithmetic
verifies  max_H [ sum coeff*rows(H) + a(e-lo)+b(hi-e) + c ] <= 0  with c<0, then for every band graphon
  d_mono(H) - 2/25 = min_r g_r(H) <= sum coeff_r g_r(H) <= -c - (nonneg)  ==>  d_mono <= 2/25 + (-c).
delta := -c (exact Fraction). This is the rigorous SDP-side input for GPT's stability squeeze.
"""
import sys, pickle, time
from fractions import Fraction as F
import numpy as np
import prove_cert as pc

def main(N=9):
    C = pc.load(N)
    print(f"=== order-{N} EXACT UPPER-BOUND certificate  d_mono <= 2/25 + delta  ===", flush=True)
    t0 = time.time()
    # cap iterations so the certificate LP + EXACT verification actually complete (the bound delta is a
    # bit looser than the it83 +4.24e-5, but it is a VERIFIED rational upper bound, which is the point).
    states, ns, dedge, t, rows, prov, v = pc.cutting_plane(C, maxit=18, target=-1.0, mom_maxvecs=10, verbose=True)
    print(f"cutting-plane done: eta*={v:+.7e}, {len(rows)} cuts [{time.time()-t0:.0f}s]", flush=True)
    cval, coeff, a, b, c = pc.certificate_lp(rows, dedge, ns)
    print(f"certificate LP optimum c = {cval:+.7e}  (=> float upper bound delta ~ {-cval:.3e})", flush=True)
    # EXACT verification: max_H Phi(H) <= 0 with c = cval (may be < 0). delta = -c_f.
    ok, mx, c_f = pc.build_and_verify(C, states, prov, coeff, a, b, c, maxden=10**7, verbose=True)
    delta = -c_f
    print(f"EXACT: max_H Phi = {float(mx):+.6e}; c_f = {float(c_f)} ; delta = -c_f = {float(delta):.6e}", flush=True)
    if mx <= 0:
        print(f"CERTIFIED (exact, Fraction):  d_mono <= 2/25 + {delta}  =  2/25 + {float(delta):.3e}  on band [0.2486,0.3197]", flush=True)
        with open(f"upperbound_cert_n{N}.pkl", "wb") as f:
            pickle.dump(dict(prov=prov, coeff=coeff, a=a, b=b, c=c, delta_num=delta.numerator, delta_den=delta.denominator,
                             maxPhi_num=mx.numerator, maxPhi_den=mx.denominator), f, protocol=4)
        print(f"saved upperbound_cert_n{N}.pkl", flush=True)
    else:
        print(f"NOT certified: max_H Phi = {float(mx):+.3e} > 0 (rationalization too coarse or cuts insufficient)", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 9)
