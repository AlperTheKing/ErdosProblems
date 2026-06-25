# Q19 ANSWER + AUDIT — 2026-06-21 (GPT Pro; chat 6a370bb0)

## ★ KEY INSIGHT (changes the picture)
We were using the WRONG formulation. Every "pick ONE globally-optimal coloring, enforce it locally"
relaxation (our 2-color switching, 4-color margin lift) stalls at ~0.10. But **BCL's published UNCOLORED
local-cut method already proves d_mono ≤ 2/23.5 = 0.085106 GLOBALLY** (arXiv:2103.14179) — only 0.005 above
the 0.08 target, and BCL prove the EXACT target OUTSIDE the medium band. So we were BEHIND the published
result the whole session. GPT's decision: **(d) uncolored BCL-style multi-cut SDP + PSD-localized
cut-deficit inequalities.** (NOT τ_K — same wall; NOT spectral as main path — K=SWS has same spectrum as W,
Tr(K³)=0 is just triangle-freeness, no quantitative lemma.)

## The formulation (Section 1)
Rooted triangle-free type σ (k verts). Non-root vertices have adjacency profile α⊆[k] (independent in σ).
Pick p_α∈[0,1]; put each P_α vertex on side 0 w.p. p_α. The constructed-cut mono density:
   C_{σ,p} = Σ_{α,β} (p_α p_β + (1−p_α)(1−p_β)) · E^σ_{αβ}   (E^σ_{αβ} = rooted ordered-edge flag between P_α,P_β).
For EVERY embedding+p, the true max-cut deficit d_mono* ≤ C_{σ,p} (the true max cut beats any constructed
cut). SDP: max z s.t. moment M^ρ(x)⪰0, edge band, z ≤ ⟨C_{σ,p},x⟩ for a family of cut rules. If opt ≤ 2/25,
some cut always hits the target. BCL families: root orders 2,3,4,5 = 10,108,953,125 cuts + a special 6-root
Clebsch cut + a 3K_2 cut.

## ★ The new refinement: PSD cut-deficit localizers (Section 2)
Scalar BCL averages over embeddings → cancellation (exactly our scalar-BR failure). For a counterexample,
g_{σ,p} := C_{σ,p} − (2/25)·1_σ ≥ 0 at EVERY embedding ⟹ the localizer
   L^{σ,p}_{ij} = ⟨[[ F_i F_j g_{σ,p} ]]⟩ ⪰ 0   (v^T L v = ⟨[[(Σv_iF_i)² g_{σ,p}]]⟩ ≥ 0).
BCL's scalar cut = the F_1=1 case. This PSD lift prevents root-environment cancellation (BCL noted extra
scalar cuts gave only marginal gains; localization is materially different). [AUDIT TODO: verify
g_{σ,p}≥0-per-embedding soundness — the counterexample-pointwise claim — like we did for BR.]
Order: cut functional is order k+2; scalar k+2; linear cylinder k+3; PSD localizer k+4. So 6-root cuts:
scalar 8, cylinder 9, PSD 10. Uncolored triangle-free state counts at order 8,9,10 = 410, 1897, 12172
(OEIS A006785) — much smaller than the 45,130 four-color order-6. Use rank-one separation (eval L, find
neg eigenvector v, add v^T L v ≥ 0, iterate) instead of materializing the cones.

## Concrete first computation (Section 3)
1. Reproduce 2/23.5 with BCL scalar cut families in an UNCOLORED SDP.
2. Add the medium band + min-degree core D(v) ≥ 4/25.
3. Record which scalar cuts are active at the pseudo-optimum.
4. PSD-localize ONLY the active ones (start: Clebsch 6-root, 3K_2, active C5-rooted, then orders 2–4).
5. Rank-one localizer cuts until separation stops.
Then add cut-assignment generation: at the pseudo-state, min the box quadratic
   C_σ(p) = Σ_{α,β} w_{αβ}(1 − p_α − p_β + 2 p_α p_β) over p∈[0,1]^r (binary p = weighted profile MaxCut),
rationalize, add its cut + localizer. The ONE question: does medium-band BCL baseline + localized active
cuts make the d_mono=2/25 target system INFEASIBLE?
Tooling: BCL paper arXiv:2103.14179; public C++ pkg github.com/Marcelo-ML/flag-algebras (BCL-style local-cut,
exact rational) — reproducing the baseline doesn't need rebuilding from scratch.

## τ_K identity (Section 4, for record) — why NOT to use it
K = {a∈{±1}^5 : Πa_i=1}; κ(a,b)=(3+Σa_ib_i)/4 ∈{0,1,2}. Σ_i m_i = d_edge + 2 d_K, so d_mono* ≤ (d_edge+2d_K)/5;
target ⟺ d_K + ½d_edge ≤ 1/5. The problem: enforcing φ is a GLOBAL min-cost labeling needs (7) the full
recoloring-kernel inequality; finite-root recoloring tests a tiny subset, and a bounded-order pseudo-coloring
fakes the 5-cut coordination while only locally stable. No finite missing family identified ⟹ no reason a
low-order τ_K SDP crosses 0.10.

## Honest status (Section 6)
The medium band is a genuine open core; no published stability result gives the constant-fraction MaxCut
surplus there (BCL's high-density argument uses min-degree peeling + strong C5-blow-up structure, doesn't
extend down to d_edge≈0.25–0.32). BUT one materially stronger tractable relaxation remains: uncolored local
cuts + medium band + pointwise PSD cut-deficit localization — starts from 0.085 (not 0.10), avoids the
fake-global-coloring obstruction, addresses averaging cancellation. If the order-10 uncolored system with
localized active BCL cuts STILL stays above 0.08 ⟹ write up partials + state the medium band needs a new
idea. Else it closes #23.

## NET / decision
Implement the UNCOLORED local-cut SDP (start small: reproduce << 0.10, aim for 0.085). This is the single
best path and we hadn't tried it (we were stuck on single-displayed-cut). Step-2|Step-1 outlook revised
UP modestly (0.085 baseline is close) but still uncertain — the last 0.005 via localization is unproven.
