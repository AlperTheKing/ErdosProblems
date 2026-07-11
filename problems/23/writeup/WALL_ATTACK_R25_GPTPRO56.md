# WALL ATTACK — R25: Ell5ScopedOneRowDescent reduced to ONE geometric lemma
# scopedHallFailure_has_internalKillerRow; k=4 case PROVEN; open = producer alignment at k≥6
# (GPT-5.6 Pro, 2026-07-11)

**[CLAUDE GATE HEADER — reduction verified by inspection; no new numerics to gate:**
- SCOPED FRAME (definitions of record, matching Codex's census gate): U_ω, S_ω (selected support),
  I_ω (internal off-support blue edges), ActComp(ω) = components of I_ω containing both endpoints of a
  selected atom; Obl(ω) = collision excess + HitNeed RESTRICTED to V_act; obligationScore = |Obl(ω)|;
  no active components ⟹ score 0 (3); scoped-Hall failure ⟹ score > 0 (4).
- **THE ONE LEMMA (5) — ScopedHallFailure_has_internalKillerRow**: scoped Hall failure ⟹ ∃ atom f +
  alternative shortest row Q ≠ R_f with V(Q) ⊆ U_ω, |E(Q) ∩ I_ω| ≥ 3, and ActComp(ω[f→Q]) = ∅.
  Then descent is AUTOMATIC: new score 0 < old score (7) ⟹ Ell5ScopedOneRowDescent (full Lean wrapper
  given, proof = obtain + omega). Census split: 691/705 have |E(Q)∩I| = 4, 14/705 have 3.
- **PROVEN ALREADY (k=4 branch)**: for an active atom f=st, shortest I_ω-path P from s to t has even
  length (bipartite, same side) ≥ 4 (d_B = 4); if k = 4, P itself IS an alternative shortest row (simple,
  four blue edges, induced by tri-freeness: chord at dist 2 = triangle, dist 3 = shorter blue path) —
  airtight ✓. **OPEN = k ≥ 6: PRODUCER ALIGNMENT** — every internal vertex of P lies on selected rows
  (producers), and support-minimality (12: ∪_{g≠f} F_g = F for f ∈ A, defect-one family) gives every edge
  of every alternative row of f a producer atom ≠ f — but nothing yet forces FOUR COMPATIBLE CONSECUTIVE
  producer edges assembling into one legal row. "The numerical Hall deficit does not presently force that
  producer alignment. This is the first unproved step."
- **HYPOTHESIS ROLES (final form)**: tri-free → co-occurrence lemma (I-edges are genuine missing pairs;
  dist-2 chord = triangle, dist-3 = shortens bad pair to 2, dist-4 = bad endpoints blue-adjacent) +
  induced-row property; max-cut → validates the full source relation (a scoped deficiency is genuine,
  not a rejected-negative-switch artifact); Γ-min → upstream only (canonical all-ℓ5 row DB);
  support-minimality (IsMinimalDefectOne) → producer existence per edge (12).
- **EXACT FINITE CHECKER for (5)** + failure record spec; TWO distinct falsifier outcomes: (i) no internal
  killer row but SOME one-row replacement still descends ⟹ falsifies only (5)-as-stated (census form);
  (ii) NO one-row replacement descends ⟹ decisive CE to Ell5ScopedOneRowDescent itself.
- **LEAN SHAPES COMPLETE**: ScopedInternalKillerRow structure, checkScopedInternalKillerRow (no trusted
  Boolean payload), scopedHallFailure_has_internalKillerRow (the wall statement with htri/hBconn/hmax/
  hGamma/hminimal), Ell5ScopedOneRowDescent wrapper (compiles immediately given the lemma).
- **FRONTIER (verbatim)**: "minimal scoped Hall deficiency ⟹ one internal three-or-four-active-edge row
  that destroys active scope. The shortest-I-path argument proves everything up to the producer-alignment
  step; that alignment is the first finite graph lemma still unproved."

## NEXT
- R26 (sent): attack producer alignment at k ≥ 6 — prove a deficient scoped shore forces an I-dense
  five-vertex window (four consecutive S∪I edges with ≥3 in I forming a DB row), or construct the
  k≥6-only failure cage (checker outcome i/ii distinguished).
- Codex lanes: compile the R25 stack (structure/checker/wrapper — mechanical); census N=12 scoped failures
  classified by the (5)-checker outcomes; verify the k=4 branch against the 705 anatomy (expect 691 = k4).**]
