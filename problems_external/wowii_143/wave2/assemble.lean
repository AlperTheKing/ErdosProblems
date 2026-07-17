import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Degrees
import Mathlib.Data.Set.Finite.Lemmas

/-!
Wave-2 assembly for Graffiti.pc / Written on the Wall II Conjecture 143:

  For a simple connected graph `G` with `0 < σ(G)`,
  `girth(G) + 1 ≤ tree(G) * σ(G)`.

Self-contained (modulo the standard imports): stage-1 lemmas (maxobs, cyccert),
the ported seed/max/degree lemmas, the singleton bound, the two-leaf branch, and
the full theorem `conjecture143_full`.

Names carrying a trailing prime are self-contained copies of lemmas that a
parallel session has meanwhile also added (identical statements) to the imported
`FormalConjecturesForMathlib...LargestInducedTree` / `...Degrees` oleans;
redeclaring the same fully-qualified name is impossible.
-/

namespace SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α]

section Stage1

variable {G : SimpleGraph α}

omit [DecidableEq α] in
/-- If the subgraph induced on all vertices is a tree, the graph is acyclic. -/
lemma isAcyclic_of_induce_finset_univ_isTree
    (h : (G.induce ((Finset.univ : Finset α) : Set α)).IsTree) : G.IsAcyclic := by
  rw [Finset.coe_univ] at h
  intro v c hc
  let f := (induceUnivIso G).symm
  exact h.IsAcyclic (c.map f.toHom)
    ((Walk.map_isCycle_iff_of_injective f.toEmbedding.injective).2 hc)

omit [DecidableEq α] in
/-- A nonempty proper vertex set in a connected graph has an edge across its boundary. -/
lemma Connected.exists_adj_finset_compl'
    (hG : G.Connected) {s : Finset α} (hne : s.Nonempty) (hsu : s ≠ Finset.univ) :
    ∃ z ∉ s, ∃ a ∈ s, G.Adj z a := by
  obtain ⟨u, hu⟩ := hne
  have hzex : ∃ z : α, z ∉ s := by
    by_contra hn
    push_neg at hn
    exact hsu (Finset.eq_univ_of_forall hn)
  obtain ⟨z, hz⟩ := hzex
  obtain ⟨p⟩ := hG u z
  obtain ⟨d, _, hd_in, hd_out⟩ :=
    p.exists_boundary_dart (s : Set α) (by simpa) (by simpa)
  exact ⟨d.snd, by simpa using hd_out, d.fst, by simpa using hd_in, d.adj.symm⟩

/-- A boundary vertex of a maximum-cardinality induced tree containing `r` has two
distinct neighbors in the tree. -/
lemma exists_two_adj_of_max_card_induced_tree_superset
    {r s : Finset α} (hG : G.Connected) (hrs : r ⊆ s)
    (hT : (G.induce (s : Set α)).IsTree)
    (hmax : ∀ t : Finset α, r ⊆ t → (G.induce (t : Set α)).IsTree → t.card ≤ s.card)
    (hsu : s ≠ Finset.univ) :
    ∃ z ∉ s, ∃ a ∈ s, ∃ b ∈ s, a ≠ b ∧ G.Adj z a ∧ G.Adj z b := by
  have hne : s.Nonempty := by
    obtain ⟨⟨x, hx⟩⟩ := hT.isConnected.nonempty
    exact ⟨x, by simpa using hx⟩
  obtain ⟨z, hz, a, ha, hza⟩ := hG.exists_adj_finset_compl' hne hsu
  by_cases hex : ∃ b ∈ s, b ≠ a ∧ G.Adj z b
  · obtain ⟨b, hb, hba, hzb⟩ := hex
    exact ⟨z, hz, a, ha, b, hb, hba.symm, hza, hzb⟩
  · have huniq : ∀ ⦃b : α⦄, b ∈ s → G.Adj z b → b = a := by
      intro b hb hzb
      by_contra hba
      exact hex ⟨b, hb, hba, hzb⟩
    have hT' := hT.induce_insert_of_unique_adj hz ha hza huniq
    have hrs' : r ⊆ insert z s := fun v hv => Finset.mem_insert_of_mem (hrs hv)
    have hle := hmax (insert z s) hrs' hT'
    have hcard := Finset.card_insert_of_notMem hz
    omega

