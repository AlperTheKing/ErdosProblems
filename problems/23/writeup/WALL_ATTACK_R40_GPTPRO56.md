# WALL ATTACK — R40: EXPLICIT N=78 GRAFTED ROTOR COLLAPSES TO DEFECT 0 (P1 margin 94); SOURCE
# PROLIFERATION INTRINSIC; heavySupportNeighbour_commonBlue_or_detour (compile-ready) KILLS ALL
# POSITIVE-SURPLUS/DOUBLE-STAR ROTORS; P(falsifier) ~15%; NARROWED QUESTION = CUT-TIGHT
# SUPPORT-OVERLAPPING ROTORS
# (GPT-5.6 Pro, 2026-07-12; harvested ~12.1k ch; GPT's stress script SHA b293d746...c4e18e28)

**[CLAUDE GATE HEADER — the instance is FULLY PINNED (sec 1) and my structural gate runs this tick
(_claude_r40_n78_instance_gate.py): counts N=78/|E|=164/|B|=137/|M|=27, tri-free, displayed cut, distances,
row histogram {54:7,63:10,75:1}, 9/8 minimality arithmetic, per-state demand {264,180,180,264} + P1-capacity
recount. Codex gets the FULL production evaluation of the 4 states + the new lemma to compile + the narrowed
generator target. The blow-up maxcut argument (affine per twin class ⟹ monochromatic optimum ⟹ reduces to
the 8-vtx base) is verified by inspection; the σ-additivity identity (19) σ({c,x}) = σ(c)+σ(x)+2·1[cx∈M] for
same-side non-adjacent pairs is elementary (no blue cx by triangle-freeness through common nbr — actually by
same-side; no shared edge to double-count).]**

## The explicit instance (fully pinned)
8 parts × 3 (A,B,P,Q,X,Y,M,V = IDs 0-23); COMPLETE bipartite blue classes A−X, Y−B, P−M, V−Q + square
X−M, M−Y, Y−V, V−X; bad classes A−B, P−Q; graft blue edges 0−6 (a0−p0), 1−9 (a1−q0). Cut: {X,Y,P,Q} | {A,B,M,V}.
Rows: A^M_ij=(a_i,x_i,m_{i+j},y_j,b_j), A^V likewise with v; B^X_ij=(p_i,m_i,x_{i+j},v_j,q_j), B^Y with y
(indices mod 3). Four macro states ω0..ω3 = (A^M,B^X),(A^M,B^Y),(A^V,B^Y),(A^V,B^X).
Support module: r=24, cL=25, cR=26, L={27,28,29}, R={30,31,32}; support edges r−cL, r−cR, cL−ℓ, cR−r′; bads
L×R (9); selected rows (ℓ,cL,r,cR,r′) — the 9/8 inclusion-minimal defect-one family (|E′| ≤ 2+|L′|+|R′|
proper; 9 > 8 full). Locks: per bad k (lex order) five privates 33+5k..37+5k, blue length-6 path between its
endpoints. Bridge: blue 2−34 (connects blue graph without joining selected internal graphs).
Totals: N=78, |B|=137, |M|=27, |E|=164; tri-free; blue connected; all 27 bads at blue distance exactly 4;
rotor row histogram {54:7, 63:10, 75:1}; support bads have unique rows. Maxcut 137 EXACT (blow-up affine →
rotor block 72+2 graft = 74; support block 8 + 9·6 = 62; bridge 1). Γ = 27·25 = 675 exact.

## THE COLLAPSE (anti-falsifier verdict)
Four states: |I_ω|=35 each; ActiveVerts 24/18/18/24; collision demand 264/180/180/264; **Δ(ω)=0 ALL FOUR.**
Same-first ALONE pays every active owner: P1 capacity 3038/2300/2300/3038, minimum per-owner margin 94;
same-first pools have distinct first coordinates ⟹ ownerwise injections automatically globally injective +
component-coherent. Rotor block alone (24 vtx): owner x0 demand 20 vs |P1∪P3∪CB| = 374 (6/340/64); owner m0
20 vs 368. **Source proliferation is intrinsic to activation — the first blocker fires before the support
witness is even attached.**

## Blocker-by-blocker
1. **Pin rows FIRE**: graft preserves distance-4 but the complete DB balloons (54-75 rows/atom); the orbit is
   a tiny subset. Longer pins just move exposure (outside scope ⟹ P4/P5 mass; selected ⟹ same-first mass +
   row alternatives).
2. **DECISIVE — strong-probe dichotomy**: every square-part vertex has σ({c}) = dB−dM = 9. For same-side
   owner-probe pairs, σ({c,x}) = σ(c)+σ(x)+2·1[cx∈M] ≥ 9 ⟹ free pairs are STRONG common-blue sources (≫
   production threshold 2); covered pairs feed rowCompanion/detour. Weak-free engineering CANNOT suppress
   them. K_{t,t} centre: σ = t+1 (K3,3 ⟹ 4). **Compile-ready:
   `heavySupportNeighbour_commonBlue_or_detour (hheavy : 2 ≤ singletonCutLoss supportNbr) :
   (strong common-blue pair, both halves) ∨ CheckedTwoEdgeDetourAt` — kills ALL positive-surplus double-star
   rotor implementations.**
3. **Lock/quiescent FIRES**: a DISJOINT support witness contributes 54 non-co-occurring vertices ⟹ ≥108
   same-first halves per rotor owner vs margin 94. A future falsifier's minimal defect-one family MUST
   overlap the collision-heavy core. Selected-lock alternative recreates P4/P5-vs-selector dilemma.
4. **No positive SCC at all** (defect 0 everywhere); rigidifying the row DB destroys symmetry ∨ maxcut
   certificate ∨ traffic.

## WeakProbeClassTightness interaction (the squeeze)
Evading (19) needs EVERY probe support-neighbour cut-tight (singleton loss ≤ 1); then WPCT forces a whole
attachment class surplus-identically-0. ⟹ **a serious rotor falsifier cannot use positive-surplus centres;
it must live in balanced cut-tight (C5-blow-up-like) geometry — exactly where censuses show LARGE
rowCompanion/FreeHalf pools.** Structural tension identified.

## Honest fork + estimate
Uniform blow-up family: ZERO chance (every state collision-feasible). A real falsifier needs SIMULTANEOUSLY:
support witness overlapping the traffic core; cut-tight probe neighbours; global saturation of all keys;
P4/P5 suppression without selector escapes; detours staying in a positive-defect SCC. GPT has NO such
construction. **Subjective P(genuine canonical falsifier in the family) ≈ 15%.**
**NARROWED QUESTION (R41 target): "Can a cut-tight, support-overlapping active rotor have positive minimum
collision defect?"** Proof route: strengthen heavySupportNeighbour_commonBlue_or_detour globally — cut-tight
attachment classes either expose enough source mass or admit a lower-defect row transition.
