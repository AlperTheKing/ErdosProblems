# net_H(v) ≤ 3  reduced to three local atoms  (high-side load-PSC half)

**Context.** δ=0 (Γ≤N²) via the load-PSC twin needs POS-SUPPORT-CONTAINMENT on the high side,
which reduces (split-net, blocks 300–308) to the pointwise cap

    net_H(v) := B_out(v) − M_out(v) ≤ 3   for every v in a scoped high band H.

Scope: γ-min connected-B max cut of a triangle-free graph; (M,ell,T,mu,cyc)=struct_for_side;
positive support {T>0} meets ≥2 K-components; H={u : T[u] > t_j} with 2 t_j ≥ N.
Edge tallies at v: B_in/B_out = cut (bichromatic) edges to inside/outside H; M_in/M_out =
monochromatic (bad) edges to inside/outside H. dB=B_in+B_out, dM=M_in+M_out, lip(v)=dB−dM.

## The three atoms (all EXACT-verified, 0 violations on the full battery — _l123.py)

- **(L1)** δ_M(H)=0 : the overload superlevel H carries no monochromatic edge ⇒ **M_in(v)=0** ∀v∈H.
- **(L2)** an *isolated* high vertex (B_in=M_in=0) has **dM_total=1 and dB_total≤4**.
- **(L3)** *every* high vertex satisfies the weak max-cut local slack **dB_total − dM_total ≤ 4**.

Battery = full census N≤11 (all γ-min cuts) + blowups N≤26 + iterated Mycielskians (C5→Grötzsch→Myc N=23)
+ glued-island gadgets. Scoped points=24, isolated=15. Equality cases:
L2 dB=4: (C7|Grötzsch, j5, v17, dM=1, T=815/63). L3=4: unique, NON-isolated
(C7|Grötzsch, j5, v11, dB=4, dM=0, B_in=2, M_in=0) where net=B_out−M_out=2 (the two internal B-edges absorb it).

## net_H(v) ≤ 3  ⟸  (L1)∧(L2)∧(L3)   — 4 lines

By (L1), M_in(v)=0 for all v∈H. Hence
    lip(v) = (B_in+B_out) − (M_in+M_out) = B_in + (B_out − M_out) = B_in(v) + net_H(v),
so
    net_H(v) = lip(v) − B_in(v).                                            (∗)

- **Isolated** (B_in=0): net_H = lip = dB − dM, and (L2) gives dM=1, dB≤4 ⇒ net_H ≤ 3.
- **Non-isolated**: M_in=0 (L1) forces the inside-edge to be a cut edge, so B_in≥1; by (∗) and (L3),
  net_H = lip − B_in ≤ lip − 1 ≤ 4 − 1 = 3.

∎  net_H(v) ≤ 3.

## Status

The reduction net_H≤3 ⟸ L1∧L2∧L3 is a closed, mechanical argument (above). The remaining genuinely
analytic content is the standalone proof of the **three local atoms** L1, L2, L3, each a statement about a
γ-min max cut of a triangle-free graph restricted to a high-load superlevel:

- (L1) = the load-superlevel coarea/CD fact δ_M(H_s) ≤ δ_B(H_s) specialized to overload (M-side empty there);
- (L2)/(L3) = singleton / weak max-cut local-slack bounds tied to odd-girth ≥ 5 (badlen=5 bundle).

These are Codex's leg (proof-driver); this file is the gating contract — the assembled net_H≤3 lemma plus
the three atom proofs are to be checked as one unit. Exact gate is exhausted here (one witness family,
C7|Grötzsch); all numeric content holds with 0 violations.