omit [Fintype α] [DecidableEq α] in
/-- From an induced tree on `s` and a vertex `z ∉ s` with two distinct neighbors
`a, b ∈ s`, produce the tree path `q` from `a` to `b` together with the cycle `c`
obtained by closing it up through `z`. -/
private lemma exists_cycle_data {s : Finset α} (hT : (G.induce (s : Set α)).IsTree)
    {z a b : α} (hz : z ∉ s) (ha : a ∈ s) (hb : b ∈ s) (hab : a ≠ b)
    (hza : G.Adj z a) (hzb : G.Adj z b) :
    ∃ (q : G.Walk a b) (c : G.Walk b b), q.IsPath ∧ c.IsCycle ∧
      (∀ w ∈ q.support, w ∈ s) ∧ c.length = q.length + 2 ∧
      (∀ w ∈ q.support, w ∈ c.support) := by
  obtain ⟨p, hp, -⟩ := hT.existsUnique_path ⟨a, by simpa using ha⟩ ⟨b, by simpa using hb⟩
  let e : G.induce (s : Set α) ↪g G := Embedding.induce _
  let q : G.Walk a b := p.map e.toHom
  have hq : q.IsPath := (Walk.map_isPath_iff_of_injective e.injective).2 hp
  have hqs : ∀ w ∈ q.support, w ∈ s := by
    intro w hw
    dsimp [q] at hw
    rw [Walk.support_map] at hw
    obtain ⟨w', _, rfl⟩ := List.mem_map.mp hw
    exact w'.property
  have hzq : z ∉ q.support := fun h => hz (hqs z h)
  have hw1 : (Walk.cons hza q).IsPath := hq.cons hzq
  let P : G.Path z b := ⟨Walk.cons hza q, hw1⟩
  have he : s(b, z) ∉ (P : G.Walk z b).edges := by
    intro hmem
    rw [Walk.edges_cons, List.mem_cons] at hmem
    rcases hmem with heq | hmem
    · rw [Sym2.eq_iff] at heq
      rcases heq with ⟨hbz, -⟩ | ⟨hba, -⟩
      · exact hz (hbz ▸ hb)
      · exact hab hba.symm
    · exact hzq (Walk.snd_mem_support_of_mem_edges q hmem)
  have hc : (Walk.cons hzb.symm (P : G.Walk z b)).IsCycle := Path.cons_isCycle P hzb.symm he
  refine ⟨q, Walk.cons hzb.symm (P : G.Walk z b), hq, hc, hqs, by simp [P], ?_⟩
  intro w hw
  rw [Walk.support_cons]
  exact List.mem_cons_of_mem _ (by rw [Walk.support_cons]; exact List.mem_cons_of_mem _ hw)

omit [Fintype α] in
/-- Attaching an outside vertex with two neighbors of an induced tree on `s`
creates a cycle of length at most `s.card + 1`, so the girth is at most that. -/
lemma IsTree.girth_le_card_add_one_of_two_adj
    {s : Finset α} (hT : (G.induce (s : Set α)).IsTree) {z a b : α}
    (hz : z ∉ s) (ha : a ∈ s) (hb : b ∈ s) (hab : a ≠ b)
    (hza : G.Adj z a) (hzb : G.Adj z b) :
    G.girth ≤ s.card + 1 := by
  obtain ⟨q, c, hq, hc, hqs, hlen, -⟩ := exists_cycle_data hT hz ha hb hab hza hzb
  have hg : G.girth ≤ c.length := G.girth_le_length hc
  have hsub : q.support.toFinset ⊆ s := fun w hw => hqs w (List.mem_toFinset.mp hw)
  have hcard : q.support.toFinset.card = q.length + 1 := by
    rw [List.toFinset_card_of_nodup hq.support_nodup, Walk.length_support]
  have hle : q.length + 1 ≤ s.card := hcard ▸ Finset.card_le_card hsub
  omega

