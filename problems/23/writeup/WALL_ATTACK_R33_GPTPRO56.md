# WALL ATTACK — R33: ADVERSARIAL FREEZE FAILS AT MAXCUT; WALL FINAL FORM = lockExposureOrTrade + lockTrace_step
# (GPT-5.6 Pro, 2026-07-11; harvested 12,986 ch)

**[CLAUDE GATE HEADER — the adversarial-failure computation is elementary+verified by inspection (single-leaf flip
gains t−1 > 0 in the rigid-selector gadget ⟹ not a maximum cut); the formal architecture is recorded below; the two
named open statements are the wall. Codex Δ-evaluator + falsifier-gate lanes assigned; 2943 all-local→all-anchor =
the first concrete CheckedCollisionDefectTrade (28→0), both endpoints already my-gated.]**

## Substance
1. **Branch (A) genuinely attempted, FAILED at maxcut**: freezing the 2943-style traffic block (pair lock arms,
   rigid selector row x_L−y_L−a−y_R−x_R) gives a gadget whose displayed-colour max contribution is 6 vs 7 separated
   ⟹ flipping one left leaf vs t right leaves gains Δcut ≥ t−1 > 0. Repairs recreate the dichotomy: leave lock
   vertices outside scope ⟹ P4/P5 exposes Free mass; select them via new ℓ=5 rows ⟹ new shortest-row alternatives
   create simultaneous trades. NO all-tuple collision-starved canonical cage found; no impossibility proof either.
2. **Collision problem separated exactly**: Δ(ω) = |collision obligations| − ν(ω), ν = max coherent matching under
   (1) obligation ≤1, (2) source ≤1 (unreserved FreeHalves, half-0 active reservations cap 0), (3)-(4) BASE-KEY
   COMPONENT COHERENCE via labels y_{k,c} (≤1 component per base key), (5) R_ω = deduplicated union of
   P1/P2/P3/P4/P5/common-blue. Hits excluded — each HitNeed (v,e) paid by Door(e) cap 25.
3. **Honest selection**: ω* = argmin(Δ(ω), rowCode(ω)). 2943: all-local Δ=28, all-anchor Δ=0. N12 fixture: Δ=0.
4. **Target**: `canonicalCollisionFeasibleTuple_exists : canonical ⟹ ∃ω, collisionDefect ω = 0`; Doors finish micro.
5. **CheckedCollisionDefectTrade**: arbitrary simultaneous row change + coherent partial matching certificate with
   |unmatched| < oldDefect; soundness Δ(ω') ≤ |unmatched| < Δ(ω) immediate (defect_lt, no maximality proof needed).
   2943's 676-row all-local→all-anchor reassignment = concrete 28→0 certificate.
6. **DERIVATION (compiled-shape given)**: at ω* with optimal coherent M*, if Δ>0 then lockExposureOrTrade gives
   (augment ⟹ contradicts M* optimality) ∨ (trade ⟹ contradicts ω* argmin) ⟹ Δ(ω*)=0. Well-founded by construction —
   no cycling possible (the argmin absorbs it).
7. **THE WALL (named, first unprovable)**: `deficientCollisionCut_lockExposureOrTrade` — at any optimal coherent
   matching with positive defect and least min-cut shore Z: a coherent augmentation exists OR a checked
   defect-decreasing trade exists. FIRST OBLIGATION INSIDE: `lockTrace_step` — the finite trace machine (state =
   atom, chosen row, row position, active component, base-key label) from each unmatched repeated-row occurrence
   either reaches a checked source terminal (outside-U component / quiescent zero-demand component / common-blue
   pair / existing P1-P5 terminal ⟹ augmentation) or repeats (⟹ alternating row-trade cycle ⟹ trade). Termination
   by finite states; traces need NOT decrease Γ and need NOT be bounded.
8. **Hypothesis consumption map**: triangle-free ⟹ row-intersection rule + induced ℓ=5 replacements; blue-conn ⟹
   traces cannot end unattached (outside/quiescent regions have blue boundary); MAXCUT ⟹ validates every static
   terminal (σ(S)≥0) AND the lock inequalities whose EQUALITY cases force sharing (no private disappearance);
   nodup complete rows ⟹ finite state graph + repeats are genuine trades; minimal-defect-one ⟹ deletion-producer
   maps at non-producer support edges; Γ-min = upstream regime placement only (NOT a trace potential).
9. **Decisive falsifier gate spec**: per tuple compute exact coherent matching + Δ; find argmin; if Δ(ω*)>0 emit
   (matching, min-cut shore, defect, no-smaller-tuple proof) = decisive CE to the target; for the ENGINE also emit
   the full lock-trace state graph + all cycles + best post-trade matchings + proof none augments/lowers — "the
   exact all-tuple adversarial object still not found".
10. Precise unresolved structural statement: "whether every way of repairing that lock necessarily yields either an
    exposed FreeHalf source or an arbitrary-size coherent row trade."
