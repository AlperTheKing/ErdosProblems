# WALL ATTACK — R38: BOTH CLOSING MECHANISMS FAIL; MINIMAL SURVIVOR = SATURATED NEUTRAL SQUARE ROTOR;
# THE ONE REMAINING GRAPH LEMMA = noPositiveDefectSaturatedNeutralSquareRotor (Exposure > 0)
# (GPT-5.6 Pro, 2026-07-12, "worked 8m5s"; harvested ~13k ch)

**[CLAUDE GATE HEADER — the two negative verdicts are verified by inspection: (1) the closure-growth identity
(|Z_O|+2q)−(|Z_S|+2q)=1 is arithmetic — saturated unit-defect cores survive enlargement, no parity contradiction
(2q source halves vs 2q+1 obligations is consistent); (2) the detour-cell identity n_ω′(a,b)−n_ω(a,b) =
1[a,b∈C∪{v}] − 1[a,b∈C∪{m}] gives n_ω′(x,y)=n_ω(x,y) for the probe pair (both in C) — the detour does NOT free
the pair that generated it, and new Free cells appear ONLY at (m,z) with n_ω(m,z)=1 or (m,m) with r_ω(m)=1 —
all avoidable when every n(m,z)≥2 and r(m)≥2. The "key didn't exist before ⟹ unmatched" argument is false
because a neutral class is a class of states (ω, M_ω, cursor), each tuple carrying its OWN optimal matching.
Codex N2 falsifier gate MUST be retargeted to the exact Exposure statistic (eqs 9–12). Double-star fixtures
first: GPT itself notes the counting failure mode C_v = 5r(v) − |Comp(v)| with fixed X_v,Y_v "IS the double-star
traffic phenomenon" — the rotor, if real, lives THERE.]**

## Verdict
Neither counting pressure nor detour-created-key augmentation proves realSinkNeutralAttachmentClass_hasAugment.
The minimal surviving object is a **saturated neutral square rotor**; excluding it on real canonical cages is
the exact remaining graph lemma. GPT has neither a proof that real cages cannot realize it nor a realization.

## 1. Counting pressure fails
- Probe key supply ≤ |X_v||Y_v| (X_v = active internal nbrs, Y_v = selected-row support nbrs); collision units
  C_v = 5r_ω(v) − |Comp_ω(v)| grow arbitrarily with r_ω(v) while X_v, Y_v stay fixed (selected rows reusing the
  same two support neighbours = double-star traffic). No 2C_v ≤ 2|X_v||Y_v| available.
- Alternating-closure growth: q new base keys with both halves matched ⟹ |Z_S|↦|Z_S|+2q, |Z_O|↦|Z_O|+2q —
  unit defect survives. Saturated closure (2q halves, 2q+1 obligations) is consistent. Component conflicts only
  weaken counting (base assigned elsewhere ⟹ unused half unusable by current owner).

## 2. Equal-defect detour fails to force a new source
Producer row Q = C ∪ {m} (|C|=4), detour row Q′ = C ∪ {v}:
n_ω′(a,b) − n_ω(a,b) = 1[a,b ∈ C∪{v}] − 1[a,b ∈ C∪{m}].
- Pairs inside C×C unchanged ⟹ the probe pair (x,y) stays covered: n_ω′(x,y) = n_ω(x,y).
- New Free cells only at (m,z), z∈C with n_ω(m,z)=1, or (m,m) with r_ω(m)=1. If n_ω(m,z)≥2 ∀z and r_ω(m)≥2:
  NO new Free cell at all.
- Even a new FreeHalf may fail the six eligibility predicates, be reservation-blocked, and belongs to ω′ whose
  own optimal matching M_ω′ may already match it. Per-tuple matchings kill the "new key ⟹ unmatched" argument.

## 3. Minimal surviving abstract shape — the rotor
Two states S_i (i ∈ Z/2): O_i = {o_i0, o_i1, o_i*}, S_i = {s_i0, s_i1}, M_i saturates both sources, Δ(S_i)=1
(o_i* unmatched). Every common-blue probe at o_i* returns the already-saturated base key under s_i0/s_i1; every
covered probe gives the equal-defect detour τ_i : S_i → S_{i+1}; τ_0, τ_1 inverse. Geometrically τ_i swaps the
middle of a blue square x − m_i − y − m_{i+1} − x. Background rows enforce n(m_i, z) ≥ 2 and r(m_i) ≥ 2 (so no
disappearing pair frees) and cover the opposite-middle pair (m_i, m_{i+1}). Valid abstract model of EVERYTHING
the local theorem proves. UNKNOWN: simultaneous realizability of the background rows as endpoint-anchored
induced 4-edge geodesics in a triangle-free maximum-cut cage with canonical support-minimality data.

## 4. Real form: saturated system of blue squares
Every neutral detour contains a blue 4-cycle x−m−y−v−x (x,y one side; m,v other side; old row uses x−m−y, new
uses x−v−y). Triangle-freeness permits the square, forbids its diagonals. Survival needs BOTH:
(a) disappearing-pair saturation: per transition m⇝v, n_ω(m,z) ≥ 2 for all retained z and r_ω(m) ≥ 2, OR every
created FreeHalf immediately matched/coherence-blocked in the TARGET state;
(b) probe-source saturation: every generated Free common-blue base key has all compatible usable halves matched,
or its global base label assigned to another component whose matched obligation stays inside the SCC.
Strong global requirements — but NO currently compiled graph lemma rules them out.

## 5. Exact falsifier statistic (gate spec)
NewFree(τ) = {(ω′,m,z,b) : z∈C_τ, n_ω(m,z)=1} ∪ {(ω′,z,m,b) : n_ω(z,m)=1} ∪ {(ω′,m,m,b) : r_ω(m)=1}, b ∈ Fin 2;
raw |NewFree| = 4·#{z : n_ω(m,z)=1} + 2·1[r_ω(m)=1]. Filter by unreservedness + six source relations +
obligation-compatibility in the target sink SCC ⟹ Escape(τ). Then
**Exposure(C) = Σ_{S∈C} #{probe-generated compatible sources unused in M_S} + Σ_{τ∈E(C)} #{Escape(τ) unused in
M_target(τ)}.** Augment exists iff Exposure > 0. **Decisive falsifier = real canonical cage with Δ(C) > 0 and
Exposure(C) = 0** — refutes the final lemma AND canonicalCollisionFeasibleTuple_exists.

