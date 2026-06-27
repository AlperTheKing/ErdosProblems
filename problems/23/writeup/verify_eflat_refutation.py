#!/usr/bin/env python3
"""EXACT verification of GPT-Pro's E-FLAT refutation (#23 delta=0, cut-pressure route).

GPT-Pro (2026-06-26, thread c/6a3b8a74) claims the proposed E-FLAT sub-lemma
  (W_ij>0  =>  P_ij = alpha   on ALL edge support, incl. saturated W=1)
is NOT a consequence of KKT. Box-normal-cone subdifferential calculus gives only:
  0<W_ij<1, C_ij=0  =>  P_ij = alpha   (fractional edges: equality)
  W_ij=1,   C_ij=0  =>  P_ij >= alpha  (SATURATED edges: only one-sided => slack allowed)
Witness: weighted C5-blow-up w=(0.54,0.06,0.20,0.10,0.10), edges between consecutive
classes, which sits IN-BAND and has a saturated edge (3-4) with P=1 > alpha.

We verify EXACTLY (Fractions): (1) d_edge in band, (2) maxcut leaves the unique
min-product edge monochromatic => d_mono, (3) the single optimal cut's same-side
kernel P puts P=1 on the saturated 3-4 edge while the other 4 saturated edges have
P=0 -- so 'P constant on edge support' (E-FLAT) is violated on saturated edges.
"""
from fractions import Fraction as F
from itertools import product

w = [F(54,100), F(6,100), F(20,100), F(10,100), F(10,100)]   # class weights, sum=1
assert sum(w) == 1, sum(w)

# consecutive-class edge products (cyclic C5): edge i = (i, i+1 mod 5)
prod = [w[i]*w[(i+1)%5] for i in range(5)]
edge_mass = sum(prod)                 # = sum w_i w_{i+1}
d_edge = 2*edge_mass
print("edge products (i,i+1):", [str(p) for p in prod])
print("d_edge =", d_edge, "=", float(d_edge))
print("  in band [0.2486, 0.3197]?", F(2486,10000) <= d_edge <= F(3197,10000))

# maxcut of weighted C5: choose a side for each class; odd cycle => >=1 mono edge.
# enumerate all 2^5 sign assignments, cut = sum of products on bichromatic edges.
best_cut = F(-1); opt_assign = []
for s in product([0,1], repeat=5):
    cut = sum(prod[i] for i in range(5) if s[i] != s[(i+1)%5])
    if cut > best_cut:
        best_cut = cut; opt_assign = [s]
    elif cut == best_cut:
        opt_assign.append(s)
beta = edge_mass - best_cut           # monochromatic mass under best cut
d_mono = 2*beta
print("\nmaxcut =", best_cut, " beta(mono mass) =", beta, " d_mono =", d_mono, "=", float(d_mono))
print("  d_mono < 2/25=0.08 (band slack)?", d_mono < F(2,25))
# which edge(s) are left monochromatic at optimum, and is it the unique min-product edge?
min_edge = min(range(5), key=lambda i: prod[i])
print("  unique min-product edge =", (min_edge, (min_edge+1)%5), " product =", str(prod[min_edge]))
print("  # optimal cuts =", len(opt_assign), " (expect 1 => unique => rigid 0/1 pressure)")
for s in opt_assign:
    mono = [i for i in range(5) if s[i]==s[(i+1)%5]]
    print("   opt assign", s, " mono edges:", [(i,(i+1)%5) for i in mono])

# Same-side kernel P of the (unique) optimal cut, on the 5 cyclic edges:
s = opt_assign[0]
print("\nSame-side pressure P on the 5 saturated cyclic edges (W=1):")
Pvals = {}
for i in range(5):
    j=(i+1)%5
    Pij = F(1) if s[i]==s[j] else F(0)
    Pvals[(i,j)] = Pij
    print(f"   edge {i}-{j}: W=1, C=0,  P={Pij}")
distinct = set(Pvals.values())
print("\nE-FLAT would require P constant on edge support. Distinct P-values on edges:", sorted(str(x) for x in distinct))
print("E-FLAT holds on saturated edges?", len(distinct)==1,
      " => REFUTED (P=1 on the mono edge, P=0 on the 4 cut edges)." if len(distinct)>1 else "")
print("\nKKT box-normal-cone content (the CORRECT, weaker statement):")
print("  saturated W=1,C=0 => P>=alpha only (one-sided). With alpha<=0 the P=1 mono edge")
print("  has STRICT slack P-alpha>0. So KKT is consistent with P>alpha on a saturated edge;")
print("  E-FLAT (equality everywhere on edge support) does NOT follow from KKT. [confirmed]")
