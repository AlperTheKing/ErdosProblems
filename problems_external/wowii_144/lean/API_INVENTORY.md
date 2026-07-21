# API INVENTORY — Lean assets for WOWII 142/144 (2026-07-18)

Scope: everything relevant to induced trees / girth / distances available in
`E:\fc_pr_build` (branch `wowii-141-143-proofs`, toolchain v4.27.0, oleans fresh as of
2026-07-18, `lake build FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree`
exit 0) plus the 141/142/143 wave scratch files. All names are in namespace `SimpleGraph`
unless noted. "REPO" = importable compiled library file; "SCRATCH" = standalone compiled
scratch file (copy lemmas into new files; they are not lake targets).

## 1. Induced trees — REPO `FormalConjecturesForMathlib/Combinatorics/SimpleGraph/LargestInducedTree.lean`

| Name | Statement (informal) |
|---|---|
| `largestInducedTreeSize` (def) | `sSup {n \| ∃ s : Finset α, s.card = n ∧ (G.induce ↑s).IsTree}` |
| `card_le_largestInducedTreeSize` | induced tree on `s` ⟹ `s.card ≤ largestInducedTreeSize G` |
| `one_le_largestInducedTreeSize` | `[Nonempty α]` ⟹ `1 ≤ t(G)` |
| `IsTree.induce_insert_of_unique_adj` | tree on `s` + outside `z` with UNIQUE neighbor `a ∈ s` ⟹ tree on `insert z s` (single-vertex attach) |
| `Walk.induce_support_isTree_of_length_eq_dist` | a shortest walk induces a tree on its support |
| `girth_sub_one_le_largestInducedTreeSize` | cyclic ⟹ `girth − 1 ≤ t(G)` (T2; shortest cycle minus one vertex) |
| `Connected.exists_induced_tree_containing_pair` | connected ⟹ any `x, y` lie in a common induced tree finset |
| `exists_maximum_induced_tree_containing` | family of induced trees ⊇ `r` nonempty ⟹ has a max-cardinality member |
| `Connected.exists_adj_finset_compl` | connected, `s` nonempty proper ⟹ ∃ `z ∉ s` adjacent to some `a ∈ s` |
| `exists_two_adj_of_maximum_induced_tree_containing` | boundary vertex of a MAX prescribed induced tree has TWO distinct neighbors in it (two-adjacency certificate) |
| `IsTree.girth_add_one_le_card_of_two_leaves_of_two_adj` | tree on `s` containing two degree-1 vertices of `G`, plus outside `z` with 2 neighbors ⟹ `girth + 1 ≤ s.card` |
| `girth_add_one_le_largestInducedTreeSize_of_two_leaves` | connected cyclic + two distinct leaves ⟹ `girth + 1 ≤ t(G)` (143 two-leaf lemma) |

## 2. Induced trees / girth — REPO `.../InducedTreeNeighborhood.lean` (141 campaign)

| Name | Statement (informal) |
|---|---|
| `IsTree.girth_le_length_add_two_of_two_adj` | path `p` in induced tree with two-adjacent outside `z` ⟹ `girth ≤ p.length + 2` (cycle closure certificate) |
| `isIndepSet_neighborSet_of_four_le_girth` | `girth ≥ 4` ⟹ every neighborhood is independent |
| `IsTree.card_support_inter_closedNeighborFinset_le_three` | tree path meets a closed neighborhood in ≤ 3 vertices (overlap lemma) |
| `exists_indepSet_finset_neighbors` | explicit independent neighbor finset witnessing `indepNeighborsCard` |
| `isTree_induce_insert_indepSet_neighbors` | center + independent neighbor set induces a star (tree) |
| `indepNeighborsCard_add_one_le_largestInducedTreeSize` | star bound |
| `indepNeighborsCard_le_degree` | local independence ≤ degree |
| `maxDegree_add_girth_le_largestInducedTreeSize_add_three` | connected cyclic, `girth ≥ 4` ⟹ `Δ + g ≤ t + 3` (141 main) |

