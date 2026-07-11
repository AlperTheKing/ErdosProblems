# WALL ATTACK — R34: lockTrace ENGINE FALSE AT STATED INTERFACE (9-vtx abstract countermodel);
# corrected engine surface given; NEW geometric theorem must exclude closedCycle/deadEnd
# (GPT-5.6 Pro, 2026-07-11; harvested 12,777 ch)

**[CLAUDE GATE HEADER — countermodel VALID against the STATED axiom list; but MY ANCHORING OBSERVATION (recorded
here, fed to R35): the countermodel's 5 atoms share the IDENTICAL singleton row (v,a,b,c,d) — REAL-GRAPH-IMPOSSIBLE
(a row of atom (x,y) is a blue path FROM x TO y; five distinct bad edges cannot share one row — they would be five
parallel (v,d) edges). The stated axioms OMITTED RowEndpointAnchoring (row.head/last = atom endpoints; distinct
atoms ⟹ distinct endpoint pairs ⟹ distinct rows — graph-side theorem = my compiled PathRigidity). MY quick anchored
adaptation collapses: atoms (v,d_i), rows (v,a,b,c,d_i) give C_v = 3·4 = 12 ⟹ demand 24, while the d_i-diversity
creates row-companion sources (d_i,d_j): 20 ordered pairs ×2 halves = 40 ⟹ ~46 sources vs 24 demand ⟹ NO defect.
The sterile cycle NEEDS the un-anchored degeneracy. Engine repair (sec 8) ADOPTED regardless — the state-information
bug (occurrence/half/cursor omitted; two obligations sharing a state) is genuine.]**

## Substance
1. **Countermodel (abstract, 9 vertices)**: 5 atoms with identical singleton row (v,a,b,c,d) (support F shared,
   inclusion-minimal defect-one); active atom H=(u,...,w) + aux row; I_ω = path u−z1−v−z3−w; row-intersection rule
   holds; all switch losses 0. Ledger: n(v,·)=5 on {v,a,b,c,d} ⟹ C_v=20 ⟹ demand 40; sources = 6 unreserved
   same-first halves (half-0 of (v,z1),(v,z3) reserved); relation = K_{40,6}; Δ=34. Alternating core |Z_O|=7=|Z_S|+1;
   producer transitions form the sterile 5-cycle A0→…→A4→A0; post-cycle tuple identical, Δ unchanged. Two distinct
   half-obligations share the proposed state σ1 ⟹ the (atom,row,position,component,label) state LOSES essential info.
2. **Refuted**: "finite trace + repeated state ⟹ checked defect-lowering trade" from the STATED axioms; also
   "nonterminal ⟹ next-step" alone is insufficient (loops). Min-defect-one does NOT exclude sterile producer cycles.
3. **Subtle cases**: (a) shared locks need occurrence-level transitions; (b) baseOwner fixed ONCE in context —
   cross-component wants = dead branches (join-5886 handled); (c) unreserved ≠ augmenting (all 6 sources matched);
   (d) repeated state ⟹ closed alternating walk ⟹ only rotations/permutations — no strict trade without an unmatched
   terminal or an explicit checked trade certificate.
4. **CORRECTED ENGINE SURFACE (adopt)**: LockTraceContext (matching + root + global baseOwner + soundness),
   LockTraceCursor (obligation | source | rowOccurrence), CollisionObligation (owner, other, producerAtom,
   occurrence, copy, half, component), checkLockTraceStep = 5-way checked disjunction, soundness = invariant
   preservation ONLY, checkAugmentTerminal (matching-dependent), checkTradeTerminal (carries explicit certificate —
   repeated state alone is NOT a terminal), LockTraceSearchResult ∈ {augment, trade, closedCycle, deadEnd},
   lockTraceSearch_terminates by finite-state measure. **"A new real geometric theorem must rule out closedCycle
   and deadEnd; the current axioms cannot."**

## Same-tick Codex (marker → 2534301)
- 311 orientation bug fixed (3608/3608 pass, corrected gate 542E1B33).
- Subdivision starvation candidate (n=5647, arm edges → private length-3 paths; maxcut identity oldEdgeCut+2)
  SELF-CORRECTED as likely-dead: 2704 new unselected vertices create same-first FreeHalves for the hubs — a viable
  lock gadget must make new vertices co-occur with overloaded owners or avoid inflating the source space.
- **ASK (accepted into R35): COMMON-BLUE ABLATION** — with hits bank-funded, is collision-only P1+P3+strictP4+P5
  complete at canonical/argmin tuples (all fixtures + N≤12)? If yes, the reservation ledger drops from the proof
  (exclusivity = safety interface only). Census running.
- join-5886 independent re-gate PASSED (matching-level coherence sufficient: 19950/comp flow, 39,900 injective,
  zero defect); Pattern5StaticOwnership.lean compiled (93A86DBE).
- Lanes authorized: ledger/flow verification ×2, argmin census + ablation, falsifier-first attack on the target.

## NET after R34
Wall = closedCycle/deadEnd EXCLUSION under the CORRECTED engine + FULL axioms (incl RowEndpointAnchoring +
atom-endpoint-distinctness, which the countermodel exploits by omission). R35 SENT: does the sterile cycle survive
anchoring? (my adaptation says no) — anchored countermodel or exclusion proof; + common-blue ablation folded in.
