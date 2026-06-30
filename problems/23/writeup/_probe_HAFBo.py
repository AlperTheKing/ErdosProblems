"""Probe: find the H?AFBo] gamma-min cut (N=9, Gamma=50) and print its structure."""
from fractions import Fraction as F
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins

g6 = "H?AFBo]"
n, E = dec(g6)
print("N =", n, "edges =", E)
adj, cuts = gmins(n, E)
print("num gamma-min cuts:", len(cuts))
for ci, side in enumerate(cuts):
    if not Bconn(n, adj, side):
        continue
    st = struct_for_side(n, adj, side)
    if st is None:
        continue
    M, ell, T, mu, cyc = st
    G = sum(F(ell[f])**2 if False else ell[f]**2 for f in M)
    # actually Gamma = sum_v T[v]
    Gamma = sum(T)
    print(f"cut {ci}: side={side} |M|={len(M)} Gamma={Gamma} T={[str(x) for x in T]}")
    print("   bad edges M:", M, "ell:", {f: ell[f] for f in M})
    for f in M:
        print("    f", f, "ncyc", len(cyc[f]), "ell", ell[f])
    break
