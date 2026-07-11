# WALL ATTACK — R41: P1 MASS PINCER FALSE (companions cancel); NEW PROVABLE LEMMA
# cutTightActiveStar_strongProbe_or_detour (star inequality — NO weak-free branch at cut-tight owners);
# SURVIVOR PINNED TO t=3/N=15/|M|=9 WINDOW; remaining invariant = noPositiveDefectFullyCoveredCutTightStar;
# GPT P(falsifier) ~10%
# (GPT-5.6 Pro, 2026-07-12, "worked 16m58s"; harvested ~12.7k ch)

**[CLAUDE GATE HEADER — the star inequality is VERIFIED BY INSPECTION: S = {v} ∪ N_B(v); N_B(v) independent
(triangle-freeness); internal edges of S = exactly the k blue star edges; loss(S) = σ(v) + Σσ(a) − 2k ≥ 0 ⟹
Σ_{a∈N_B(v)} σ(a) ≥ 2k − σ(v) ≥ 2k−1 at cut-tight v; pigeonhole (σ(x)=1 ⟹ Σ≤1; σ(x)=0 ⟹ Σ≤k−1; both < 2k−1
for k≥2) forces some y with covered pair OR σ(x)+σ(y)≥2; loss({x,y}) = σ(x)+σ(y) exactly (xy ∉ E by
tri-freeness) ⟹ PRODUCTION threshold met. Covered branch = R37 detour machinery (positions differ 2, v∉Q by
co-occurrence). SOUND. The P1-identity D_v − P1_v = 10r(v) − 2N + deg_I(v) kills my pincer — accepted. The
t=3 window goes to the falsifier gate as THE structured-family target (N=15 — small enough for aggressive
enumeration). My R42 lever (posted): in the window deg_I(v)=1, ANY star detour inserts v into the row ⟹ vx
becomes SUPPORT ⟹ v deactivates ⟹ demand drops (strict trade) UNLESS the removed edges xm, m·s_i activate a
compensating region — the activation ledger must balance EXACTLY, and the star theorem then applies to the
NEW owner. R42 = prove the activation-ledger imbalance.]**

## 1. Cut-tightness identities
σ(v) = dB(v) − dM(v) ≥ 0 (maxcut). Cut-tight: σ(v) ≤ 1 ⟹ k = t or t+1. Active ⟹ k ≥ 2 ⟹ t ≥ 1:
**every cut-tight active owner is a bad-edge endpoint.**

## 2-3. THE STAR THEOREM (new, provable now)
Σ_{a∈N_B(v)} σ(a) ≥ 2dB(v) − σ(v)  (star switch, N_B(v) independent, no internal bads)  — at cut-tight v:
≥ 2k−1. ⟹ for active neighbour x, SOME y ∈ N_B(v)\{x} has n(x,y) > 0 (⟹ genuine two-edge detour: same side,
positions differ exactly 2, v ∉ Q, completeness) or n(x,y) = 0 ∧ σ(x)+σ(y) ≥ 2 (⟹ loss({x,y}) = σ(x)+σ(y) ≥ 2
⟹ BOTH halves production-strength common-blue, unreserved). **NO WEAK-FREE BRANCH.** Lean shapes:
CutTightStarProbeResult (strongCommonBlue with loss_ge_two | twoEdgeDetour) +
`cutTightActiveStar_strongProbe_or_detour (htri hmax) (hactive : activeInternalAdj ω owner activeNbr)
(htight : singletonCutLoss owner ≤ 1) : Nonempty (CutTightStarProbeResult …)`.
This CLOSES the σ-gap exactly where the falsifier had to live (cut-tight classes).

## 4. Anchored mass consequences
r(v) ≥ t (t distinct anchored rows); c(v) ≤ 1+4r(v); C_v = 5r(v) − c(v) ≥ t−1 (LINEAR only).
Endpoint-diversity P3 floor: 4(C(t,2) − q_v) half-sources; q_v ≤ 3|M| (weak in equality regime).

## 5. P1 pincer FALSE
D_v = 2(5r(v) − c(v)); P1_v = 2(N − c(v)) − deg_Iact(v) ⟹ **D_v − P1_v = 10r(v) − 2N + deg_I(v)** — c(v)
CANCELS. Positive P1 pressure ⟺ 5r(v) > N − deg_I(v)/2 (an owner can keep ~N/5 zero-companions and still be
P1-deficient). Shore form: D(Z) − P1(Z) = 10r(Z) − 2N|Z| + d_I(Z); positivity ⟹ N|Z| < 25|M| + d_I(Z)/2 — no
contradiction at equality scale 25|M| = N².

## 6-7. THE PARAMETER WINDOW (falsifier-gate target)
t ≥ 3, N = 5t, |M| = t²; owner v: dB = dM = t, r(v) = t, deg_I(v) = 1 ⟹ σ(v)=0, P1 pressure = 10t−10t+1 = 1.
q_v = C(t,2) fully covered (rows needed ⌈C(t,2)/3⌉ ≤ t²) ⟹ P3 floor 0; covered pairs → detours (the neutral
mechanism). **Smallest: t=3, N=15, |M|=9** — incidence target: N_B(v) = {x,s0,s1}, N_M(v) = {y0,y1,y2},
vx ∈ I_ω, anchored rows through v use only s0,s1, selected rows cover {x,s0},{x,s1}, all detours equal-defect
in one SCC, same nine atoms realize the 9/8 minimal circuit (NO disjoint witness). Realization must satisfy
SIMULTANEOUSLY: anchored induced rows, tri-freeness, genuine maxcut, full probe-pair coverage, no lower-defect
state, no P4/P5 exposure, global coherent saturation.

## 8. The actual remaining invariant
`noPositiveDefectFullyCoveredCutTightStar (C : CheckedSinkNeutralAttachmentClass) (state) (owner ∈
leastDeficientOwners) (hactive) (htight : loss ≤ 1) (hpressure : 0 < ownerP1Pressure) :
CheckedCoherentAugmentation ⊕ CheckedCollisionDefectTrade` — local input already proved by the star theorem;
open content GLOBAL: all strong star keys matched/blocked WHILE all covered star pairs stay equal-defect
detours inside one positive-defect sink SCC. A real rotor must hide inside a FULLY COVERED CUT-TIGHT
BLUE-NEIGHBOUR STAR.

## 9. Hypothesis consumption + estimate
Tri-freeness: star independence, exact star identity, distance-2 positions, detour validity. Maxcut: σ≥0,
star bound, loss additivity, production threshold. Anchoring/completeness: t anchored rows, detour rows in
DB. Minimality: only for latent producers / witness overlap. Γ-minimality: upstream (all-ℓ=5).
**P(genuine canonical falsifier) ≈ 10%** (was 15%); 90% on: fully covered cut-tight stars necessarily expose
a globally unused strong key or a lower-defect detour under the complete row DB + coherent matching.
