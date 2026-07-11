# WALL ATTACK — R20 (TWO-PART reply): base-only Hall FALSE (311-vtx CE) + row-companion repair;
# LP bridge decomposed exactly — the ONE uncontrolled term = h_boundary (dual-weighted cut functional)
# (GPT-5.6 Pro, 2026-07-11, HARVESTED VIA IN-APP BROWSER — reply split into two assistant messages)

**[CLAUDE GATE HEADER:**

## R20a — transfer-matching layer
- **VERDICT: BASE-ONLY (sameFirst + commonBad) Hall-completeness is FALSE.** Obstruction = corridor-overloaded
  vertex: internal corridor of many ℓ=5 rows with few bad neighbours. Necessary condition at overloaded v
  (derived from the accepted identity F_v − C_v = K(N−T(v)) + reach caps):
  **2(T(v)−N) + deg_I(v) ≤ 2·d_bad(v)(d_bad(v)−1)** (6). No graph identity forces it.
- **311-vtx CANONICAL CE**: archived 167-vtx active-circuit cage + C5-blow-up attachment at active path
  vertex v=9, parts (8,64,1,64,8) [P0–P1–{v}–P3–P4–P0], bad class P4×P0 (64 new bad edges); every shortest
  row passes through v, NO new bad edge incident to v. N=311, |B|=1359, |Hbad|=92, |E|=1451;
  maxcut = 207+1152 = 1359 (one-vertex sum adds; attachment classes 512,64,64,512,64, displayed cut leaves
  one 64-class uncut — exact enumeration claimed); Γ = 92·25 = 2300 min (blue dist 4 everywhere, even ≥4
  forced). T(v) = 25 + 64·5 = 345 ⟹ T−N = 34; deg_I(v)=2, d_bad(v)=2 (unchanged: attachment meets old graph
  only at v; N_bad(v)={5,13} permanently Free = 4K half-slots). **Base-only Hall gap = K(2·34+2−4) = 66K.**
  [MY ARITHMETIC CHECK: T=345 ✓, T−N=34 ✓, gap 66K ✓, |E|=235+1216 ✓, |Hbad|=28+64=92 ✓, Γ=2300 ✓,
  attachment edge total 1216 = 512+64+64+512+64 ✓, 1216−64=1152 ✓; attachment-maxcut=1152 exactness +
  Γ-min + tri-free = GATE ITEMS.] Claimed SHAs: py 76b594f6…, json 42275b6b… — gate queued.
- **LOSS ≥ 0 IS AUTOMATIC** (9): for EVERY vertex set S, maximality of the displayed cut gives
  |Hbad∩δ(S)| ≤ |B∩δ(S)|, i.e. loss(S) ≥ 0. [TRIVIALLY VERIFIED: switching S changes cut size by
  |Hbad∩δ(S)|−|B∩δ(S)| ≤ 0. ✓] ⟹ the common-bad-neighbour condition was ONLY an ownership rule, never
  needed for the loss inequality.
- **THIRD BASE PATTERN (minimal repair): ROW-COMPANION PAIR TERMINAL** — Free ordered pair (x,z), x≠z, with
  Companion_ω(v,x) ∧ Companion_ω(v,z) (each lies on a selected row through owner v; Freeness forces the two
  witnesses onto DISTINCT rows); switch S={x,z}, loss ≥ 0 automatic; capacity justified by the Free
  half-slot. Full Lean structure **CheckedRowCompanionBaseTerminal** given (fields: leftAtom/rightAtom,
  owner_left/right ∈ row verts, source_left/right ∈ row verts, distinct, switchSet={left,right},
  loss_nonneg, owner_active); HitNeed match ⟹ kind .c5Base, support {owner}, capQ 1/(2K), sourceId =
  encodeFreeHalfKey; collision match cancels (no token). STRICTLY generalizes common-bad-neighbour.
- **EXACT REPAIR of 311**: distinct x,z ∈ P0 — every P0 vertex is an endpoint of attachment atoms whose
  every selected row passes v ⟹ row-companions of v in every ω; no selected row contains two P0 vertices ⟹
  all 8·7=56 ordered pairs permanently Free; loss({x,z}) = 128−16 = 112 ✓ [my check: blue deg 64 to P1 ×2;
  bad deg 8 to P4 ×2 ✓]; 33 orbits × 2K = 66K exactly repairs (8). **ZERO prune steps.**
- Fixture separation: 167/175 have empty HitNeed (enough vertex slack; T=35/40 vs N=167/175); 3892 passes
  with commonBad only; **311 separates**: sameFirst+commonBad FAILS, +rowCompanion PASSES.
- **COMPLETE TRANSFER CHECKER** (spec): 3 base patterns (sameFirst | commonBad | rowCompanion) → exact
  capacitated bipartite matching on orbits (source→obligationOrbit mult; obligationOrbit→freeOrbit INF iff
  direct witness; freeOrbit→sink mult; INF = 1+Σmult; integral max-flow expands to injective half-slot
  matching). Prune stage ONLY on residual failure (explicit old/new rows, actual shortest, injective slot
  map, exact n_ω recomputation, strictly decreasing LOCAL row-rewrite rank — global Γ is NOT a valid rank —
  component preservation), then recompute reachability and rerun. Staged gate sequence: sameFirst →
  +commonBad → +rowCompanion → +prune closure; run on 167, 175, 3892, 311, then census. Falsifier export
  (12): orbit set Z with mult(Z) > mult(ReachFree(Z)) + full witnesses + per-rejection first failed Boolean.
- Lean soundness shape **checkedBaseCorridorPruneMatching_to_activeFullBank** (consumes tri-free + maximum
  cut + CheckedTransferMatching over sameFirst ∪ commonBad ∪ rowCompanion ∪ checkedPruneReachability;
  produces ActiveComponentFullBankCert via EndpointReserveHall_to_fullBank; noDoubleSpend from sourceOf
  injectivity, component from trace, legality from terminal, reserve from slot counts).
- **NEW SHARP QUESTION (GPT's own)**: does stage 3 (three base patterns) ALWAYS produce a full matching on
  canonical cages, or is checked prune transport genuinely necessary?

## R20b — LP-bridge layer (my retask's actual question: trace terms → cutAlpha−cutBeta−cutGamma identity)
- **EXACT DECOMPOSITION (compilable NOW against my BankedWallLP)**: for any checked dual d, minimal closed
  deficient shore P, ANY partial routing u : P×N(P) → ℚ≥0 extracted from terminal trace pieces (u=0
  allowed — no existence theorem needed), and any cut X:
  **cutGap_d(X) = scaledDeficiency_d(L,P) + R_Δ(P,u,X) + R_D2(u) + R_cap(P,u)** (4)/(5), where
  M_d(P,u) = Σ_p (L(p)−u_P(p))·γ(p); R_D2 = Σ u(p,s)(δ(s)−γ(p)) ≥ 0 [legality ⟹ γ(p)≤δ(s), checked];
  R_cap = Σ_s (cap(s)−u_N(s))·δ(s) ≥ 0; R_Δ = Λ_d(X) − M_d(P,u) with Λ_d(X) = cutAlpha_d−cutBeta_d−cutGamma_d.
  Sufficient (weakest) inequality (8): **M_d(P,u) ≤ Λ_d(X) + R_D2 + R_cap**. Lean theorems given:
  scaledDeficiency_cutGap_decomposition (proof = unfold + ring) and
  scaledDeficiency_cutGap_of_boundary_bound (hboundary ⟹ Def_d(P) ≤ cutGap_d(X), by linarith).
- **THE FIRST UNCONTROLLED TERM = h_boundary = R_Δ**: the trace proves loss(S) = |B∩δ(S)|−|Hbad∩δ(S)| ≥ 0
  (UNWEIGHTED) + ordinal rank decrease; the needed quantity is the DUAL-WEIGHTED functional
  Λ_d(S) = Σ_{a∈δ} α(a) − Σ_{e∈δ} β(e) − Σ_{p∈δ} γ(p). **No implication (15)⟹(16)**: explicit example —
  boundary with one bad + two blue edges, loss = 1 > 0; weights (α,β)=(1/10, 2/5) give Λ_d = −7/10 < 0;
  weights (4/5, 1/20) give +7/10. Same combinatorial trace, sign flips. Γ-rank decrease is ORDINAL —
  termination only, contributes NO rational summand. Tri-free validates geometry; max-cut validates
  unweighted loss (primal token capacity); NEITHER prices the boundary with α,β,γ.
- **Symmetric-difference composition fails too** (18)/(19): X = S_1 ⊕…⊕ S_q leaves TWO exact signed errors —
  Σ_i Λ_d(S_i) − M_d (not signed by max-cut loss) and the parity correction 2(Σk_a α − Σk_e β − Σk_p γ)
  (unsigned: mixed signs).
- **MINIMAL EXACT FALSIFIER GATE (h_boundary)**: per shore P + checked dual d: D = Def_d(P) > 0;
  G_trace = max Λ_d over the affine F2-span of {initial owner/corner cut, all trace switch sets, all
  producer wall rows}; G_max = max Λ_d over ALL allowed cuts. Verdicts: D > G_max ⟹ the ENTIRE desired cut
  conclusion is false on that instance (decisive); D > G_trace ⟹ current trace assembly falsified;
  G_trace < D ≤ G_max ⟹ cut exists but the R18/R19 record does not construct it. Certificate fields listed
  (P, L, γ, sinks, cap, δ, u, M_d, R_D2, R_cap, masks, both maximizers, α/β/γ totals, rational gap, parity
  counts).
- **BOTTOM LINE (verbatim tail): "The sink and routing portions are closed. The exact remaining
  quantitative bridge is h_boundary; the present transfer/switch record does not establish it."**

## MY RECONCILIATION + NEXT
- The wall is now TWO precisely-separated layers sharing one spine: (L1) transfer-matching
  Hall-completeness — now with a THIRD base pattern and the sharp stage-3 question; (L2) h_boundary — the
  dual-weighted cut-realization bridge, which NO amount of unweighted switch bookkeeping can close;
  it needs either a cut-construction rule from the owner atlas/switch masks or a new checked trace field
  priced in (α,β,γ).
- L1 and L2 have INDEPENDENT finite falsifier gates (staged matching gate; D-vs-G_trace-vs-G_max gate) —
  both census-checkable; fixtures first: 167, 175, 3892, 311.
- MY LANES: (i) gate the 311 CE (script _claude_r20_311_gate.py: build graph, tri-free, maxcut=1359 exact
  [attachment enumeration], Γ=2300 min, T(v)=345, base-only gap 66K, row-companion repair 66K, loss 112);
  (ii) implement the staged 4-pattern matching gate; (iii) compile scaledDeficiency_cutGap_decomposition
  into BankedWallLP (Codex lane candidate — compile-ready); (iv) h_boundary falsifier gate on fixtures;
  (v) retask R21 = the h_boundary cut-construction question (L2 is now the innermost wall).**]
