#!/usr/bin/env python3
"""INDEPENDENT soundness audit of the order-9 dual certificate dual_cert_n9.pkl, for the Step-1 closure claim
(a(30)<=36, a(25)<=25 via uniform blow-up + delta < 1/450). Verifies the TWO conditions the soundness rests on:
 (1) MOMENT NONNEG: every USED moment atom m_j(H) = v^T M^sigma(H) v >= 0 over ALL 1897 order-9 states (exact F).
 (2) DEFICIT LOWER BOUND: every USED deficit atom g_r(H) >= d_mono(H) - 2/25, where d_mono(H) is the TRUE
     (integer max-cut) mono-density of the order-9 graph H. (k=0 has no root restriction; k>=1 may carry an
     O(k/n) finite-size slack but the graphon-limit soundness needs g_r >= profile-mono - 2/25 >= d_mono-2/25,
     since the fractional profile-cut's E[mono] >= min-mono = d_mono.)
Also reports which k-values and how many atoms are actually used.
"""
import pickle
from fractions import Fraction as F
import numpy as np
import prove_cert as pc
import flag_exact as fx
import certify_dual as cd

T = F(2, 25)

def true_dmono(n, A):
    """exact d_mono(H) = 2*(e - MaxCut)/n^2 for order-n graph H (brute max cut)."""
    adj = [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]
    e = sum(len(adj[u]) for u in range(n)) // 2
    best = -1
    for m in range(1 << (n-1)):
        c = 0
        for u in range(n):
            su = (m >> u) & 1
            for v in adj[u]:
                if v > u and su != ((m >> v) & 1): c += 1
        if c > best: best = c
    return F(2*(e-best), n*n)

def main():
    cert = pickle.load(open("dual_cert_n9.pkl", "rb"))
    prov = cert["prov"]; ndix = cert["ndix"]; nmix = cert["nmix"]
    lam = [F(x) for x in cert["lam"]]; gam = [F(x) for x in cert["gam"]]
    C = pc.load(9)
    states, ns, dedge, t, rows, prov2, v = pc.cutting_plane(C, maxit=15, target=-1e-6, mom_maxvecs=8, verbose=False)
    print(f"loaded cert: {len(ndix)} deficit atoms, {len(nmix)} moment atoms; {ns} states", flush=True)
    # used atoms
    used_def = [(c, ndix[c]) for c in range(len(lam)) if lam[c] != 0]
    used_mom = [(c, nmix[c]) for c in range(len(gam)) if gam[c] != 0]
    kvals = sorted(set(prov[i][1] for (c, i) in used_def))
    print(f"USED deficit atoms: {len(used_def)} (k-values present: {kvals}); USED moment atoms: {len(used_mom)}", flush=True)

    # (1) MOMENT NONNEG
    print("--- (1) moment-row nonnegativity (used moment atoms >= 0 over all states) ---", flush=True)
    worst_m = None; nneg = 0
    for (c, i) in used_mom:
        vals = cd.regen(C, states, prov, i)
        mn = min(vals)
        if mn < 0:
            nneg += 1
            if worst_m is None or mn < worst_m: worst_m = mn
    print(f"  used moment atoms: {len(used_mom)}; atoms with a NEGATIVE value: {nneg}; worst min = {worst_m}", flush=True)

    # (2) DEFICIT LOWER BOUND vs TRUE d_mono
    print("--- (2) deficit g_r(H) >= d_mono(H) - 2/25  (true integer max-cut d_mono) ---", flush=True)
    dmono = [true_dmono(n, A) for (n, A) in states]
    worst_by_k = {}
    for (c, i) in used_def:
        k = prov[i][1]
        vals = cd.regen(C, states, prov, i)
        for j in range(ns):
            slack = vals[j] - (dmono[j] - T)   # want >= 0
            if k not in worst_by_k or slack < worst_by_k[k][0]:
                worst_by_k[k] = (slack, j, states[j][0])
    for k in sorted(worst_by_k):
        sl, j, nj = worst_by_k[k]
        print(f"  k={k}: worst (g_r - (d_mono-2/25)) over states = {float(sl):+.5e} (>=0 means deficit is a valid lower bound) at state {j} (n={nj})", flush=True)
    allok = all(worst_by_k[k][0] >= 0 for k in worst_by_k)
    print(f"  => deficit lower-bound g_r >= d_mono-2/25 holds for ALL used k: {allok}", flush=True)
    print(f"SUMMARY: moment-neg atoms={nneg} (want 0); deficit-lowerbound-ok={allok}", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
