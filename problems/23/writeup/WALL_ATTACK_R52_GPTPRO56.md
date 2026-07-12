# WALL ATTACK — R52: CDC PATTERN TRANSFER — THE COHERENCE-FREE PIVOT. Candidate I (soft collision
# two-cover / fractional flow, NO BaseKeyComponentCoherent) SURVIVES THE ENTIRE CORPUS and, if its
# selection theorem holds, PROVES ERDOS #23 EVEN IF THE COHERENT ROTOR WALL IS FALSE. Candidates II/III/IV
# killed with exact reasons. New theorem-of-record candidate: canonicalSoftCollisionFeasibleTuple_exists.
# (GPT-5.6 Pro, 2026-07-12, "worked 17m27s"; harvested ~15.6k ch; cites the published CDC note)

**[CLAUDE GATE HEADER — the candidate-I logic is verified by inspection: (i) dropping coherence is SOUND for
counting (each FreeHalf spent ≤ once ⟹ the signed Free-minus-Collision identity still yields N² − 25|M| ≥ 0
via the compiled inactive-collapse accounting); coherence was needed only by the BANK-PACKAGE construction
path; (ii) the soft 2-cover (z ∈ {0,1,2}, obligation-degree 2, source-degree ∈ {0,2}) decomposes into even
cycles ⟹ alternating selection = injective matching — the exact CDC 0/2 analogue; (iii) the fractional form
is a bipartite-flow polytope ⟹ INTEGRAL ⟹ flow ⟺ matching; (iv) corpus monotonicity: soft-MaxFlow ≥
coherent-MaxFlow, so every coherent-defect-0 witness (ALL fixtures + the full N≤12 census) transfers
instantly; 2943 passes via the anchor tuple; join-5886's two-root conflict DISAPPEARS BY DESIGN. NEW EXACT
OBJECTIVE for the engine: Δ_soft(ω) = |O_ω| − MaxFlow(O,S,E) with NO base-component variables; a graph with
min_ω Δ_soft > 0 kills the pivot (falsifier target); zero everywhere ⟹ THEOREM OF RECORD CHANGES to the
soft selection theorem — strictly weaker and plausibly far more tractable than the coherent one.]**

## Candidate I — coherence-free soft collision flow (SURVIVES)
Relaxation: drop BaseKeyComponentCoherent; keep the six-relation eligibility E_ω ⊆ O_ω × S_ω. Soft object:
z_{o,s} ∈ {0,1,2}, Σ_s z = 2 per obligation, Σ_o z ∈ {0,2} per source ⟹ even-cycle graph ⟹ matching
(SoftCollisionTwoCover.toMatching). Fractional: x = z/2, standard bipartite polytope, integral
(fractionalCollisionFlow_integral). THEOREM CHAIN: **Soft Lemma 1** softCollisionFlow_to_erdos23 (inactive
collapse + flow ⟹ 25|M| ≤ N²; elementary counting); **Soft Lemma 2** softCollisionFlow_iff_noDual (Hall
prices p(o) ≤ q(s) on eligible pairs; Σp ≤ Σq; elementary LP duality); **GRAPH LEMMA (the new wall)**
canonicalSoftCollisionFeasibleTuple_exists. Bypasses: bank tokens, component ownership, micro HitNeed
tokenization, THE COHERENT-BASE ROTOR WALL. Corpus: 8-vtx (vacuous), 89 (collapsed), 167/311 (explicit
matchings), N12 fixture (28-key assignment), N78 (P1 margins), 2943 (anchor tuple + P5 repair), join-5886
(conflict gone by design), census (monotonicity). #298/#264/18-vtx are non-cages (excluded upstream).

## The missing CDC handshake (R53 target)
softDualGap_switchDetour_decomposition: gap(d) = −weightedDetourEnergy − weightedSwitchEnergy (both ≥ 0)
would annihilate every dual exactly as CDC's endpoint handshake kills η(d). NOT known. Neutral rotors show
detour energy can telescope; the identity must extract a positive switch-surplus/source-exposure term from
every positive-gap orbit. NOTE (mine): the old rotor bookkeeping used COHERENCE-BLOCKING as a saturation
mode — in the soft setting that mode is GONE, Exposure can only be paid by matched halves ⟹ the R38-R42
rotor analysis must be REDONE and is plausibly much harder for the adversary.

## Candidates II-IV (dead, exact reasons)
II fractional row-pair packing (Σλ = 1 per atom; pair loads ≤ 1 ⟹ 25|M| ≤ N² directly): **killed by the
89-vtx double-star** — dual w_{r,r} = 1 gives Σ_f min_R w(R) = 20 > 1 (rows forced through the hub pair;
harmless congestion after collapse, fatal for naked packing). III finite-group pair-parity: unsound —
parity cannot enforce UNIT CAPACITY (20 occurrences at (r,r) pair among themselves under any fixed module);
exact-degree repair collapses back to Candidate I. IV minimal-circuit cofactor circulation (left kernel of
the generic atom-support incidence matrix; genuine nowhere-zero algebraic flow): no nonnegative counting
lemma; incidence cycle space supports unkillable duals; sign problem (rational-function field); does not
distinguish production-realizable from dead supports.

## Honest assessment + directive
The CDC pattern transfers ARCHITECTURALLY (rigid injection → soft transport → linear dual → global double
count), NOT as a finite-group parity trick (CDC = even cover in char 2; #23 = unit-capacity injection under
unbounded multiplicities — magnitudes essential). IMMEDIATE: gate Δ_soft on corpus + N≤12 (expected 0
everywhere by monotonicity — verify); adversarial hunt min Δ_soft > 0; if clean, pivot the theorem of
record and REDO the rotor/falsifier program in the soft setting (R53).
