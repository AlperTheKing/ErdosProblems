#!/usr/bin/env python3
"""D4 SKEPTIC part 3: DECISIVE consistency check on n=9.
Reconstruct the FULL Phi(H) = sum lam g + sum gam m + band from the SAVED cert
(dual_cert_n9.pkl) using certify_dual.regen, and confirm:
  (1) max_H Phi(H) == delta (the saved maxPhi)  -> cert internally consistent
  (2) the moment part sum_gam_m(H) is NEGATIVE at the deficit-heavy states
      (so chain (c) 'm_j>=0 pointwise' is FALSE; nonneg only holds at graphon level)
  (3) my independent sum_lam_g matches the deficit part of Phi exactly.
"""
import pickle, time
from math import comb
from fractions import Fraction as F
import numpy as np
import prove_cert as pc
import flag_exact as fx
import certify_dual as cd

LO = F(1243, 5000); HI = F(3197, 10000); T = F(2, 25)

def main():
    d = pickle.load(open('dual_cert_n9.pkl', 'rb'))
    prov = d['prov']; ndix = d['ndix']; nmix = d['nmix']
    lam = [F(s) for s in d['lam']]; gam = [F(s) for s in d['gam']]
    mu = F(d['mu']); nu = F(d['nu'])
    delta = F(int(d['maxPhi_num']), int(d['maxPhi_den']))
    print("loaded cert. delta =", float(delta), " mu,nu =", float(mu), float(nu))

    t0 = time.time()
    C = pc.load(9)
    states = list(C["sup"]) if "sup" in C else None
    # certify_dual.regen needs states list; reconstruct from C
    import flag_engine as fe
    states = fe.enumerate_graphs(9, triangle_free=True)
    ns = len(states)
    print("n=9 states:", ns, " load+enum", round(time.time()-t0), "s")

    edens = fx.edge_density_exact(states)
    # deficit part
    defpart = [F(0)]*ns
    for c, i in enumerate(ndix):
        if lam[c] != 0:
            vals = cd.regen(C, states, prov, i)
            for j in range(ns):
                if vals[j] != 0:
                    defpart[j] += lam[c]*vals[j]
    print("deficit part done", round(time.time()-t0), "s")
    # moment part
    mompart = [F(0)]*ns
    for c, i in enumerate(nmix):
        if gam[c] != 0:
            vals = cd.regen(C, states, prov, i)
            for j in range(ns):
                if vals[j] != 0:
                    mompart[j] += gam[c]*vals[j]
    print("moment part done", round(time.time()-t0), "s")

    band = [mu*(edens[j]-LO) + nu*(HI-edens[j]) for j in range(ns)]
    Phi = [defpart[j] + mompart[j] + band[j] for j in range(ns)]

    mx = max(Phi)
    print("RECONSTRUCTED max_H Phi =", float(mx), " == saved delta?", mx == delta)
    print("  exact max numerator/denominator match:", mx.numerator == int(d['maxPhi_num']) and mx.denominator == int(d['maxPhi_den']))

    # how many states have deficit part > delta, and what is moment part there?
    over = [j for j in range(ns) if defpart[j] > delta]
    print("states with deficit_part > delta:", len(over))
    neg_mom = sum(1 for j in over if mompart[j] < 0)
    print("  of those, moment_part < 0 (pulls back down):", neg_mom, "/", len(over))
    if over:
        jw = max(over, key=lambda j: defpart[j])
        print("  worst-deficit state j=", jw)
        print("    deficit_part =", float(defpart[jw]))
        print("    moment_part  =", float(mompart[jw]), " (NEGATIVE => chain(c) pointwise-m>=0 is FALSE)")
        print("    band         =", float(band[jw]))
        print("    Phi          =", float(Phi[jw]), " <= delta?", Phi[jw] <= delta)
    # global min moment part (confirm moments go negative pointwise)
    mnmom = min(mompart)
    print("global min moment_part over n=9 =", float(mnmom))
    print("global max moment_part over n=9 =", float(max(mompart)))

if __name__ == "__main__":
    main()