NOTE: the path helpers inside this file (`path_start_unique_edge`,
`path_incident_edges_le_two`, `exists_subpath_between`, `tree_isPath_eq_cons_nil`,
`tree_center_mem_support`, `tree_edge_mem_of_center_mem`) are **private** — re-copy them
if needed (public copies exist in SCRATCH `wowii_141/wave1c/overlap.lean`).

## 3. NEW (this prestage) — SCRATCH `wowii_144/lean/lemmaM.lean` (compiled, exit 0, axioms clean)

| Name | Statement (informal) |
|---|---|
| `IsTree.induce_union_of_unique_bridge` | **attach primitive (a)**: disjoint finsets `S`, `T`, both induce trees, exactly one `G`-edge between them ⟹ `S ∪ T` induces a tree |
| `mem_foldr_union` | `x ∈ L.foldr (· ∪ ·) ∅ ↔ ∃ F ∈ L, x ∈ F` |
| `isTree_induce_union_foldr_of_unique_bridges` | **fold (b)**: base tree `P` + list of pairwise disjoint, pairwise non-adjacent trees each sending exactly one edge into `P` ⟹ union induces tree of card `\|P\| + Σ\|Fᵢ\|` |
| `card_add_sum_le_largestInducedTreeSize_of_unique_bridges` | **consumer**: same data ⟹ `\|P\| + Σ\|Fᵢ\| ≤ t(G)` |
| `exists_induced_tree_finset_card_girth_sub_one` | **supplier (c, ∃-form)**: cyclic ⟹ ∃ finset `P`, `P.card = girth − 1`, `P` induces a tree (shortest cycle minus a vertex, witness exposed) |
| `girth_sub_one_add_sum_le_largestInducedTreeSize` | **Lemma M composition**: cyclic ⟹ ∃ base `P` (card `g−1`, tree) s.t. every admissible component list gives `g − 1 + Σ\|Fᵢ\| ≤ t(G)` |

"Exactly one edge between S and T" model:
`∃ a ∈ S, ∃ b ∈ T, G.Adj a b ∧ ∀ a' ∈ S, ∀ b' ∈ T, G.Adj a' b' → a' = a ∧ b' = b`.

## 4. Distances — REPO `.../VertexDistance.lean`

| Name | Statement (informal) |
|---|---|
| `distToSet` (def) | `min_{s ∈ S} dist v s` (0 if `S = ∅`) |
| `ecc` (def) | `max_{v ∉ S} distToSet v S` (0 if `S = univ`) — the C144 `e`-functional |
| `eccSet` (def) | `max_{ALL v} distToSet v S` (0 if `S = ∅`) — the C142 `f`-functional |
| `distMin` (def) | `min_{v ∉ S} distToSet v S` |
| `path` / `isInducedPath` (defs) | induced-path number / list-based induced path predicate |
| `averageDistance`, `distavg`, `graphSquare`, `isInducedC4`, `countInducedC4`, even-distance defs | not needed for 142/144 |
| `computable_dist`, `dist_eq_computable` | BFS distance = `G.dist` (for decide-style checks) |

## 5. Eccentricity / center / periphery — REPO `.../Eccentricity.lean`

| Name | Statement (informal) |
|---|---|
| `maxEccentricityVertices` (def) | periphery `B = {v \| eccent v = ediam}` (the C142 base set) |
| `computable_ediam` / `ediam_eq_computable` | BFS diameter bridge |
| `computable_eccent` / `eccent_eq_computable` | BFS eccentricity bridge |
| `computable_radius` / `radius_eq_computable` | BFS radius bridge |