/-- A vertex of degree one cannot lie on a cycle. -/
private lemma Walk.IsCycle.notMem_support_of_degree_eq_one [DecidableRel G.Adj]
    {v x : α} {c : G.Walk v v} (hc : c.IsCycle) (hx : G.degree x = 1) :
    x ∉ c.support := by
  intro hxc
  let r : G.Walk x x := c.rotate hxc
  have hr : r.IsCycle := hc.rotate hxc
  have hadj_snd : G.Adj x r.snd := r.adj_snd hr.not_nil
  have hadj_pen : G.Adj x r.penultimate := (r.adj_penultimate hr.not_nil).symm
  obtain ⟨u, -, huniq⟩ := degree_eq_one_iff_existsUnique_adj.mp hx
  exact hr.snd_ne_penultimate ((huniq _ hadj_snd).trans (huniq _ hadj_pen).symm)

/-- If the induced tree on `s` contains two leaves of `G` and an outside vertex has
two neighbors in `s`, then the girth is strictly less than `s.card`. -/
lemma IsTree.girth_add_one_le_card_of_two_leaves_of_two_adj'
    [DecidableRel G.Adj] {s : Finset α} (hT : (G.induce (s : Set α)).IsTree)
    {x y z a b : α} (hxs : x ∈ s) (hys : y ∈ s) (hxy : x ≠ y)
    (hx : G.degree x = 1) (hy : G.degree y = 1)
    (hz : z ∉ s) (ha : a ∈ s) (hb : b ∈ s) (hab : a ≠ b)
    (hza : G.Adj z a) (hzb : G.Adj z b) :
    G.girth + 1 ≤ s.card := by
  obtain ⟨q, c, hq, hc, hqs, hlen, hsub⟩ := exists_cycle_data hT hz ha hb hab hza hzb
  have hg : G.girth ≤ c.length := G.girth_le_length hc
  have hxq : x ∉ q.support := fun h => hc.notMem_support_of_degree_eq_one hx (hsub x h)
  have hyq : y ∉ q.support := fun h => hc.notMem_support_of_degree_eq_one hy (hsub y h)
  have htcard : q.support.toFinset.card = q.length + 1 := by
    rw [List.toFinset_card_of_nodup hq.support_nodup, Walk.length_support]
  have hyt : y ∉ q.support.toFinset := by simpa using hyq
  have hxyt : x ∉ insert y q.support.toFinset := by
    simp only [Finset.mem_insert, not_or]
    exact ⟨hxy, by simpa using hxq⟩
  have hsubset : insert x (insert y q.support.toFinset) ⊆ s := by
    intro w hw
    rcases Finset.mem_insert.mp hw with rfl | hw
    · exact hxs
    rcases Finset.mem_insert.mp hw with rfl | hw
    · exact hys
    · exact hqs w (List.mem_toFinset.mp hw)
  have hcard2 : (insert x (insert y q.support.toFinset)).card = q.length + 3 := by
    rw [Finset.card_insert_of_notMem hxyt, Finset.card_insert_of_notMem hyt, htcard]
  have hle : q.length + 3 ≤ s.card := hcard2 ▸ Finset.card_le_card hsubset
  omega

end Stage1

omit [Fintype α] in
/-- Every pair of vertices in a connected graph lies in an induced tree. -/
lemma Connected.exists_induced_tree_containing_pair' {G : SimpleGraph α}
    (hG : G.Connected) (x y : α) :
    ∃ s : Finset α, x ∈ s ∧ y ∈ s ∧ (G.induce (s : Set α)).IsTree := by
  obtain ⟨p, _, hp⟩ := hG.exists_path_of_dist x y
  refine ⟨p.support.toFinset, ?_, ?_, ?_⟩
  · simp
  · simp
  · exact Walk.induce_support_isTree_of_length_eq_dist p hp

