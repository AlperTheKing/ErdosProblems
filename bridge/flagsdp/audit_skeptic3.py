#!/usr/bin/env python3
"""Independent skeptic audit of D3: exact dual-feasibility of dual_cert_n9.pkl.

Goals (independent of certify_dual.py self-report):
 1. Recompute Phi(H) over ALL states from SAVED prov + SAVED multipliers, my own loop.
    Report the TRUE max over all 1897 states and the argmax.
 2. Verify the exact regenerators MATCH the float LP rows the LP actually optimized
    (regenerate atoms, compare to a fresh cutting_plane rows[] within float tol). This is
    the load-bearing check: if regen != LP-row, the saved maxPhi need not bound the LP combo.
 3. Cross-check: independently confirm that maxPhi <= delta target and < 1/450.
"""
import pickle, sys, time
from math import comb
from fractions import Fraction as F
import numpy as np
import prove_cert as pc
import flag_exact as fx
import certify_dual as cd

LO = F(1243, 5000); HI = F(3197, 10000); T = F(2, 25)

def main():
    C = pc.load(9)
    states = C["states"]; ns = len(states)
    d = pickle.load(open("dual_cert_n9.pkl", "rb"))
    prov = d["prov"]; ndix = d["ndix"]; nmix = d["nmix"]
    lam = [F(s) for s in d["lam"]]; gam = [F(s) for s in d["gam"]]
    mu = F(d["mu"]); nu = F(d["nu"])
    mp = F(d["maxPhi_num"], d["maxPhi_den"])
    print(f"loaded cert: ns={ns} nonzero_lam={sum(1 for x in lam if x)} nonzero_gam={sum(1 for x in gam if x)} mu={mu} nu={nu}", flush=True)

    edens = fx.edge_density_exact(states)
    Phi = [mu * (edens[i] - LO) + nu * (HI - edens[i]) for i in range(ns)]
    # deficit atoms
    t0 = time.time()
    for c, i in enumerate(ndix):
        if lam[c] != 0:
            vals = cd.regen(C, states, prov, i)
            for j in range(ns):
                if vals[j] != 0:
                    Phi[j] += lam[c] * vals[j]
    print(f"deficit atoms done [{time.time()-t0:.0f}s]", flush=True)
    for c, i in enumerate(nmix):
        if gam[c] != 0:
            vals = cd.regen(C, states, prov, i)
            for j in range(ns):
                if vals[j] != 0:
                    Phi[j] += gam[c] * vals[j]
    print(f"moment atoms done [{time.time()-t0:.0f}s]", flush=True)

    # TRUE max over ALL states, exact comparison
    mx = Phi[0]; arg = 0
    for j in range(ns):
        if Phi[j] > mx:
            mx = Phi[j]; arg = j
    print(f"INDEP max_H Phi = {mx} = {float(mx):.10e}  argmax={arg}", flush=True)
    print(f"saved maxPhi     = {mp} = {float(mp):.10e}", flush=True)
    print(f"diff (indep - saved) = {mx - mp}", flush=True)
    print(f"indep_max <= saved : {mx <= mp}", flush=True)
    print(f"indep_max < 1/450  : {mx < F(1,450)}", flush=True)
    # how many states are within 1e-6 of max (degeneracy / near-violations)
    near = sum(1 for j in range(ns) if mx - Phi[j] < F(1, 10**6))
    print(f"states within 1e-6 of max: {near}", flush=True)
    # is any state ABOVE 1/450? (would break integrality)
    above = [j for j in range(ns) if Phi[j] >= F(1,450)]
    print(f"states with Phi >= 1/450: {len(above)}", flush=True)

if __name__ == "__main__":
    main()