## 6. The one remaining graph lemma (frozen shells)
`noPositiveDefectSaturatedNeutralSquareRotor (D) (htri hblueConnected hmax hrowsComplete hrowsAnchored
hrowsNodup hminimal) (C : CheckedSinkNeutralAttachmentClass D) (hpositive : 0 < C.defect) :
0 < D.neutralExposure C` — its consumer `realSinkNeutralAttachmentClass_hasAugment (… hexposure) :
Nonempty (CheckedCoherentAugmentation D C)` extracts the unused source and augments along the sink trace.

## 7. Conditional main theorem (full skeleton, compilable)
`canonicalCollisionFeasibleTuple_exists (D) (hcanonical) (hrotor : ∀ C, 0 < C.defect → 0 < D.neutralExposure C) :
∃ ω, D.collisionDefect ω = 0` — argmin defect; optimal matching; local step gives augment / lower detour
(contra minimality) / equal-defect edge / neutral matching transition; sink SCC; hrotor ⟹ Exposure > 0 ⟹
augmentation ⟹ contra optimality ⟹ δ = 0. Doors/vertexSlack/prune then discharge HitNeed microcopies.

## Honest status + the final question
Current hypotheses prove the local square/detour structure but NOT the exposure inequality. The last question:
**"Can a real maximum-cut cage realize a positive-defect, fully saturated neutral system of blue detour
squares?"** Falsifier search = exactly (Δ>0, sink SCC, all probe sources matched/blocked, all detour-created
eligible FreeHalves matched/blocked, neutralExposure = 0).
