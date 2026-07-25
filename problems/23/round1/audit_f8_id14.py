"""Identify the true a(14) witness and compare with the report's claim."""
from fractions import Fraction
from audit_f8_lib import (g6dec, g6enc, canon_str, cayleyZ, edges, bip_exact, blowup,
                          mono_masks, psi_int, trifree, maximal_tf, twinfree)

W = 'L?`DAboU`w@{hS'          # my a(14)=7 witness pattern (13 vertices)
C = 'LhEIHEPQHGaPaP'          # report's Circ(13;1.5)
nW, aW = g6dec(W)
nC, aC = g6dec(C)
n5, a5 = cayleyZ(13, [1, 5])
print("witness  :", W, "n=", nW, "deg seq", sorted(bin(x).count('1') for x in aW),
      "m=", len(edges(nW, aW)), "bip=", bip_exact(nW, aW))
print("Circ(13;1,5) from file:", C, "deg", sorted(bin(x).count('1') for x in aC),
      "m=", len(edges(nC, aC)), "bip=", bip_exact(nC, aC))
print("cayleyZ(13,[1,5]) g6 =", g6enc(n5, a5), " equals file's Circ(13;1.5)?",
      g6enc(n5, a5) == C)
cw, cc = canon_str(nW, aW), canon_str(nC, aC)
print("canon(witness) =", cw)
print("canon(C13(1,5))=", cc)
print("witness isomorphic to C13(1,5)? ", cw == cc)
print("witness maximal-TF/twinfree/TF:", maximal_tf(nW, aW), twinfree(nW, aW), trifree(nW, aW))

EW, MW = mono_masks(nW, aW)
print("\nPsi(witness, one part doubled) for each vertex:")
vals = []
for i in range(13):
    a = [1] * 13
    a[i] = 2
    vals.append(psi_int(EW, MW, a))
print(vals, " max =", max(vals))
g = blowup(nW, aW, [2 if i == vals.index(max(vals)) else 1 for i in range(13)])
print("14-vertex blow-up: n,m =", g[0], len(edges(*g)), " bip =", bip_exact(*g),
      " ratio =", Fraction(bip_exact(*g)[0], 196), " g6 =", g6enc(*g))

EC, MC = mono_masks(nC, aC)
print("\nPsi(C13(1,5), one part doubled) for each vertex:",
      [psi_int(EC, MC, [2 if j == i else 1 for j in range(13)]) for i in range(13)])
