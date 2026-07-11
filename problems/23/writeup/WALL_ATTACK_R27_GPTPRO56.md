# WALL ATTACK — R27: unit-defect alternating core + producer closure;
# missing lemma = alternatingProducerIndicatorBound (|Z_O| ≤ |Z_S| + 1[B₃(Z)≠∅]);
# incidence countermodel ⟹ proof must use ORDERED SPLICES (GPT-5.6 Pro, 2026-07-11)

**[CLAUDE GATE HEADER — no graph numerics to gate; N=11 incidence model checked by inspection (gap
20−10 = 10 = 2(15−11)+2 ✓ shore identity consistent; explicitly NOT tri-free-realizable):**
- **UNIT-DEFECT NORMALIZATION**: lex-least maximum matching μ, least unmatched obligation o₀, alternating
  tree ⟹ exact bijection Z_S ↔ Z_O∖{o₀} ⟹ **|Z_O| = |Z_S| + 1** (1). No arbitrary shore gaps — one
  alternating component with defect exactly one.
- **PRODUCER CLOSURE G** (the operational latent→selected upgrade): seedRows(collision) = its extra row;
  seedRows(HitNeed at v) = all rows through v; close under the lex-least minimal-defect-one deletion
  matchings prod_g(e) = m_g⁻¹(e) (3)-(4); S_G = selected edges of G. B₃(Z) = {(f,e): f active, e ∈ S_G,
  ρ_ω(f,e) = 3} — each element CONSTRUCTS the killer row (accepted bridge lemma).
- **THE MISSING LEMMA (7)/(8) — alternatingProducerIndicatorBound**: |Z_O| ≤ |Z_S| + 1[B₃(Z) ≠ ∅].
  With (1) ⟹ B₃(Z) ≠ ∅ ⟹ (16) ⟹ killer row ⟹ descent. Constructive content: if the producer closure of
  ONE unmatched half-demand has no radius-3 selected edge, the alternating tree AUGMENTS (new FreeHalf
  source outside Z_S) — contradicting maximality of μ. Full Lean derivation of (16) given
  (leastUnmatchedAlternatingCore + by_contra + card_eq).
- **WHY PRESSURE+(17)+(18) CANNOT PROVE IT**: explicit N=11 abstract INCIDENCE countermodel (7-vertex
  active path, owner z₃, 3 rows {v,a,b,c,d} + 6 rows {z_i,a,b,c,d}; gap 10; disjoint adjacent producers;
  no i,i+2,i+4 row; no ρ=3 edge) — but NOT realizable as a tri-free graph ("ordering all those rows
  through the common symbols creates forbidden local graph configurations"). ⟹ the proof MUST use the
  ORDERED blue-path structure: adjacent active u,v with rows sharing companion x have subpath distances
  to x differing by EXACTLY one (uv blue, B bipartite) ⟹ equal-length SPLICING through uv available;
  (17)/(18) are only the first two forbidden splice configurations; iterate splices until a new
  four-pattern source appears (augment) or a ρ=3 selected edge is reached.
- **HYPOTHESIS BOOKKEEPING**: max-cut has done its ENTIRE job before (7) (all four patterns validated —
  a proof cannot discard sources on switch grounds); minimality = the closure (3)-(4); Γ-min upstream.
- **EXACT GATE (per failing tuple; TINY falsifier records)**: lex-least matching → least unmatched o₀ →
  alternating core → verify |Z_O| = |Z_S|+1 → deletion matchings → producer closure → enumerate ρ_ω(f,e)
  on S_G → b_Z = 1[B₃≠∅] → CHECK |Z_O| ≤ |Z_S| + b_Z. Outcome-(i) falsifier = one core + closure + no
  ρ=3 edge. No global shore enumeration.
- **SHARPNESS**: radius 3 is tight — minimal hfar geometry = 6-edge active path + selected chord z₁z₄
  (1+2 = 3; alternative row z₀z₁z₄z₅z₆); seven active vertices minimal.

## NEXT
- R28 (sent): prove the indicator bound via the ordered-splice iteration — enumerate the full splice case
  tree (start: shared companion x of adjacent active vertices; distances differ by one; tri-free +
  shortestness kill equal-length collisions), or exhibit the tri-free-realizable countermodel.
- Codex: implement the R27 alternating-core gate (replaces shore enumeration — cheaper + sharper falsifier
  records) on all census failures + fixtures; compile ScopedAlternatingCore + the closure defs.**]
