# Q16 (plateau) — GPT answer (relayed, fresh session) + Step-2 AUDIT (2026-06-21)

User relayed a real GPT-Pro answer to the plateau question (after the first Q16 chat went degenerate).
**This CORRECTS my earlier "1/20 is a fundamental order-16 wall" conclusion** — it is only a wall for the
SHALLOW UNMARKED switching hierarchy, breakable by margin colors + exact separation (NOT 16-color flags).

## GPT verdict: choose (a) — margin-colored lift + margin-conditioned 2-root switches; make separation EXACT.
1/20 is NOT a fundamental limit of the exact single-max-cut formulation (one max cut has all info: mono
edges = β). It is a wall for the present shallow unmarked approximation to max-cut optimality.

## The plateau's "bad Clebsch cut" fingerprint (GPT, to AUDIT)
In Clebsch K (16 even subsets of [5]), the cut A₀={∅,12,13,23,14,24,15,25}, B₀=rest:
e_K=40, cut e(A₀,B₀)=28, mono e(A₀)+e(B₀)=12. Strict 1-vertex local max: 12 vtx have (d_C,d_M,h)=(3,2,1),
4 vtx have (5,0,5) [h=margin=d_C−d_M]. Max cut is 32. Blow-up: x=40/256=5/32=0.15625; d_edge=5/16=0.3125;
d_mono=2·12/256=3/32=0.09375; mono-fraction 12/40=0.30 — MATCHES my pseudo-graphon (d_edge≈0.316, mono-frac
≈0.30). **Rigorous nearby wall 3/64=0.046875 for shallow unmarked switching; my numerical 1/20 is its
weighted/pseudo descendant.** GPT: for k=3 this cut IS detected (so 1/20 NOT a proven exact wall); but the
UNMARKED type-averaged k≤2 hierarchy provably can't beat it (blow-up satisfies every unmarked [0,1] k≤2
profile switch). My coordinate-ascent k≤3 oracle missed the breaking switch (separation was inexact).

## The fix (GPT's recommended path, in order)
1. **Use the bad 28-edge Clebsch cut as a UNIT TEST for the switch oracle.**
2. **EXACT switch separation** — replace coordinate-ascent. For r≤16 profile cells, the separation
   max_{q∈[0,1]^r} S(q), S(q)=2(K1)ᵀq−2qᵀKq (K=conditional signed-edge matrix), is a NONCONVEX box-QP (K
   indefinite). Solve exactly: enumerate 2¹⁶ binary, OR ternary integer-QP, OR box-QP via SCIP/Gurobi.
   Maximizer need NOT be in {0,½,1}. Every real q found gives a valid fixed linear flag inequality.
3. **Margin colors** A_L,A_H,B_L,B_H: H(x)=C(x)−M(x)≥0 (cut-deg − mono-deg); split by threshold t=1/8
   (separates Clebsch margins 1/16 and 5/16). These are NOT free colors — add CONSISTENCY LOCALIZERS:
   linear form: for every rooted indicator flag F, ℓ_c⟨F⟩ ≤ ⟨F·E_cut⟩−⟨F·E_mono⟩ ≤ u_c⟨F⟩ (E_cut/E_mono =
   rooted 2-vertex quantum flags for cut/mono degree); PSD form: ⟨[[F_iF_j(H_σ−ℓ_c)]]⟩, ⟨[[F_iF_j(u_c−H_σ)]]⟩
   PSD. (Precedent: arXiv 2605.05346 colors vertices by a global degree threshold + colored flags.)
4. **The first margin-conditioned switch:** 2-root type = cut edge a∈A_L, b∈B_L, ab∈E;
   p_{a,b}(x)=1[x∈B_L, xa∈E] + 1[x∈A_L, xb∈E]; S_{a,b}=(N(a)∩B_L)∪(N(b)∩A_L); add SW_{a,b}≤0. Uses only 4
   sampled vtx (2 roots + 2 edge endpoints) ⟹ fits order-4 machinery. Destroys the bad cut: e.g. a=13,b=45 ⟹
   S={13,23,45,1245}, flipping gains 4 cut edges (28→32). General identity (to AUDIT): for every switch S,
   **Σ_{v∈S}H(v) + 2e_M(S) − 2e_C(S) ≥ 0**; bad cut has 4 low-margin classes (total margin 4) spanning a K_{2,2}
   cut ⟹ 4−2·4=−4<0 (so the corresponding marked switch is violated, exposing non-optimality). Unmarked roots
   can't align the 12 low-margin classes; the L/H mark does.
5. **Triangle-free degree localizers:** edge xy ⟹ N(x),N(y) disjoint ⟹ d_A(x)+d_A(y)≤a, d_B(x)+d_B(y)≤b
   (a=μ(A),b=μ(B)); per edge-type in M,C notation. Plus d_mono ≤ d_edge − 2∫d(x)² (MaxCut≥Σd_v²/N).
6. If still stuck above 3/32 ⟹ second-stage joint (M,H) binning; if that stalls ⟹ full 16-state Clebsch
   (min-cost-labeling localizers G_{a→b}(x)≥0; the 5 coordinates all matter via Σ_i 1[σ_i(φu)=σ_i(φv)]=1+2c).

## Step-2 AUDIT: [bad-cut fingerprint + general identity to be machine-verified — verify_q16_badcut.py]
## NET: a concrete, tractable plateau-break (margin colors = 4, not 16). My "fundamental wall" was premature.
Step 2 still UNPROVEN; this is a route to push the SDP below 0.09375 toward 0.08.
