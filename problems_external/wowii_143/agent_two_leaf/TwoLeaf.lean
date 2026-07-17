import FormalConjectures.Util.ProblemImports

/-! Scratch formalization of the two-leaf branch of WOWII Conjecture 143. -/

namespace AgentTwoLeaf

open Classical SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α]

omit [DecidableEq α] in
lemma card_le_largestInducedTreeSize {G : SimpleGraph α} {s : Finset α}
    (hs : (G.induce (s : Set α)).IsTree) :
    s.card ≤ largestInducedTreeSize G := by
  unfold largestInducedTreeSize
  apply le_csSup
  · refine ⟨Fintype.card α, ?_⟩
    intro n hn
    obtain ⟨t, rfl, _⟩ := hn
    exact Finset.card_le_univ t
  · exact ⟨s, rfl, hs⟩

omit [Fintype α] in
lemma Walk.induce_support_isTree_of_length_eq_dist {G : SimpleGraph α} {u v : α}
    (p : G.Walk u v) (hp : p.length = G.dist u v) :
    (G.induce (p.support.toFinset : Set α)).IsTree := by
  induction p with
  | @nil u =>
      have hset : (↑(Walk.nil : G.Walk u u).support.toFinset : Set α) = {u} := by ext; simp
      have hsingle : (G.induce ({u} : Set α)).IsTree := by
        letI : Nonempty ↥({u} : Set α) := ⟨⟨u, by simp⟩⟩
        letI : Subsingleton ↥({u} : Set α) := ⟨fun a b => by
          apply Subtype.ext
          have ha : (a : α) = u := by simpa only [Set.mem_singleton_iff] using a.property
          have hb : (b : α) = u := by simpa only [Set.mem_singleton_iff] using b.property
          exact ha.trans hb.symm⟩
        exact IsTree.of_subsingleton
      rw [hset]
      exact hsingle
  | @cons u v w huv p ih =>
      have hptail : p.length = G.dist v w :=
        length_eq_dist_of_subwalk hp (Walk.isSubwalk_cons p huv)
      have hT := ih hptail
      have hpath : (p.cons huv).IsPath :=
        (p.cons huv).isPath_of_length_eq_dist hp
      have hu_not : u ∉ p.support.toFinset := by
        simpa using (List.nodup_cons.mp hpath.support_nodup).1
      have huniq : ∀ ⦃b : α⦄, b ∈ p.support.toFinset → G.Adj u b → b = v := by
        intro b hb hub
        have hbmem : b ∈ p.support := by simpa using hb
        obtain ⟨i, hi, hib⟩ := List.mem_iff_getElem.mp hbmem
        have hget : p.getVert i = b := by
          rw [← p.support_getElem_eq_getVert hi, hib]
        have hi_le : i ≤ p.length := by
          have hlen := p.length_support
          omega
        have hub' : G.Adj u (p.getVert i) := by simpa [hget] using hub
        let r : G.Walk u w := (p.drop i).cons hub'
        have hdistle : G.dist u w ≤ r.length := G.dist_le r
        have hlen : (p.cons huv).length ≤ r.length := by simpa [hp] using hdistle
        have hi0 : i = 0 := by
          simp only [Walk.length_cons, r, Walk.drop_length] at hlen
          omega
        subst i
        simpa using hget.symm
      have hsupp : (Walk.cons huv p).support.toFinset = insert u p.support.toFinset := by simp
      rw [hsupp]
      exact hT.induce_insert_of_unique_adj hu_not (by simp) huv huniq

omit [Fintype α] in
lemma Connected.exists_induced_tree_containing_pair {G : SimpleGraph α}
    (hG : G.Connected) (x y : α) :
    ∃ s : Finset α, x ∈ s ∧ y ∈ s ∧ (G.induce (s : Set α)).IsTree := by
  obtain ⟨p, _, hp⟩ := hG.exists_path_of_dist x y
  refine ⟨p.support.toFinset, ?_, ?_, ?_⟩
  · simp
  · simp
  · exact Walk.induce_support_isTree_of_length_eq_dist p hp

omit [DecidableEq α] in
lemma exists_maximum_induced_tree_containing (G : SimpleGraph α) (r : Finset α)
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