Mathlib itself provides: `G.dist`, `G.edist`, `G.eccent : ℕ∞`, `G.ediam : ℕ∞`,
`G.diam : ℕ`, `G.radius : ℕ∞`, `G.center : Set α`, `mem_center_iff`, `center_nonempty`,
`radius_ne_top_iff`, `edist_le_eccent`, `dist_le_diam`, `exists_dist_eq_diam`,
`exists_eccent_eq_ediam_of_finite`, `exists_edist_eq_radius_of_finite`,
`Connected.exists_path_of_dist`, `Connected.dist_triangle`.

## 6. Distance/tree bridges — SCRATCH `wowii_142/wave1/api.lean` (compiled; copied verbatim into `skeletons.lean`)

| Name | Statement (informal) |
|---|---|
| `dist_add_one_le_largestInducedTreeSize` | T1: `dist u v + 1 ≤ t(G)` (geodesics induce trees) |
| `distToSet_le_dist` | `distToSet v S ≤ dist v s` for `s ∈ S` |
| `exists_dist_eq_distToSet` | `distToSet` to nonempty set is realized by a member |
| `ecc_eq_zero_of_forall_mem` | `S = univ ⟹ ecc S = 0` |
| `exists_ecc_witness` | `ecc` realized by some `v ∉ S` (if any) |
| `ecc_le` | pointwise bound outside `S` ⟹ `ecc S ≤ n` |
| `exists_eccSet_witness` / `eccSet_le` | same for `eccSet` |
| `distToSet_center_le_radius_toNat` | `e`-side bound `d(v, C) ≤ r` (gives `e ≤ r`) |
| `distToSet_maxEccentricityVertices_le_diam` | `f`-side bound `d(v, B) ≤ D` (gives `f ≤ D`) |
| `radius_toNat_add_one_le_largestInducedTreeSize` | `r + 1 ≤ t(G)` |
| `diam_add_one_le_largestInducedTreeSize` | `D + 1 ≤ t(G)` |

## 7. Skeletons — SCRATCH `wowii_142/wave1/skeletons.lean` (compiled; exactly 2 `sorry`)

| Name | Status |
|---|---|
| `conjecture144_skeleton` | `(girth : ℝ) − 1 + ecc G G.center ≤ t(G)`; proved except branch cyclic ∧ `ecc G G.center ≠ 0` (line 146 `sorry`) |
| `conjecture142_skeleton` | `(2/3)·girth + eccSet G B ≤ t(G)`, `B = maxEccentricityVertices`; proved except cyclic ∧ `eccSet G B ≠ 0` (line 182 `sorry`) |

## 8. 141 wave scratch — `wowii_141/wave1/`, `wave1c/`

| Name | File | Statement (informal) |
|---|---|---|
| `IsTree.induce_union_leaves` | `wave1/star.lean` | attach a finset `W` of pairwise nonadjacent leaves all seeing the tree only at one vertex `v` ⟹ still a tree (special case of lemmaM fold, all bridges at `v`) |
| `rootedShortestPath` (+`_isPath`, `_length`) | `wave1/rooted_girth.lean` | chosen geodesic from root, length = dist |
| `rootedParent` (+`_eq_root`, `_adj`, `_dist_add_one`) | `wave1/rooted_girth.lean` | BFS parent function |
| `rootedParentGraph` (+`_adj_iff`, `_le`) | `wave1/rooted_girth.lean` | BFS parent graph ≤ G |
| `rootedParentGraph_connected/_dist_eq/_isAcyclic/_isTree` | `wave1/rooted_girth_stage2.lean` | BFS tree: spanning tree preserving distances from root |
| `girth_le_two_mul_dist_sup_add_one` | `wave1/rooted_girth_stage2.lean` | `girth ≤ 2·ecc(root) + 1` for every root (non-tree edge closes a short cycle through the BFS tree) |
| `overlap.lean` (wave1c) | | public copies of the now-private path helpers of §2 |
| `conjecture141_full` | `wave1c/final141.lean` | full 141 (superseded by repo `maxDegree_add_girth_le_largestInducedTreeSize_add_three`) |

## 9. 143 wave scratch — `wowii_143/wave2/` (compiled; primed variants avoid repo-name clashes)

