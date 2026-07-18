import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.VertexDistance
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Eccentricity

/-!
Wave-1 API for WOWII Conjecture 142/144 work.

Contents:
* `dist_add_one_le_largestInducedTreeSize` : shortest paths are induced trees.
* `distToSet_le_dist`, `exists_dist_eq_distToSet` : basics for `distToSet`.
* `ecc_eq_zero_of_forall_mem`, `exists_ecc_witness`, `ecc_le` : basics for `ecc`.
* `exists_eccSet_witness`, `eccSet_le` : basics for `eccSet`.
* `distToSet_center_le_radius_toNat`, `distToSet_maxEccentricityVertices_le_diam` :
  distance-to-center / distance-to-periphery bounds.
* `radius_toNat_add_one_le_largestInducedTreeSize`,
  `diam_add_one_le_largestInducedTreeSize` : radius/diam corollaries.
-/

namespace SimpleGraph

open Classical

variable {α : Type*} [Fintype α] [DecidableEq α] {G : SimpleGraph α}

/-- Any two vertices of a connected graph lie on an induced tree of order
`dist u v + 1`, so `dist u v + 1 ≤ largestInducedTreeSize G`. -/
lemma dist_add_one_le_largestInducedTreeSize (hG : G.Connected) (u v : α) :
    G.dist u v + 1 ≤ largestInducedTreeSize G := by
  obtain ⟨p, hp_path, hp_len⟩ := hG.exists_path_of_dist u v
  have hT := p.induce_support_isTree_of_length_eq_dist hp_len
  have hcard : p.support.toFinset.card = p.length + 1 := by
    rw [List.toFinset_card_of_nodup hp_path.support_nodup, Walk.length_support]
  have hle := card_le_largestInducedTreeSize hT
  omega

omit [DecidableEq α] in
/-- `distToSet` is bounded above by the distance to any member of the set. -/
lemma distToSet_le_dist (v : α) {S : Set α} {s : α} (hs : s ∈ S) :
    G.distToSet v S ≤ G.dist v s := by
  unfold distToSet
  split_ifs with h
  · exact Finset.min'_le _ _ (Finset.mem_image_of_mem _ (Set.mem_toFinset.mpr hs))
  · exact Nat.zero_le _