omit [DecidableEq α] in
/-- A nonempty family of induced trees with prescribed vertices has a largest member. -/
lemma exists_maximum_induced_tree_containing' (G : SimpleGraph α) (r : Finset α)
    (hr : ∃ s : Finset α, r ⊆ s ∧ (G.induce (s : Set α)).IsTree) :
    ∃ s : Finset α,
      r ⊆ s ∧
      (G.induce (s : Set α)).IsTree ∧
      ∀ t : Finset α, r ⊆ t →
        (G.induce (t : Set α)).IsTree → t.card ≤ s.card := by
  let A : Set (Finset α) :=
    {s | r ⊆ s ∧ (G.induce (s : Set α)).IsTree}
  have hAfin : A.Finite := Set.toFinite A
  have hAne : A.Nonempty := by
    obtain ⟨s, hrs, hT⟩ := hr
    exact ⟨s, hrs, hT⟩
  obtain ⟨s, hsA, hmax⟩ := Set.exists_max_image A Finset.card hAfin hAne
  dsimp [A] at hsA hmax
  refine ⟨s, hsA.1, hsA.2, ?_⟩
  intro t hrt hT
  exact hmax t ⟨hrt, hT⟩

omit [DecidableEq α] in
/-- In a nontrivial preconnected finite graph, second-smallest degree one forces two leaves. -/
lemma exists_distinct_degree_one_of_secondSmallestDegree_eq_one' [Nontrivial α]
    (G : SimpleGraph α) [DecidableRel G.Adj] (hG : G.Preconnected)
    (hσ : secondSmallestDegree G = 1) :
    ∃ x y : α, x ≠ y ∧ G.degree x = 1 ∧ G.degree y = 1 := by
  let ds := degreeSequence G
  have hlen : 2 ≤ ds.length := by
    simpa [ds, degreeSequence] using Fintype.one_lt_card (α := α)
  obtain ⟨a, b, tail, hds⟩ : ∃ a b tail, ds = a :: b :: tail := by
    cases h : ds with
    | nil => simp [h] at hlen
    | cons a rest =>
        cases hrest : rest with
        | nil => simp [h, hrest] at hlen
        | cons b tail => exact ⟨a, b, tail, rfl⟩
  have hb : b = 1 := by
    simpa [secondSmallestDegree, ds, hds] using hσ
  have hsorted : ds.Pairwise (· ≤ ·) := by
    simp [ds, degreeSequence]
  have hab : a ≤ b := by
    simpa [hds] using hsorted.rel_get_of_lt (a := ⟨0, by simp [hds]⟩)
      (b := ⟨1, by simp [hds]⟩) (by simp)
  have ha_mem : a ∈ ds := by simp [hds]
  have ha_pos : 0 < a := by
    have ha_map : a ∈ Finset.univ.val.map (fun v : α => G.degree v) := by
      simpa [ds, degreeSequence] using ha_mem
    obtain ⟨v, -, rfl⟩ := Multiset.mem_map.mp ha_map
    exact hG.degree_pos_of_nontrivial v
  have ha : a = 1 := by omega
  have hcount : 2 ≤ ds.count 1 := by simp [hds, ha, hb]
  have hcoeds : (↑ds : Multiset ℕ) =
      Finset.univ.val.map (fun v : α => G.degree v) := by
    simp [ds, degreeSequence]
  have hcountm : 2 ≤
      (Finset.univ.val.map (fun v : α => G.degree v)).count 1 := by
    rw [← hcoeds, Multiset.coe_count]
    exact hcount
  have hleaves : 2 ≤ (Finset.univ.filter fun v : α => G.degree v = 1).card := by
    rw [Multiset.count_map] at hcountm
    simpa only [← Finset.filter_val, eq_comm] using hcountm
  have htwo : 1 < (Finset.univ.filter fun v : α => G.degree v = 1).card := by omega
  obtain ⟨x, hx, y, hy, hxy⟩ := Finset.one_lt_card.mp htwo
  exact ⟨x, y, hxy, (Finset.mem_filter.mp hx).2, (Finset.mem_filter.mp hy).2⟩

omit [DecidableEq α] in
/-- Every finite graph with a vertex has an induced tree on one vertex. -/
lemma one_le_largestInducedTreeSize' [Nonempty α] (G : SimpleGraph α) :
    1 ≤ largestInducedTreeSize G := by
  obtain ⟨v⟩ := (inferInstance : Nonempty α)
  have hset : ((({v} : Finset α)) : Set α) = {v} := by simp
  have hT : (G.induce (({v} : Finset α) : Set α)).IsTree := by
    rw [hset]
    letI : Nonempty ↥({v} : Set α) := ⟨⟨v, by simp⟩⟩
    letI : Subsingleton ↥({v} : Set α) := ⟨fun a b => by
      apply Subtype.ext
      have ha : (a : α) = v := by simpa only [Set.mem_singleton_iff] using a.property
      have hb : (b : α) = v := by simpa only [Set.mem_singleton_iff] using b.property
      exact ha.trans hb.symm⟩
    exact IsTree.of_subsingleton
  simpa using card_le_largestInducedTreeSize hT

