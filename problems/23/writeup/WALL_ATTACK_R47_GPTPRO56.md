# WALL ATTACK — R47: THE EXACT MAXCUT/ROW-PRESERVATION BRIDGE (CheapGeometry ⟺ extension); NO ALL-t
# COEFFICIENT CONTRADICTION (filter, not closer); TWO-LAYER ENDGAME FROZEN; P ~5%
# (GPT-5.6 Pro, 2026-07-12, "worked 7m56s"; harvested ~11.6k ch)

**[CLAUDE GATE HEADER + ENGINE OVERLAY — the same hour: (a) the maxcut obstruction REPEATS on three
independent support hits (10+8 / 9+9 / 12+6; decisive switches 21/22/23; all 8 splits UNSAT each,
CaDiCaL-replayed); 13+5 rooted-infeasible; (b) ⚠ SCOPE CORRECTION (my profile question caught it): NONE of
the three hits is fully covered — the exact selected-row layer admits NO individual owner profile in any ⟹
GPT's no_t5_triangleFree_twoOwnerCoveredCircuit is NOT falsified; the hits die at PROFILE REALIZABILITY
first, maxcut second; (c) the INTEGRATED profile+circuit CP-SAT (one row/atom, r(owner)=5, one active edge,
endpoint selected, all pairs covered) finds the three hits INFEASIBLE and 400 bounded rooted supports give
ZERO integrated hits; (d) SHARED-BAD-NEIGHBOUR ROOTING MUST BE DROPPED at t=5 (my ruling, answering their
audit): the t=4 K_{2,3}-core forcing came from the s+a+b+d ≥ 5 budget, which is VACUOUS at t=5 (4t+5−t²=0) —
the exhaustive sweep must widen. The two-layer endgame below is adopted; layer-boundary now has THREE gates:
profile realizability → cheap geometry → production matching.]**

## 1-3. The exact bridge
κ(S) = |M∩δ(S)| − |B₀∩δ(S)|; displayed cut maximum ⟺ ∀S: κ(S) ≤ |X∩δ(S)| (complete — every cut is a switch).
Row preservation ⟺ X independent in the finite monotone hypergraph H_safe = {H_P = E(P)∩C : P a forbidden
path (length < 4, or new length-4 ∉ R_a)} ∪ {H_T : triangles} — multi-edge interactions handled (individual
safety insufficient). Cap_rp(S) = max |X∩δ(S)| over H_safe-independent X; NECESSARY: max(0,κ(S)) ≤ Cap_rp(S)
∀S. One-switch exclusion: noExtension_of_switchDeficit_gt_rowSafeCapacity. Dead candidate #1: κ = 21; a
single-switch cert needs Cap_rp(S) ≤ 20 (the SAT proof certifies the stronger global UNSAT).

## 4-5. CheapGeometry (frozen interface) + pruning
**CheapGeometry(D) ⟺ ∃X ⊆ C: H_safe-independent ∧ B₀∪X connected ∧ ∀S κ(S) ≤ |X∩δ(S)| ⟺
HasTriangleFreeRowPreservingMaximumCutExtension** (compile shells: RowPreservingExtensionData, switchDeficit,
RowSafe, CheapGeometry, cheapGeometry_iff_rowPreservingMaximumCutExtension). First-stage pruning: singleSafe(e)
(per-atom distance test d(s,p)+1+d(q,t) > 4 both orientations); Cap_rp(S) ≤ #{singleSafe candidates across S}.

## 6-7. Universal forcing is weak; scale verdict
Defect-one forces only E_S[κ_support(S)] = 1/2 ⟹ ∃S κ ≥ 1 (scale-free but tiny); the 21 was particular. NO
Θ(t²) heavy switch from support cardinalities. Scale: raw ambient capacity ~ 21t²/4 vs demand ≤ t² — both
Θ(t²), capacity coefficient larger ⟹ NO asymptotic contradiction. Concentrated bads/small boundary ⟹ big κ;
dense distance layers ⟹ small Cap; spread supports may be cheap. The all-t support-level target
twoOwnerCoveredCircuit_has_overfullRowSafeCut is TRUE on all three dead candidates, NOT proved generally.

## 8-9. Pipeline + THE TWO-LAYER ENDGAME
Rooted search order: circuit → shore splits → candidates → singleSafe → H_safe → Cap_rp on high-deficit
switches → global (10) lazily → ONLY cheap geometries reach production. Statistics: κ_max, c₁(S), Cap_rp,
global slack. Cheap shape prediction: bad-heavy cuts spread over many singleSafe pairs (low signed cut
discrepancy / remote distance layers). **FINAL PROOF SHAPE (GPT's ruling): LAYER 1 geometric exclusion
(non-cheap circuits never become cages — the bridge above) + LAYER 2 production matching
(canonicalCollisionFeasibleTuple_exists on cheap survivors). A genuine falsifier must pass BOTH.** With the
engine correction, layer boundary = profile realizability → cheap geometry → production matching.

## P
GPT ≈ 5% (three dead candidates = the row-preservation layer does real work; other supports may be cheaper).
Engine layer count as of this tick: integrated profile+circuit hits at t=5 = ZERO (three support hits + 400
bounded rooted supports all infeasible at the profile layer).
