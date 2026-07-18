import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.VertexDistance
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Eccentricity

/-!
Wave-1 skeletons for WOWII Conjectures 142 and 144.

Each skeleton is fully proved except for the single hard cyclic branch
(cyclic graph with nonzero set-eccentricity term), which is left as an
explicitly allowed `sorry`.

The API lemmas below are copied verbatim from `api.lean` (stage-1, compiled
clean); only the lemmas actually used by the skeletons are included.
-/

namespace SimpleGraph

open Classical

variable {α : Type*} [Fintype α] [DecidableEq α] {G : SimpleGraph α}

/-! ### Copied Wave-1 API (from `api.lean`) -/

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

/-! ### Skeletons -/

/-- Skeleton for WOWII Conjecture 144:
`tree(G) ≥ girth(G) - 1 + ecc(center(G))` for connected `G`.
Fully proved except the cyclic branch with `ecc G G.center ≠ 0`. -/
theorem conjecture144_skeleton [Nontrivial α] (G : SimpleGraph α) (h : G.Connected) :
    (G.girth : ℝ) - 1 + (ecc G G.center : ℝ) ≤ (largestInducedTreeSize G : ℝ) := by
  by_cases hcyc : G.IsAcyclic
  · -- Acyclic: girth is the junk value 0; use the radius bounds.
    have hg : G.girth = 0 := hcyc.girth_eq_zero
    have hecc : ecc G G.center ≤ G.radius.toNat :=
      ecc_le fun v _ => distToSet_center_le_radius_toNat h v
    have ht : G.radius.toNat + 1 ≤ largestInducedTreeSize G :=
      radius_toNat_add_one_le_largestInducedTreeSize h
    have hecc' : (ecc G G.center : ℝ) ≤ (G.radius.toNat : ℝ) := by exact_mod_cast hecc
    have ht' : (G.radius.toNat : ℝ) + 1 ≤ (largestInducedTreeSize G : ℝ) := by
      exact_mod_cast ht
    rw [hg]
    push_cast
    linarith
  · by_cases he : ecc G G.center = 0
    · -- Cyclic with zero center-eccentricity: shortest cycle minus a vertex.
      have hg3 : 3 ≤ G.girth := three_le_girth hcyc
      have hnat : G.girth - 1 ≤ largestInducedTreeSize G :=
        girth_sub_one_le_largestInducedTreeSize G hcyc
      have hcast : (G.girth : ℝ) - 1 ≤ (largestInducedTreeSize G : ℝ) := by
        have h1 : ((G.girth - 1 : ℕ) : ℝ) ≤ (largestInducedTreeSize G : ℝ) := by
          exact_mod_cast hnat
        rwa [Nat.cast_sub (by omega), Nat.cast_one] at h1
      have he' : (ecc G G.center : ℝ) = 0 := by rw [he]; norm_num
      rw [he']
      linarith
    · sorry -- HARD BRANCH (gate-dependent): cyclic with ecc G G.center ≠ 0

/-- Skeleton for WOWII Conjecture 142:
`tree(G) ≥ (2/3)·girth(G) + eccSet(B)` for connected `G`, where `B` is the set
of vertices of maximum eccentricity.
Fully proved except the cyclic branch with `eccSet G B ≠ 0`. -/
theorem conjecture142_skeleton [Nontrivial α] (G : SimpleGraph α) [DecidableRel G.Adj]
    (h : G.Connected) :
    let B : Set α := (maxEccentricityVertices G : Set α)
    (2 : ℝ) / 3 * (G.girth : ℝ) + (eccSet G B : ℝ) ≤ (largestInducedTreeSize G : ℝ) := by
  intro B
  by_cases hcyc : G.IsAcyclic
  · -- Acyclic: girth is the junk value 0; use the diameter bounds.
    have hg : G.girth = 0 := hcyc.girth_eq_zero
    have hf : eccSet G B ≤ G.diam :=
      eccSet_le fun v => distToSet_maxEccentricityVertices_le_diam h v
    have ht : G.diam + 1 ≤ largestInducedTreeSize G :=
      diam_add_one_le_largestInducedTreeSize h
    have hf' : (eccSet G B : ℝ) ≤ (G.diam : ℝ) := by exact_mod_cast hf
    have ht' : (G.diam : ℝ) + 1 ≤ (largestInducedTreeSize G : ℝ) := by exact_mod_cast ht
    rw [hg]
    push_cast
    linarith
  · by_cases hf : eccSet G B = 0
    · -- Cyclic with zero periphery-eccentricity: (2/3)·g ≤ g - 1 since g ≥ 3.
      have hg3 : 3 ≤ G.girth := three_le_girth hcyc
      have hnat : G.girth - 1 ≤ largestInducedTreeSize G :=
        girth_sub_one_le_largestInducedTreeSize G hcyc
      have hg3' : (3 : ℝ) ≤ (G.girth : ℝ) := by exact_mod_cast hg3
      have hcast : (G.girth : ℝ) - 1 ≤ (largestInducedTreeSize G : ℝ) := by
        have h1 : ((G.girth - 1 : ℕ) : ℝ) ≤ (largestInducedTreeSize G : ℝ) := by
          exact_mod_cast hnat
        rwa [Nat.cast_sub (by omega), Nat.cast_one] at h1
      have hf' : (eccSet G B : ℝ) = 0 := by rw [hf]; norm_num
      rw [hf']
      linarith
    · sorry -- HARD BRANCH (gate-dependent): cyclic with eccSet G B ≠ 0

end SimpleGraph