/-- Two distinct leaves in a connected cyclic graph give an induced tree of order
at least `girth + 1`. -/
lemma girth_add_one_le_largestInducedTreeSize_of_two_leaves'
    (G : SimpleGraph α) [DecidableRel G.Adj] (hG : G.Connected) (hcyc : ¬ G.IsAcyclic)
    {x y : α} (hxy : x ≠ y) (hx : G.degree x = 1) (hy : G.degree y = 1) :
    G.girth + 1 ≤ largestInducedTreeSize G := by
  obtain ⟨s₀, hxs₀, hys₀, hT₀⟩ := hG.exists_induced_tree_containing_pair' x y
  have hr : ({x, y} : Finset α) ⊆ s₀ :=
    Finset.insert_subset_iff.mpr ⟨hxs₀, Finset.singleton_subset_iff.mpr hys₀⟩
  obtain ⟨s, hrs, hT, hmax⟩ :=
    exists_maximum_induced_tree_containing' G {x, y} ⟨s₀, hr, hT₀⟩
  have hxs : x ∈ s := hrs (by simp)
  have hys : y ∈ s := hrs (by simp)
  have hsu : s ≠ Finset.univ := by
    intro hsu
    subst hsu
    exact hcyc (isAcyclic_of_induce_finset_univ_isTree hT)
  obtain ⟨z, hz, a, ha, b, hb, hab, hza, hzb⟩ :=
    exists_two_adj_of_max_card_induced_tree_superset hG hrs hT hmax hsu
  exact (hT.girth_add_one_le_card_of_two_leaves_of_two_adj'
    hxs hys hxy hx hy hz ha hb hab hza hzb).trans (card_le_largestInducedTreeSize hT)

/-- **WOWII Conjecture 143** (denominator-free form): for a finite nontrivial connected
graph `G` with positive second-smallest degree `σ(G)`,
`girth(G) + 1 ≤ tree(G) * σ(G)`. -/
theorem conjecture143_full [Nontrivial α] (G : SimpleGraph α) [DecidableRel G.Adj]
    (h : G.Connected) (hσ : 0 < secondSmallestDegree G) :
    (G.girth : ℝ) + 1 ≤ (largestInducedTreeSize G : ℝ) * (secondSmallestDegree G : ℝ) := by
  have hnat : G.girth + 1 ≤ largestInducedTreeSize G * secondSmallestDegree G := by
    by_cases hcyc : G.IsAcyclic
    · have hg0 : G.girth = 0 := girth_eq_zero.mpr hcyc
      have ht : 1 ≤ largestInducedTreeSize G := one_le_largestInducedTreeSize' G
      have hprod : 1 * 1 ≤ largestInducedTreeSize G * secondSmallestDegree G :=
        Nat.mul_le_mul ht hσ
      rw [hg0]
      simpa using hprod
    · have hg3 : 3 ≤ G.girth := three_le_girth hcyc
      rcases Nat.lt_or_ge (secondSmallestDegree G) 2 with hσ1 | hσ2
      · have hσeq : secondSmallestDegree G = 1 := by omega
        obtain ⟨x, y, hxy, hx, hy⟩ :=
          exists_distinct_degree_one_of_secondSmallestDegree_eq_one' G h.preconnected hσeq
        rw [hσeq, Nat.mul_one]
        exact girth_add_one_le_largestInducedTreeSize_of_two_leaves' G h hcyc hxy hx hy
      · have ht := girth_sub_one_le_largestInducedTreeSize G hcyc
        have h2t : G.girth + 1 ≤ largestInducedTreeSize G * 2 := by omega
        exact h2t.trans (Nat.mul_le_mul (Nat.le_refl _) hσ2)
  exact_mod_cast hnat

end SimpleGraph