| Name | File | Statement (informal) |
|---|---|---|
| `isAcyclic_of_induce_finset_univ_isTree` | `maxobs.lean`/`assemble.lean` | induced tree on `Finset.univ` ⟹ `G` acyclic |
| `Connected.exists_adj_finset_compl'` | both | same as repo unprimed |
| `exists_two_adj_of_max_card_induced_tree_superset` | both | two-adjacency certificate for max-CARD induced tree ⊇ `r` |
| `IsTree.girth_le_card_add_one_of_two_adj` | `cyccert.lean`/`assemble.lean` | outside `z` with 2 neighbors of tree on `s` ⟹ `girth ≤ s.card + 1` |
| `IsTree.girth_add_one_le_card_of_two_leaves_of_two_adj('` | `cyccert.lean`/`assemble.lean` | 2 leaves in tree + 2-adjacent outside vertex ⟹ `girth + 1 ≤ s.card` |
| `exists_distinct_degree_one_of_secondSmallestDegree_eq_one'` | `assemble.lean` | `σ(G) = 1` ⟹ two distinct degree-1 vertices (repo version in `Degrees.lean` unprimed) |
| `girth_add_one_le_largestInducedTreeSize_of_two_leaves'` | `assemble.lean` | two-leaf lemma (repo version unprimed) |
| `conjecture143_full` | `assemble.lean` | `girth + 1 ≤ t(G)·σ(G)` complete |

## 10. Verified-present Mathlib primitives (checked against `.lake/packages/mathlib` this session)

* `connected_induce_union` (`Connectivity/Subgraph.lean:608`) — glue two preconnected induced pieces along one edge.
* `Walk.exists_boundary_dart` (`Walks/Basic.lean:388`) — walk from inside `S` to outside `S` has a crossing dart.
* `Walk.rotate`, `IsCycle.rotate`, `mem_support_rotate_iff`, `rotate_darts`, `rotate_edges` (`Connectivity/WalkDecomp.lean`, `Paths.lean`).
* `Walk.darts_takeUntil_subset`, `darts_dropUntil_subset` + support/edges variants (`Connectivity/WalkDecomp.lean`).
* `Walk.dart_fst_mem_support_of_mem_darts` (`Walks/Basic.lean:260`), `Walk.dart_snd_mem_support_of_mem_darts` (`Walks/Operations.lean:438`), `Walk.snd_mem_support_of_mem_edges` (`Walks/Operations.lean:450`).
* `Walk.induce`, `Walk.map_induce`, `Walk.support_induce` (`Walks/Maps.lean:193-217`) — lift a walk contained in `s` into `G.induce s`.
* `Walk.map_isCycle_iff_of_injective`, `Walk.map_isPath_iff_of_injective`, `Embedding.induce`.
* `List.inj_on_of_nodup_map` (`Data/List/Nodup.lean:198`) — nodup mapped list ⟹ map injective on members (used for "a trail repeats no edge").
* Girth (ℕ-valued, junk 0): `girth_eq_zero ↔ IsAcyclic`, `three_le_girth`, `girth_le_length`, `exists_girth_eq_length` (`Girth.lean`).
* `Finset.card_union_of_disjoint`, `Finset.disjoint_union_left`, `Finset.disjoint_left`.

## 11. Known ABSENT (nothing in repo, scratch, or Mathlib) — see NEEDS_E_SIDE.md

* T3 chordlessness/isometry of shortest cycles (any form).
* Cycle-position arithmetic (`d_K`, arcs, antipodes) on a girth witness walk.
* `Walk.support_dropLast` / `support_take`-style support characterizations (blocks the
  z-selectable `K.erase z` supplier; current supplier is ∃-form only).
* Branch components of `G − K` as reusable finset decomposition.
* Any `center`/`radius` vs `diam` comparison (`D ≥ r`, `D ≥ r+1` under `e ≥ 1`).
