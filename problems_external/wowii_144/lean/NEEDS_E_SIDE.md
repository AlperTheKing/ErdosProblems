# NEEDS — Lean API gaps for the metric side of C144 (Lemma E) and C142

Context: `lemmaM.lean` (compiled 2026-07-18) closes the combinatorial consumer side:
from a base induced tree `P` (supplied at card `girth − 1`) plus a list of pairwise
non-adjacent tree components each sending exactly one edge into `P`, we get
`t(G) ≥ (g−1) + Σ|Fᵢ|`. Everything below is what the METRIC side (Lemma E:
`e ≥ 1 ⟹ ∃ shortest cycle K, e ≤ M(K)`; and C142's `f`-analogue) still needs.
Difficulty: easy ≈ ≤1 session; medium ≈ 1–3 sessions; hard ≈ multi-session/design risk.

## G1. Chordlessness of shortest cycles (T3, part 1) — MEDIUM

Statement: if `c : G.Walk v v` is a cycle with `c.length = G.girth`, and
`x, y ∈ c.support` with `G.Adj x y`, then `s(x,y) ∈ c.edges`.
Route: rotate `c` at `x` (`Walk.rotate`, `IsCycle.rotate`); `y` splits the rotated cycle
via `takeUntil`/`dropUntil`; both pieces are paths (cycle support-tail nodup +
`IsPath.takeUntil/dropUntil`); closing the SHORTER piece (length ≤ ⌊g/2⌋ < g − 1... use
`length take + length drop = g`) with the chord gives a cycle
(`Walk.cons_isCycle_iff` — need chord ∉ piece edges, from nodup) of length < g,
contradicting `girth_le_length`. Build on: `WalkDecomp` take/drop length lemmas
(`length_takeUntil_le`, take_spec), `Walk.cons_isCycle_iff` (same pattern as
`treepath.lean`). All pieces exist; the bookkeeping ("chord not an edge of the shorter
arc unless consecutive") is the work.

## G2. Isometry of shortest cycles (T3, part 2: arcs of length ≤ ⌊g/2⌋ are geodesics) — HARD

Statement: for a girth cycle `c` and `i ≤ j ≤ c.length`,
`G.dist (c.getVert i) (c.getVert j) = min (j−i) (g−(j−i))`.
This is the hardest primitive: the classical proof splices a hypothetical shorter
geodesic with the shorter arc and must extract a genuine CYCLE shorter than `g` from a
closed walk — Mathlib has no "closed walk of length < girth is degenerate" tool.
Feasible route: induction via `Connected.exists_path_of_dist` + the fact that a closed
walk shorter than the girth is contained in a tree-like part… in practice: prove the
KEY SPECIAL CASE first (`dist(c.getVert 0, c.getVert i) ≥ min i (g−i)`) by strong
induction on a shortest counterexample using G1; expect several sessions. Every INTEL
"window/tent" count sits on top of this. Mathlib pieces: `Walk.getVert`,
`adj_getVert_succ`, `dist_le`, `Connected.dist_triangle`, G1.
Fallback that avoids full isometry: only `dist ≥ 1` facts + component structure may
suffice for the `g = 3, 4` endgames, but the `g ≥ 5` window argument needs real `d_K`.

## G3. Cycle-position arithmetic `d_K`, arcs, antipodes — MEDIUM (given G2)

Define for a girth witness `c` (length `g`): position map `Fin g → α`, `i ↦ c.getVert i`
(injective on `[0, g)` — from `IsCycle.support_nodup` + `support_getElem_eq_getVert`);
`d_K i j := min |i−j| (g−|i−j|)`; antipode/window predicates as `Fin g`/ℕ arithmetic.
Needed lemmas: injectivity, `Adj (pos i) (pos (i+1 mod g))`, `d_K` triangle/symmetry
(pure `omega`), and the G2 bridge `G.dist (pos i) (pos j) = d_K i j`. Tedious but
mechanical once G2 exists. Build on: `Walk.getVert_mem_support`, `Walk.length_support`,
`List.Nodup` index lemmas.

## G4. z-selectable supplier: `P = K.support.toFinset.erase z` — MEDIUM

`lemmaM.lean` supplies SOME `P` of card `g−1`; Lemma M needs `P = K ∖ {z}` for a CHOSEN
`z` (edges from components into `z` are unrestricted). Route: rotate `c` at `z`, reuse
the compiled supplier proof, then identify the witness set: needs
`(tail.dropLast).support.toFinset = support.toFinset.erase z`, i.e. a
`Walk.support_dropLast`-style lemma that Mathlib LACKS (checked: no `support_take` /
`support_dropLast` characterization). Two options: (i) prove the list lemma
`l.Nodup → l ≠ [] → l.dropLast.toFinset = l.toFinset.erase (l.getLast h)` (~20 lines,
self-contained); (ii) avoid dropLast: subset + card argument
(`Finset.eq_of_subset_of_card_le`) needing only `z ∉ p.support`. Also needed: the
adjacency data "`pos i ∈ P` for `i ≠ z-position`, consecutive positions adjacent in
`G.induce P`" to place component bridges — comes free from G3's position map.

## G5. Branch components of `G − K` as a component list — MEDIUM-HARD

Lemma M's `M(K)` maximizes over induced forests `F ⊆ V∖K` whose components each send
exactly one edge into `K∖{z}`. To FEED `isTree_induce_union_foldr_of_unique_bridges`
we must decompose an induced forest into its component finsets:
* `(G.induce ↑F).IsAcyclic` + `ConnectedComponent` of the induced graph → list of
  component supports as `Finset α` (via `Fintype (ConnectedComponent _)`,
  `ConnectedComponent.supp`, `Set.toFinset`, `Finset.univ.toList`).
* Per component: induced-connected + acyclic ⟹ `IsTree` on the supp
  (`induce` of `induce` transitivity — needs the standard
  `G.induce s |>.induce t ≃ G.induce (t-image)` glue, mildly annoying with subtypes).
* Distinct components are non-adjacent inside `F` (definition of components) — but the
  fold hypothesis needs non-adjacency IN `G` between component finsets, which is TRUE
  (an F-internal G-edge between components would merge them) yet requires the
  supp-level restatement.
* Pairwise disjointness: `ConnectedComponent.supp` pairwise disjoint — exists in spirit
  (`connectedComponentMk` fibers); restating for finsets is routine.
Alternative that skips components entirely: in the eventual 144 proof, construct the
witness families DIRECTLY as lists of explicit tree finsets (paths/tails), never as
"a forest"; then G5 shrinks to EASY. Recommend designing the paper proof's Lean plan
around explicit lists (the class-P proof's per-position witness trees already are).

## G6. Geodesic-to-set tails (distToSet witness paths) — EASY-MEDIUM

Needed: from `exists_dist_eq_distToSet` (compiled, wave1 api) get a geodesic
`v → s₀ ∈ S` realizing `distToSet v S`, whose INTERNAL vertices stay outside... the
precise fact used by Lemma E: along a geodesic from `v` to the set `C` (or `K`),
prefix vertices have `distToSet ≥ distToSet v − i` (1-Lipschitz along edges).
Pieces: `Connected.exists_path_of_dist`, `Walk.take`/`getVert`, `distToSet_le_dist`,
plus a new `distToSet_adj_ge_sub_one : G.Adj u w → distToSet u S ≤ distToSet w S + 1`
(easy from `dist` triangle through the witness member). All routine.

## G7. Center/radius facts: `e ≤ r` and `e ≥ 1 ⟹ D ≥ r + 1` — EASY

`e ≤ r` is DONE in substance: `ecc_le` + `distToSet_center_le_radius_toNat`
(wave1 api.lean, compiled) — just compose.
`e ≥ 1 ⟹ D ≥ r+1`: route: `e ≥ 1` ⟹ `G.center ≠ univ` (via `ecc_eq_zero_of_forall_mem`)
⟹ ∃ `w ∉ center`, i.e. `eccent w ≠ radius`; `radius ≤ eccent w` always
(`radius_le_eccent`), so `radius + 1 ≤ eccent w ≤ ediam` — then ℕ∞→ℕ transfer
(`ENat.toNat`, `radius_ne_top_iff`, `connected_iff_ediam_ne_top`). Main friction:
ℕ∞/ℕ casts, same flavor as `distToSet_center_le_radius_toNat` (pattern exists).
Also easy variant for C142: both ends of a diametral geodesic are peripheral
(`f ≤ max_v d(v, {b,w})` — needs `eccent`-monotonicity along realized distances; the
INTEL fact `d(b,w) = D = ecc b ⟹ ecc w = D` is one `le_antisymm` over `edist`).

## G8. `M(K)`-style maximization as a def (optional) — EASY

Lemma E's statement `e ≤ M(K)` needs `M(K)` as a ℕ-valued max over component lists.
Recommend NOT defining a `noncomputable def M`; instead state Lemma E in Lean as
"∃ K (girth cycle), ∃ z, ∃ list L (admissible for `K.erase z`), `ecc G G.center ≤ Σ|Fᵢ|`"
— this composes directly with `girth_sub_one_add_sum_le_largestInducedTreeSize` /
`card_add_sum_le_largestInducedTreeSize_of_unique_bridges` and skips a sup-def + its
attainment lemmas entirely.

## G9. Window/tent counting layer (class-P proof S1–S8) — MEDIUM

Once G2/G3 exist, the capacity count (`Σ Dⱼ ≥ δ₀` over any cover of `2δ₀−1` noncentral
window positions; per-position witness trees with `d_K(σ, ρⱼ) ≥ r+1−Dⱼ`) is finite
combinatorics over `Fin g` + ℕ: `Finset.sum` bounds, pigeonhole
(`Finset.exists_le_of_sum_le`), interval finsets. No graph theory beyond G2/G3/G6;
plan it as a standalone arithmetic file.

---

## Top-3 hardest (ranked)

1. **G2 — shortest-cycle isometry** (splice/extraction argument with zero Mathlib
   support; blocks all `d_K`-based window arguments).
2. **G5 — forest→component-list decomposition** (ConnectedComponent/supp/subtype
   plumbing; avoidable by designing the proof around explicit witness lists — strongly
   recommended).
3. **G3 (+G4) — cycle-position bookkeeping** (`Fin g` arithmetic bridged to walks;
   mechanical but voluminous, and the `erase z` supplier needs a missing
   `support_dropLast`-style lemma).
