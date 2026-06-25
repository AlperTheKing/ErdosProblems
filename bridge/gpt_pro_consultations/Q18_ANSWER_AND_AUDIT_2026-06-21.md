# Q18 ANSWER + AUDIT — 2026-06-21 (GPT Pro "Kapsamlı"; chat 6a370bb0)

GPT's verdict: the d_mono=0.125 point is NOT a genuine max-cut graphon — it is the finite-order shadow
of a HIDDEN-BIPARTITION/color-cloning graphon (a bipartite graphon whose true bipartition is hidden from
the displayed A/B coloring). Exact two-root switching kills it. A PSD-localized BR is valid but unlikely
to bridge the 0.10→0.08 gap. **The 0.10 plateau is a genuine wall for low-root single-cut relaxations.**

## VERIFIED CLAIMS

### ★ SW0-strictness theorem — CONFIRMED (operator proof audited + computational check)
No nonzero triangle-free graphon with a GENUINE max cut can have d_mono = d_cut (SW0 is strict).
Proof: K(x,y)=W(x,y)s(x)s(y) (s=±1 cut signs), ∫K = d_mono−d_cut. Max-cut ⟹ randomized-switching
inequality ⟨f,Kf⟩ ≥ ∫K ∀f∈[−1,1]. If SW0 tight (∫K=0) ⟹ K⪰0. Triangle-free ⟹ Tr(K³)=∫WWW(triangles)=0.
K⪰0 ∧ Tr(K³)=0 ⟹ K=0 ⟹ W=0. ∎
COMPUTATIONAL CHECK (verify inline): over all nonzero triangle-free graphs n≤7, max(mono/cut) at the max
cut = 0.25 (C5: e=5,maxcut=4,mono=1), strictly <1. ⟹ the d_mono=0.125 (SW0-tight, mono=cut) optimum is a
pure missing-global-optimality artifact, NOT a real obstruction.

### The 0.125 obstruction = hidden-bipartition graphon
4-cell graphon: latent ℓ∈{0,1} × displayed c∈{A,B}, each measure 1/4, W=½·1[ℓ≠ℓ']. d_edge=1/4,
d_mono=d_cut=1/8, every vertex h(v)=0 (so margin marks see NOTHING). The displayed A/B is independent of
the true bipartition ℓ → displayed cut is nowhere near max. Explains the empty + single-side-mono states.

### Exact 2-root switch (Section 2) — TESTED, partially confirms GPT
For 2-root ab∈E, a,b same side: P=N(a)∖N(b), Q=N(b)∖N(a) (disjoint, triangle-free); orientations
t=1,2 with p_t as in flag_order5_br.sw2_explicit. On order-6 2-color core:
  +SW0+SW1 = 0.125 → +SW2(my partial, adjacent-same-side only) = **0.1217** → +SW2+BR+EX+degcyl = **0.1192**.
GPT predicted full exact switching → ~0.101 (my SW2 is partial: no non-adjacent types, no BOX-SW
continuous separation). Either way ≫ 0.098.

## ★ STOPPING RULE FIRED
GPT: "If this [2-color order-6 + exact 2-root switching + BOX-SW + SW-PSD + BR-CYL/PSD] system remains at
d_mono ≥ 0.098, STOP the low-root two-color route." My result (0.119, and ~0.101 even with full
switching) ≫ 0.098 ⟹ **STOP the low-root 2-color flag-SDP route.**

## New tools GPT gave (for the record, if revisited)
- **SW-PSD**: K^σ + Δ·p(σ)·I ⪰ 0, Δ=d_cut−d_mono=d_edge−2d_mono≥0; profile-edge matrix; 6×6/8×8 blocks.
- **BOX-SW** exact continuous separation: min_{a∈[−1,1]^r} aᵀK^σa, enumerate ≤3^8 faces (exact 2-root oracle,
  stronger than p∈{0,½,1}).
- **BR-CYL** (order-5): −⟨[[F·𝓑_σ]]⟩ ≥ 0 for order-3 flags F. **BR-PSD** (order-6, two-root only):
  L^{σ,BR}_{ij}=−⟨[[F_iF_j𝓑_σ]]⟩ ⪰ 0 (do NOT impose entrywise signs). Even stronger: localize the two
  orientations separately L^{σ,p_t}⪰0. (mono-P3 BR-PSD needs order 7 — infeasible.)

## ★ STRATEGIC VERDICT (GPT, honest)
- The 0.125 artifact dies with exact 2-root switching → reproduces ~0.10.
- BR-PSD / orientation localizers MAY improve but **unlikely to reach 0.08** (scalar BR already in the
  cone of exact 2-root orientation switches; prior k=3 switching improved 0.101→0.1005; 4-color margin
  also ~0.10; the hidden-bipartition obstruction has h(v)=0 so margin marks are blind to it).
- The 0.10 wall = "missing a coordinated multi-cut structure", more global than first-order margin.
- (c) peeling ALONE cannot close the band: Clebsch blow-up has d_edge=5/16=0.3125 (high min-degree) but
  < BCL threshold 0.3197 → peeling shrinks but doesn't reach the BCL high-density zone.
- (b) analytic: Tr(K³)=0 is structural but no sharp quantitative lemma yet.
- (a) rank-one-LP 4-color order-6: final DIAGNOSTIC only, not expected to reach 0.08.
- **BEST PIVOT: back to the Clebsch/τ_K formulation** where the FIVE correlated cuts are built into the
  objective, not approximated by ever-deeper switch oracles.

## NET (my assessment)
The flag-SDP "direct-β single-displayed-cut" route — the whole session's main effort — **walls at ~0.10**,
confirmed by GPT's structural argument AND my test (stopping rule fired). The SW0-strictness theorem is a
genuine durable result. Step 2 via flag-SDP is essentially closed; the recommended τ_K pivot was already
explored earlier and hit the SAME effective-stability wall (per AUDIT_flagsdp + H2_ATTACK_FINDINGS).
Step 2 is research-grade OPEN with no clear path. Honest Step-2|Step-1 ≈ 8–12%.
