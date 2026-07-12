# WALL ATTACK — R53: SOFT ROTOR SURVIVES VIA RESERVATION ONLY ⟹ ADAPTIVE-RESERVATION RELAXATION
# (edge-cap 2) KILLS IT; fixed-tuple handshake ⟺ the flow itself (no parity miracle); cross-tuple
# SOURCE-EXPOSURE is the true energy (2943 worked: +25 → −3 via 28 new halves); GPT P(soft theorem)≈98%,
# P(program closes via soft pivot)≈70%
# (GPT-5.6 Pro, 2026-07-12, "worked 8m52s"; harvested ~14.2k ch; script SHA f5b76a50)

**[CLAUDE GATE HEADER — verified by inspection: (i) the minimal soft rotor types exactly (2 states, one
2-half stem + ONE unreserved half-one key each; (B,U,L,A)=(2,1,0,1); coherence never used — the blocker is
the frozen half-zero ACTIVE-EDGE RESERVATION); (ii) the adaptive-reservation model (per-active-edge capacity
2 over its FOUR keys instead of pre-fixed halves) keeps the count sound — every active edge still removes
exactly 2 units ⟹ collisionUnits + |I_act| ≤ FreePairs ⟹ N² − 25|M| ≥ 0 — the polytope is a standard
integral network flow, AND the minimal rotor DIES (pay both v-obligations with (v,x,0),(v,x,1), reserve the
reverse orientation adaptively); (iii) the handshake converse (10) is coefficient comparison: any
nonnegative fixed-tuple decomposition IS a fractional flow ⟹ CDC's trick needed an INDEPENDENT global
coefficient supply (the Γ-flow) — ours must come from CROSS-TUPLE trades; (iv) the 2943 arithmetic is
consistent with my R29 gates (19950/19925/25 local; +28 quiescent halves ⟹ 19953 ⟹ gap −3 anchor; the
energy = SOURCE-EXPOSURE COUNT 28, NOT σ=26 nor 728 — switch magnitudes are legality witnesses, not
budgets). NEW WEAKEST TARGET: canonicalSoftEdgeCapFeasibleTuple_exists. IMMEDIATE GATE: adaptive-variant
defect over corpus + N≤12 (engine job; kills the only known abstract soft rotor if 0 everywhere).]**

## 1. Minimal coherence-free soft rotor (survives — via reservation only)
2 states ω_A/ω_B; O = {two halves of one stem}, S = {single unreserved half-one key of the active edge};
Δ_soft = 1 each; live detour ledger (2,1,0,1); reverse identical. 6/5 occurrence-rich version by adding
persistent stems/keys. NO coherence anywhere. Independent half-spending doesn't kill it because half zero
stays reserved ⟹ only one source per orientation.

## 2. THE ADAPTIVE-RESERVATION RELAXATION (new weakest sound target)
Replace fixed half-zero reservation with: Σ_{o,s over the 4 keys of active edge e} x_{o,s} ≤ 2 (keys keep
capacity 1; non-active keys direct to sink). Ordinary integral network flow. Counting sound: 2·FreePairs −
2|I_act| available ⟹ N² − 25|M| ≥ 0. Kills the minimal rotor. Lean: FractionalCollisionFlowWithEdgeCaps +
canonicalSoftEdgeCapFeasibleTuple_exists ("may be the better theorem of record").

## 3-5. Handshake verdict
Soft dual = pure Hall prices; identity (6): gap = −Σx(q−p) − Σ(1−c_s)q_s — EXISTS but converse (10): any
such decomposition's λ IS a flow (coefficient comparison) ⟹ fixed-tuple linear algebra cannot bypass Hall.
Switch/star magnitudes are NOT capacities (σ=26 switch licenses 28 halves; one key = capacity 1 regardless).
P(literal CDC fixed-tuple finish) ≈ 15%.

## 6-7. Cross-tuple = the mechanism; 2943 = the model
Detour energies that are potential differences telescope (the rotor: G=1 ↔ G=1). The 2943 fixture gives the
TRUE energy form: local tuple Hall gap +25 (demand 19950 vs 17325 P1 + 2600 P3 = 19925); the coordinated
676-row anchor trade exposes 14 ordered quiescent pairs = 28 NEW halves ⟹ gap −3. **Energy = newly exposed
source-half COUNT.** Remaining theorem: every globally-minimal positive soft defect admits an exposure trade
XOR is an impossible real soft rotor (noPositiveDefectSoftReservedEdgeRotor — strictly narrower than the
coherent version; and VOID under adaptive reservation if its gate passes).

## 8-9. Corpus + stack + P
Corpus: all pass (2943 baseline soft defect = 25 but anchor tuple 0 with slack 3; census transfers by
monotonicity; #298/#264/18-vtx are non-cages). Stack: 3 elementary lemmas (two-cover ⟺ flow ⟺ no-dual;
decomposition ⟺ flow) + erdos23_of_softCollisionFlow + the wall (fixed or edge-cap variant). **GPT P: soft
theorem true ≈98%; program closes via soft pivot in finitely many exposure/rotor rounds ≈70%.**