lemma Connected.exists_adj_finset_compl {G : SimpleGraph α}
    (hG : G.Connected) {s : Finset α} (hs : s.Nonempty) (hsu : s ≠ Finset.univ) :
    ∃ z ∉ s, ∃ a ∈ s, G.Adj z a := by
  obtain ⟨u, hu⟩ := hs
  have hzex : ∃ z : α, z ∉ s := by
    by_contra hn
    push_neg at hn
    apply hsu
    exact Finset.eq_univ_of_forall hn
  obtain ⟨z, hz⟩ := hzex
  obtain ⟨p⟩ := hG u z
  obtain ⟨d, _, hd_in, hd_out⟩ :=
    p.exists_boundary_dart (s : Set α) (by simpa) (by simpa)
  exact ⟨d.snd, by simpa using hd_out, d.fst, by simpa using hd_in, d.adj.symm⟩

lemma exists_two_adj_of_maximum_induced_tree_containing
    {G : SimpleGraph α} {r s : Finset α}
    (hG : G.Connected) (hrs : r ⊆ s) (hs : s.Nonempty)
    (hT : (G.induce (s : Set α)).IsTree)
    (hmax : ∀ t : Finset α, r ⊆ t →
      (G.induce (t : Set α)).IsTree → t.card ≤ s.card)
    (hsu : s ≠ Finset.univ) :
    ∃ z ∉ s, ∃ a ∈ s, ∃ b ∈ s,
      a ≠ b ∧ G.Adj z a ∧ G.Adj z b := by
  obtain ⟨z, hz, a, ha, hza⟩ := Connected.exists_adj_finset_compl hG hs hsu
  by_cases hex : ∃ b ∈ s, b ≠ a ∧ G.Adj z b
  · obtain ⟨b, hb, hba, hzb⟩ := hex
    exact ⟨z, hz, a, ha, b, hb, hba.symm, hza, hzb⟩
  · have huniq : ∀ ⦃b : α⦄, b ∈ s → G.Adj z b → b = a := by
      intro b hb hzb
      by_contra hba
      exact hex ⟨b, hb, hba, hzb⟩
    have hT' :=
      hT.induce_insert_of_unique_adj hz ha hza huniq
    have hrs' : r ⊆ insert z s := by
      intro v hv
      exact Finset.mem_insert_of_mem (hrs hv)
    have hle := hmax (insert z s) hrs' hT'
    have hcard := Finset.card_insert_of_notMem hz
    omega
