# WALL ATTACK — R10: innermost tight-corner lemma (the concrete-lens selection proof mechanism)
# (GPT-5.6 Pro, 2026-07-10, RELAYED VERBATIM BY USER)

**[CLAUDE GATE HEADER:**
- **FOUR-CORNER IDENTITY (4) VERIFIED by my exact gate** (all 16 endpoint membership cases):
  1[e∈δX] + 1[e∈δY] − 1[e∈δ(X∩Y)] − 1[e∈δ(X∪Y)] = 2·1[e∈E(Q,R)], Q=X\Y, R=Y\X. Consequences (5)-(6):
  X,Y D1-tight + I,J D1-feasible ⟹ α-mass(E(Q,R)) − β-mass − γ-mass = (σ(I)+σ(J))/2 ≥ 0; with a
  positive-γ crossing port ⟹ **a dual-positive anchor atom a× crosses the corner** (7)-(8). THE DUAL
  SELECTS THE LENS ANCHOR, NOT A FIBER — dodges the R9 parity trap entirely (no exact-one requirement).
- **Selection**: γ-reduction preprocessing (lower inessential γ exactly; preserves D1/D2/StrictGap since γ
  absent from the objective; micro-lemma essentialGamma_has_tight_root_row) → innermost tight crossing pair
  (X,Y) by lex order (|Q|+|R|, |δF(Q)|+|δF(R)|, ΓRank, code) → **U := X\Y** feeds the EXISTING
  checkConcretePureLensCageSplit (no synthetic closure, no regenerated bank).
- **THE new geometric lemma (the wall): `innermostTightRootCorner_pure`** — proof mechanism given:
  * noDouble: a selected 5-vertex geodesic meeting Q in ≥2 intervals gives a corridor splice; corner words
    ∈ {00,10,11,01}^5 = finite case split; every non-convex 10-occurrence yields (i) a SHORTER blue
    replacement (contradicts ℓ=5 shortestness) or (ii) an equal-length replacement with strictly smaller
    Γ-signature (fewer corridor alternations, then fewer off-support edges, then smaller code —
    contradicts Γ-minimality). Triangle-freeness used exactly at the listed degeneracies (1+2-edge pair =
    triangle; distinct first/last contacts; spliced walk simple).
  * cover-or-zero: same splice on the first-entry/last-exit segment ⟹ every nonzero-surplus atom wholly
    owned by one child; cut atoms are zero-surplus ℓ=5 (allowed).
  * properness: closure of Q = whole parent ⟹ first real exit port on the trace is non-Door-only (compiled
    edge-door discharge) ⟹ with a× forms a STRICTLY SMALLER crossing pair — contradicts innermostness.
  * vertex-disjointness: earliest meeting of the two closure traces ⟹ smaller crossing or smaller Γ-rank —
    contradicts the lex choice.
- **Bank + balance arms ALREADY COMPILED**: vertex disjointness ⟹ single ownership (termInCage exclusive)
  ⟹ Bank(W)+Bank(C') ≤ Bank(C) (term_contrib_le summed); Surplus additive (pure-lens exchange) ⟹
  Balance(W)+Balance(C') ≤ Balance(C) < 0 ⟹ some proper child negative ⟹ contradicts MinNeg. This CLOSES
  no_rootCrossing_in_minNeg GIVEN the pure lemma.
- **Direct exact gate** (10 steps, adopted): γ-reduce → enumerate tight rows → crossing pairs → four-corner
  recompute in Fraction → positive-γ port in E(Q,R) → α-positive corner atoms → lex order → run the real
  checker on U=Q → verify ownership + (10). Decisive falsifier format: real graph/cut/atom-path/edge-port/
  LocalBankTerm tables + full checked strict dual + all slacks + crossing witness + ALL innermost pairs +
  checker failure for EVERY U=X\Y + per-child MinNeg. No synthetic ports or pooled sinks.
- STATUS: wall of record = **innermostTightRootCorner_pure** (finite 4^5-corner-word case analysis with
  shortestness + Γ-minimality + tri-free levers) + γ-reduction micro-lemma + four-corner bookkeeping
  (VERIFIED) + finite-Farkas iff + MandatoryDoorRoute checker fact. MY NEXT: demand the FULL corner-word
  case table (the actual finite proof, not the mechanism sketch) + hand Codex the four-corner identity /
  γ-reduction / selection-order formalization lanes; implement the 10-step gate on abstract candidates per
  the R8 recipe.**]