omit [DecidableEq α] in
/-- `distToSet` to a nonempty set is realized by some member of the set. -/
lemma exists_dist_eq_distToSet {S : Set α} (hS : S.Nonempty) (v : α) :
    ∃ s ∈ S, G.dist v s = G.distToSet v S := by
  unfold distToSet
  split_ifs with h
  · obtain ⟨s, hs, hval⟩ :=
      Finset.mem_image.mp (Finset.min'_mem _ (h.image fun s => G.dist v s))
    exact ⟨s, Set.mem_toFinset.mp hs, hval⟩
  · exact absurd (Set.toFinset_nonempty.mpr hS) h

omit [DecidableEq α] in
/-- If every vertex belongs to `S` then `ecc G S = 0` (the outer maximum ranges
over the empty complement). -/
lemma ecc_eq_zero_of_forall_mem {S : Set α} (h : ∀ v, v ∈ S) : G.ecc S = 0 := by
  simp only [ecc]
  split_ifs with hne
  · obtain ⟨w, hw⟩ := hne
    exact absurd (h w) (Finset.mem_filter.mp hw).2
  · rfl

omit [DecidableEq α] in
/-- `ecc G S` is realized: if the complement of `S` is nonempty, some vertex
outside `S` attains it. -/
lemma exists_ecc_witness {S : Set α} (h : ∃ v, v ∉ S) :
    ∃ v ∉ S, G.distToSet v S = G.ecc S := by
  simp only [ecc]
  split_ifs with hne
  · obtain ⟨w, hw, hval⟩ :=
      Finset.mem_image.mp (Finset.max'_mem _ (hne.image fun v => G.distToSet v S))
    exact ⟨w, (Finset.mem_filter.mp hw).2, hval⟩
  · obtain ⟨v, hv⟩ := h
    exact absurd ⟨v, Finset.mem_filter.mpr ⟨Finset.mem_univ v, hv⟩⟩ hne

omit [DecidableEq α] in
/-- Upper bound for `ecc` from a pointwise bound outside `S`. -/
lemma ecc_le {S : Set α} {n : ℕ} (h : ∀ v ∉ S, G.distToSet v S ≤ n) :
    G.ecc S ≤ n := by
  simp only [ecc]
  split_ifs with hne
  · apply Finset.max'_le
    intro y hy
    obtain ⟨w, hw, rfl⟩ := Finset.mem_image.mp hy
    exact h w (Finset.mem_filter.mp hw).2
  · exact Nat.zero_le n

omit [DecidableEq α] in
/-- `eccSet G S` is realized by some vertex. -/
lemma exists_eccSet_witness [Nonempty α] (S : Set α) :
    ∃ v, G.distToSet v S = G.eccSet S := by
  simp only [eccSet]
  split_ifs with hne
  · obtain ⟨w, -, hval⟩ := Finset.mem_image.mp (Finset.max'_mem _ hne)
    exact ⟨w, hval⟩
  · exact absurd (Finset.univ_nonempty.image _) hne

omit [DecidableEq α] in
/-- Upper bound for `eccSet` from a pointwise bound. -/
lemma eccSet_le {S : Set α} {n : ℕ} (h : ∀ v, G.distToSet v S ≤ n) :
    G.eccSet S ≤ n := by
  simp only [eccSet]
  split_ifs with hne
  · apply Finset.max'_le
    intro y hy
    obtain ⟨w, -, rfl⟩ := Finset.mem_image.mp hy
    exact h w
  · exact Nat.zero_le n

omit [DecidableEq α] in
/-- Every vertex of a connected graph is within `radius` (as a natural number)
of the center. -/
lemma distToSet_center_le_radius_toNat [Nonempty α] (hG : G.Connected) (v : α) :
    G.distToSet v G.center ≤ G.radius.toNat := by
  obtain ⟨c₀, hc₀⟩ := center_nonempty (G := G)
  refine (distToSet_le_dist v hc₀).trans ?_
  have hrad : G.radius ≠ ⊤ := radius_ne_top_iff.mpr hG
  have h1 : (G.dist v c₀ : ℕ∞) ≤ G.radius := by
    rw [(hG.preconnected v c₀).coe_dist_eq_edist, edist_comm,
      ← (mem_center_iff c₀).mp hc₀]
    exact edist_le_eccent
  have h2 := ENat.toNat_le_toNat h1 hrad
  simpa using h2

omit [DecidableEq α] in
/-- Every vertex of a connected graph is within `diam` of the periphery
(the set of vertices of maximum eccentricity). -/
lemma distToSet_maxEccentricityVertices_le_diam [Nonempty α] (hG : G.Connected)
    (v : α) :
    G.distToSet v (maxEccentricityVertices G) ≤ G.diam := by
  obtain ⟨b₀, hb₀⟩ := exists_eccent_eq_ediam_of_finite (G := G)
  have hb₀mem : b₀ ∈ maxEccentricityVertices G := hb₀
  exact (distToSet_le_dist v hb₀mem).trans
    (dist_le_diam (connected_iff_ediam_ne_top.mp hG))

/-- Radius corollary: `largestInducedTreeSize G ≥ radius + 1` for connected `G`. -/
lemma radius_toNat_add_one_le_largestInducedTreeSize [Nonempty α]
    (hG : G.Connected) :
    G.radius.toNat + 1 ≤ largestInducedTreeSize G := by
  obtain ⟨u, v, huv⟩ := exists_edist_eq_radius_of_finite (G := G)
  have hcoe : (G.dist u v : ℕ∞) = G.radius := by
    rw [(hG.preconnected u v).coe_dist_eq_edist, huv]
  have hduv : G.dist u v = G.radius.toNat := by
    rw [← hcoe]
    simp
  calc G.radius.toNat + 1 = G.dist u v + 1 := by rw [hduv]
    _ ≤ _ := dist_add_one_le_largestInducedTreeSize hG u v

/-- Diameter corollary: `largestInducedTreeSize G ≥ diam + 1` for connected `G`. -/
lemma diam_add_one_le_largestInducedTreeSize [Nonempty α] (hG : G.Connected) :
    G.diam + 1 ≤ largestInducedTreeSize G := by
  obtain ⟨u, v, huv⟩ := exists_dist_eq_diam (G := G)
  rw [← huv]
  exact dist_add_one_le_largestInducedTreeSize hG u v

end SimpleGraph