lemma IsTree.girth_add_one_le_card_of_two_leaves_of_two_adj
    {G : SimpleGraph α} [DecidableRel G.Adj] {s : Finset α}
    (hT : (G.induce (s : Set α)).IsTree)
    {x y z a b : α}
    (hxs : x ∈ s) (hys : y ∈ s) (hxy : x ≠ y)
    (hx : G.degree x = 1) (hy : G.degree y = 1)
    (hz : z ∉ s) (ha : a ∈ s) (hb : b ∈ s)
    (hab : a ≠ b) (hza : G.Adj z a) (hzb : G.Adj z b) :
    G.girth + 1 ≤ s.card := by
  let e : G.induce (s : Set α) ↪g G := SimpleGraph.Embedding.induce _
  obtain ⟨p, hp, _⟩ := hT.existsUnique_path ⟨a, by simpa⟩ ⟨b, by simpa⟩
  let q : G.Walk a b := p.map e.toHom
  have hq : q.IsPath := by
    dsimp [q]
    exact (Walk.map_isPath_iff_of_injective e.injective).2 hp
  have hq_s : ∀ w ∈ q.support, w ∈ s := by
    intro w hw
    dsimp [q] at hw
    rw [Walk.support_map] at hw
    obtain ⟨w', hw', rfl⟩ := List.mem_map.mp hw
    exact w'.property
  have hzq : z ∉ q.support := fun hzmem => hz (hq_s z hzmem)
  let r : G.Walk a z := q.concat hzb.symm
  have hr : r.IsPath := hq.concat hzq hzb.symm
  have hclose : s(z, a) ∉ r.edges := by
    intro he
    dsimp [r] at he
    simp only [Walk.edges_concat, List.concat_eq_append, List.mem_append, List.mem_singleton] at he
    rcases he with he | he
    · exact hzq (q.fst_mem_support_of_mem_edges he)
    · simp only [Sym2.eq, Sym2.rel_iff', Prod.mk.injEq, Prod.swap_prod_mk] at he
      rcases he with ⟨hzb', haz⟩ | ⟨_, hab'⟩
      · exact hza.ne haz.symm
      · exact hab hab'
  let c : G.Walk z z := r.cons hza
  have hc : c.IsCycle := by
    dsimp [c]
    exact (Walk.cons_isCycle_iff r hza).2 ⟨hr, hclose⟩
  have hsubx : (G.neighborSet x).Subsingleton := by
    obtain ⟨nx, hnx, huniqx⟩ := degree_eq_one_iff_existsUnique_adj.mp hx
    intro u hu v hv
    exact (huniqx u hu).trans (huniqx v hv).symm
  have hsuby : (G.neighborSet y).Subsingleton := by
    obtain ⟨ny, hny, huniqy⟩ := degree_eq_one_iff_existsUnique_adj.mp hy
    intro u hu v hv
    exact (huniqy u hu).trans (huniqy v hv).symm
  have hxz : x ≠ z := fun hxz => hz (hxz ▸ hxs)
  have hyz : y ≠ z := fun hyz => hz (hyz ▸ hys)
  have hxnot : x ∉ c.support :=
    hc.isTrail.not_mem_support_of_subsingleton_neighborSet hxz hxz hsubx
  have hynot : y ∉ c.support :=
    hc.isTrail.not_mem_support_of_subsingleton_neighborSet hyz hyz hsuby
  have hqC : ∀ ⦃w : α⦄, w ∈ q.support → w ∈ c.support := by
    intro w hw
    have hwr : w ∈ r.support := by
      dsimp [r]
      exact q.support_subset_support_concat hzb.symm hw
    dsimp [c]
    exact r.support_subset_support_cons hza hwr
  have hqsub : q.support.toFinset ⊆ (s.erase x).erase y := by
    intro w hw
    have hwq : w ∈ q.support := by simpa using hw
    have hws : w ∈ s := hq_s w hwq
    have hwx : w ≠ x := by
      intro hwx
      subst w
      exact hxnot (hqC hwq)
    have hwy : w ≠ y := by
      intro hwy
      subst w
      exact hynot (hqC hwq)
    simp [hws, hwx, hwy]
  have hqcard : q.support.toFinset.card = q.length + 1 := by
    rw [List.toFinset_card_of_nodup hq.support_nodup, q.length_support]
  have hy_erase : y ∈ s.erase x := by simp [hys, hxy.symm]
  have hcard := Finset.card_le_card hqsub
  rw [hqcard, Finset.card_erase_of_mem hy_erase,
    Finset.card_erase_of_mem hxs] at hcard
  have hclen : c.length = q.length + 2 := by simp [c, r]
  have hg := G.girth_le_length hc
  omega
lemma girth_add_one_le_largestInducedTreeSize_of_two_leaves
    (G : SimpleGraph α) [DecidableRel G.Adj]
    (hG : G.Connected) (hcyc : ¬ G.IsAcyclic)
    {x y : α} (hxy : x ≠ y)
    (hx : G.degree x = 1) (hy : G.degree y = 1) :
    G.girth + 1 ≤ largestInducedTreeSize G := by
  obtain ⟨t, hxt, hyt, hTt⟩ :=
    Connected.exists_induced_tree_containing_pair hG x y
  have hr : ∃ u : Finset α,
      ({x, y} : Finset α) ⊆ u ∧ (G.induce (u : Set α)).IsTree := by
    refine ⟨t, ?_, hTt⟩
    intro v hv
    rcases Finset.mem_insert.mp hv with rfl | hv
    · exact hxt
    · have hvy : v = y := Finset.mem_singleton.mp hv
      subst v
      exact hyt
  obtain ⟨s, hrs, hT, hmax⟩ :=
    exists_maximum_induced_tree_containing G {x, y} hr
  have hxs : x ∈ s := hrs (by simp)
  have hys : y ∈ s := hrs (by simp)
  have hs : s.Nonempty := ⟨x, hxs⟩
  have hsu : s ≠ Finset.univ := by
    intro hsu
    subst s
    have hset : (↑(Finset.univ : Finset α) : Set α) = Set.univ := by
      ext v
      simp
    rw [hset] at hT
    have hTuniv : (G.induce Set.univ).IsTree := hT
    have hGtree : G.IsTree := (induceUnivIso G).isTree_iff.mp hTuniv
    exact hcyc hGtree.IsAcyclic
  obtain ⟨z, hz, a, ha, b, hb, hab, hza, hzb⟩ :=
    exists_two_adj_of_maximum_induced_tree_containing
      hG hrs hs hT hmax hsu
  have hbound : G.girth + 1 ≤ s.card :=
    IsTree.girth_add_one_le_card_of_two_leaves_of_two_adj
      hT hxs hys hxy hx hy hz ha hb hab hza hzb
  exact hbound.trans (card_le_largestInducedTreeSize hT)
end AgentTwoLeaf
